import bcrypt, jwt  
# bcrypt → 비밀번호 해싱/검증
# jwt → JSON Web Token 생성/검증
from fastapi import Depends, HTTPException  
# Depends → FastAPI 의존성 주입
# HTTPException → HTTP 에러 응답 발생시 사용
from fastapi.security import OAuth2PasswordBearer  
# OAuth2 비밀번호 기반 인증을 위한 FastAPI 보안 모듈
from sqlalchemy.orm import Session  
# DB 세션 타입 힌트용
from database import get_db  
# DB 세션 생성 함수 import
import models  
# User 모델 등 ORM 모델 import
from datetime import datetime, timedelta  
# 시간 관련 처리, 토큰 만료 시간 계산에 사용

# JWT 설정
SECRET_KEY = "YOUR_SECRET_KEY"  
# JWT 서명용 비밀 키
ALGORITHM = "HS256"  
# JWT 암호화 알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 60  
# 액세스 토큰 만료 시간(분 단위)

# OAuth2 스킴 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")  
# 로그인 URL 지정
# FastAPI가 자동으로 Authorization 헤더에서 Bearer 토큰을 추출

# 비밀번호 해싱
def hash_password(password: str) -> str:
    # bcrypt로 비밀번호 해싱
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    # encode() → 문자열을 바이트로 변환
    # gensalt() → 랜덤 솔트 생성
    # decode() → 바이트 → 문자열로 변환

# 비밀번호 검증
def verify_password(plain, hashed) -> bool:
    # 입력한 평문 비밀번호와 DB의 해시된 비밀번호 비교
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# JWT 토큰 생성
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()  
    # 원본 데이터 보호 위해 복사
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # 만료 시간 계산, 지정 없으면 기본 60분
    to_encode.update({"exp": expire})  
    # JWT payload에 만료 시간(exp) 추가
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  
    # 토큰 생성

# 현재 로그인한 사용자 조회
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        # 토큰 디코딩
        user_id = payload.get("user_id")  
        # payload에서 user_id 추출
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        # user_id 없으면 인증 실패
        user = db.query(models.User).filter(models.User.id == user_id).first()  
        # DB에서 user 조회
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user  
        # 로그인 성공 시 User 객체 반환
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        # 토큰이 잘못되거나 만료되면 인증 실패
