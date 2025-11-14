from sqlalchemy import create_engine  
# SQLAlchemy의 create_engine 함수를 불러옴
# DB와 연결할 엔진 객체를 만드는 함수

from sqlalchemy.ext.declarative import declarative_base  
# ORM 모델(Base)을 정의할 때 상속받는 Base 클래스를 만드는 함수

from sqlalchemy.orm import sessionmaker  
# DB와 실제로 데이터를 주고받을 세션(Session) 객체를 만드는 함수

from sqlalchemy.orm import Session  
# Session 타입 힌트를 위해 import
# 함수의 반환 타입이나 변수 타입 표기에 사용

# SQLite 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./myapi.db"  
# 현재 폴더에 myapi.db라는 SQLite 파일 생성
# "sqlite:///" → SQLite 파일 경로 지정
# "./myapi.db" → 현재 폴더에 생성

# 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # DB 연결 정보
    connect_args={"check_same_thread": False}  
    # SQLite에서는 기본적으로 같은 스레드에서만 DB 접근 가능
    # 여러 스레드에서 안전하게 접근하도록 설정
)

# DB와 실제로 대화할 세션 생성
SessionLocal = sessionmaker(
    autocommit=False,  # False → 커밋을 수동으로 해야 함
    autoflush=False,   # False → 변경 내용을 자동으로 DB에 반영하지 않음
    bind=engine        # 어떤 DB 엔진과 연결할지 지정
)

# ORM 모델들이 상속할 Base 클래스 생성
Base = declarative_base()
# 이후 ORM 모델을 만들 때 class User(Base): ... 처럼 상속

# FastAPI 의존성 주입용 DB 세션 함수
def get_db():
    """DB 세션을 생성하고 사용 후 반드시 닫아주는 의존성 함수"""
    db: Session = SessionLocal()  # DB 세션 생성
    try:
        yield db  # 세션 사용
        # FastAPI에서 yield를 쓰면 이 함수가 의존성 주입으로 활용 가능
    finally:
        db.close()  # 세션 종료 시 반드시 닫아줌
