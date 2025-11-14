from fastapi import APIRouter, Depends, HTTPException
# FastAPI에서 API 경로 그룹화, 의존성 주입, 에러 처리에 필요한 클래스와 함수들을 불러온다
from sqlalchemy.orm import Session
# SQLAlchemy의 ORM 기능 중 데이터베이스와의 통신 및 쿼리 실행을 담당하는 Session 클래스를 불러온다
from database import get_db
# 데이터베이스 연결 및 세션을 생성하고 관리하는 함수를 'database.py' 파일에서 불러온다
import models, schemas
# 데이터베이스 테이블 구조(ORM 모델)가 정의된 'models.py'와 데이터 검증/직렬화 스키마(Pydantic)가 정의된 'schemas.py' 모듈을 불러옵니다
from datetime import datetime
# 게시글 작성일 등 시간 정보를 기록하기 위해 파이썬 내장 datetime 모듈을 불러온다

# /posts 경로로 시작하는 API들을 묶어서 관리할 수 있는 라우터 객체를 생성한다
router = APIRouter(prefix="/posts", tags=["posts"])

# 1. 게시글 생성 (Create)
@router.post("/", response_model=schemas.PostResponse)
# HTTP POST 요청이 기본 경로로 들어왔을 때 이 함수를 실행하도록 지정하며, 응답 데이터를 PostResponse 스키마로 검증하고 반환하도록 설정한다
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # 게시글 생성 함수를 정의한다
    # 클라이언트 요청 데이터, DB 세션(get_db를 통해 주입)을 매개변수로 받는다.
    new_post = models.PostModel(
    # 데이터베이스 모델 객체를 새로 생성하여 'new_post' 변수에 저장
        title=post.title,
    # 클라이언트가 보낸 요청 데이터(post)의 title 값을 새 게시글 객체의 title 필드에 설정
        content=post.content,
    # 클라이언트가 보낸 요청 데이터(post)의 content 값을 새 게시글 객체의 content 필드에 설정
        owner_id= 1,
    # 현재 로그인 기능이 없으므로, 작성자(owner) ID를 임시로 1로 지정
        create_date=datetime.utcnow()
    # 게시글 작성 시간을 현재 UTC(협정 세계시) 기준으로 설정
    )
    db.add(new_post)
    # 생성된 새 게시글 객체(new_post)를 SQLAlchemy 세션에 추가하여 DB에 저장할 준비
    db.commit()
    # 세션에 추가된 변경 사항을 실제 데이터베이스에 영구적으로 저장
    db.refresh(new_post)
    # DB에 저장된 후 자동 생성된 정보를 포함하여 'new_post' 객체를 최신 상태로 갱신
    return new_post
    # 최종적으로 저장 및 갱신된 게시글 객체를 클라이언트에게 응답으로 반환한다

# 2. 게시글 전체 조회 (Read All)
@router.get("/", response_model=list[schemas.PostResponse])
# HTTP GET 요청이 기본 경로(/posts)로 들어왔을 때 이 함수를 실행하도록 지정하며, 응답 데이터를 PostResponse 객체의 리스트로 반환하도록 설정한다
def get_posts(db: Session = Depends(get_db)):
    # 게시글 전체 조회 함수를 정의합니다.
    posts = db.query(models.PostModel).all()
    # DB 세션(db)을 이용해 PostModel 테이블의 모든 레코드(게시글)를 조회하여 리스트 형태로 저장
    return posts
    # 조회된 모든 게시글을 담은 리스트를 응답으로 반환합니다.

# 3. 게시글 단일 조회 (Read One)
@router.get("/{post_id}", response_model=schemas.PostResponse)
# HTTP GET 요청이 '/posts/숫자' 형식으로 들어왔을 때 이 함수를 실행하며, {post_id}는 URL 경로에서 게시글 ID를 추출한다
def get_post(post_id: int, db: Session = Depends(get_db)):
    # 특정 게시글 단일 조회 함수를 정의합니다.
    post = db.query(models.PostModel).filter(models.PostModel.id == post_id).first()
    # DB에서 PostModel 테이블을 쿼리하여 id가 post_id와 일치하는 레코드 조회
    
    if not post:
    # 해당 ID의 게시글이 데이터베이스에 존재하지 않는다면:
        raise HTTPException(status_code=404, detail="Post not found")
    # HTTP 404 상태 코드(Not Found)와 함께 에러 메시지를 클라이언트에게 반환한다
    return post
    # 게시글이 존재한다면, 조회된 PostModel 객체를 응답으로 반환한다

# 4. 게시글 수정 (Update)
@router.put("/{post_id}", response_model=schemas.PostResponse)
# HTTP PUT 요청이 "/posts/{post_id}" 경로로 들어오면 이 함수를 실행
def update_post(post_id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
    # 특정 게시글을 수정하는 API를 정의
    
    # 1. DB에서 수정할 게시글 조회
    post = db.query(models.PostModel).filter(models.PostModel.id == post_id).first()
    
    if not post:
    # 게시글이 존재하지 않으면 예외 발생
        raise HTTPException(status_code=404, detail="Post not found")
    # HTTP 404 상태 코드와 메시지 반환
    
    # 2. 게시글 내용 수정
    post.title = updated_post.title
    # 전달받은 데이터에서 title을 가져와 DB 객체에 덮어쓰기
    post.content = updated_post.content
    # 전달받은 데이터에서 content를 가져와 DB 객체에 덮어쓰기
    
    # 3. DB에 변경 사항 반영
    db.commit() # 세션에 있는 변경사항을 실제 DB에 저장
    db.refresh(post) # 수정된 객체를 최신 상태로 갱신
    
    # 4. 수정된 게시글 반환
    return post # 클라이언트에게 수정된 게시글 정보 전달

# 5. 게시글 삭제 (Delete)
@router.delete("/{post_id}")
# HTTP DELETE 요청이 "/posts/{post_id}" 경로로 들어오면 이 함수를 실행
def delete_post(post_id: int, db: Session = Depends(get_db)):
    # 특정 게시글을 삭제하는 API를 정의
    
    # 1. DB에서 삭제할 게시글 조회
    post = db.query(models.PostModel).filter(models.PostModel.id == post_id).first()
    
    if not post:
    # 게시글이 존재하지 않으면 예외 발생
        raise HTTPException(status_code=404, detail="Post not found")
    # HTTP 404 상태 코드와 메시지 반환
    
    # 2. 게시글 삭제
    db.delete(post) # DB 세션에서 해당 게시글 삭제
    db.commit() # 실제 DB에 삭제 반영
    
    # 3. 삭제 완료 메시지 반환
    return {"message": f"게시글 {post_id}번이 삭제되었습니다."}
    # 클라이언트에게 삭제 완료 메시지를 JSON 형태로 전달

# 시간 출력 예시
print(datetime.now()) # 로컬 시간
print(datetime.utcnow()) # UTC 시간