from fastapi import APIRouter, Depends, HTTPException  # FastAPI 라우터, 의존성 주입, HTTP 예외 처리
from sqlalchemy.orm import Session  # DB 세션 타입 힌트
import models, schemas, utils  # ORM 모델, Pydantic 스키마, 유틸 함수
from database import get_db  # DB 세션 생성 함수
from datetime import timedelta, datetime  # 토큰 만료 계산, 로그인 시간 기록
from loge_excel import register_user, save_login_history, delete_user_safe # 엑셀 기록용 함수 import
from fastapi import APIRouter, Depends, HTTPException, Form

# /users API 그룹 생성, Swagger UI에서 tags 지정
router = APIRouter(prefix="/users", tags=["users"])

# ---------------------------
# 1. 회원가입 API
# ---------------------------
@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    새로운 사용자 등록
    1. 이메일 중복 확인
    2. 비밀번호 해시 후 DB 저장
    3. 엑셀 Users 시트에도 자동 기록
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")  # 이미 등록된 이메일
    
    hashed_pw = utils.hash_password(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 엑셀에도 자동 저장
    register_user(user.username, user.email, user.password)

    return new_user

# ---------------------------
# 2. 로그인 API
# ---------------------------
@router.post("/login")
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not utils.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # DB 로그인 기록
    login_record = models.LoginHistory(user_id=user.id, login_time=datetime.utcnow())
    db.add(login_record)
    db.commit()

    # 엑셀에도 자동 저장
    save_login_history(user.id)

    access_token_expires = timedelta(minutes=60)
    token = utils.create_access_token(data={"user_id": user.id}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}


# 3. 안전한 계정 삭제 API
@router.delete("/delete-account") # HTTP DELETE 메소드를 처리하는 '/delete-account' 엔드포인트를 정의-
def remove_user_safe(username: str, email: str, password: str): # API 함수 정의: 삭제를 위해 username, email, password를 입력받는다
    try: # 예외 처리 시작: 계정 삭제 과정에서 발생할 수 있는 오류를 잡기 위함
        delete_user_safe(username, email, password) # 실제 계정 삭제 로직을 수행하는 내부 함수를 호출한다
        return {"message": f"계정 삭제 완료: {username}"} # 삭제 성공 시, 완료 메시지를 응답으로 반환한다
    except ValueError as ve: # 'delete_user_safe' 함수 내에서 잘못된 값(예: 사용자 정보 불일치)으로 인해 발생한 ValueError를 잡는다
        raise HTTPException(status_code=400, detail=str(ve)) # 400 Bad Request와 함께, ValueError의 내용을 사용자에게 반환한다
    except Exception as e: # 그 외 예상치 못한 모든 종류의 오류(Exception)를 잡는다
        raise HTTPException(status_code=500, detail=f"삭제 중 오류 발생: {str(e)}") # 500 Internal Server Error와 함께 오류 내용을 반환한다

# ---------------------------
# 4. 아이디 찾기 API
# ---------------------------
@router.post("/find-id")
def find_id(username: str, email: str, db: Session = Depends(get_db)):
    """
    이름 + 이메일로 사용자 아이디 조회
    """
    user = db.query(models.User).filter(models.User.username == username, models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user.username, "email": user.email}

# ---------------------------
# 5. 비밀번호 찾기 / 임시 비밀번호 발급
# ---------------------------
@router.post("/reset-password")
def reset_password(username: str, email: str, db: Session = Depends(get_db)):
    """
    이름 + 이메일 확인 후 임시 비밀번호 발급
    1. DB 사용자 조회
    2. 임시 비밀번호 생성 후 DB 해시 업데이트
    3. 임시 비밀번호 반환
    """
    user = db.query(models.User).filter(models.User.username == username, models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    import secrets
    temp_password = secrets.token_urlsafe(8)  # 8자리 임시 비밀번호
    user.hashed_password = utils.hash_password(temp_password)
    db.commit()
    return {"message": "임시 비밀번호 발급 완료", "temp_password": temp_password}

# ---------------------------
# 6. 비밀번호 변경 API
# ---------------------------
@router.post("/change-password")
def change_password(username: str, old_password: str, new_password: str, db: Session = Depends(get_db)):
    """
    사용자 비밀번호 변경
    1. 사용자 존재 확인
    2. 기존 비밀번호 확인
    3. 새 비밀번호 해시 DB 반영
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not utils.verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    user.hashed_password = utils.hash_password(new_password)
    db.commit()
    return {"message": "비밀번호가 성공적으로 변경되었습니다."}

# 7. HTML 폼 회원가입 처리 (templates/signup.html용)
from fastapi import Form
from fastapi.responses import RedirectResponse

@router.post("/register")
def register_user_form(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    hashed_pw = utils.hash_password(password)
    new_user = models.User(username=username, email=email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()

    # 엑셀 기록
    register_user(username, email, password)

    # 회원가입 완료 후 메인 페이지로 이동
    return RedirectResponse(url="/", status_code=303)


from fastapi import Form

@router.post("/find-id")
def find_id(username: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    # 기존 로직 그대로
    ...

@router.post("/reset-password")
def reset_password(username: str = Form(...), email: str = Form(...), db: Session = Depends(get_db)):
    # 기존 로직 그대로
    ...
