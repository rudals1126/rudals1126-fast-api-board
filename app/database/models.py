from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey  # DB 컬럼, 타입, 외래키 import
from sqlalchemy.orm import relationship  # 테이블 간 ORM 관계 설정
from database import Base  # ORM Base 클래스 import
from datetime import datetime  # 시간/날짜 처리용

# 사용자 테이블
class User(Base):
    __tablename__ = "users"  # 테이블 이름
    id = Column(Integer, primary_key=True, index=True)  # PK, 인덱스
    username = Column(String, unique=True, index=True, nullable=False)  # 사용자명, 유니크, 인덱스, 필수
    email = Column(String, unique=True, index=True, nullable=False)  # 이메일, 유니크, 인덱스, 필수
    hashed_password = Column(String, nullable=False)  # 암호화된 비밀번호
    created_at = Column(DateTime, default=datetime.utcnow)  # 생성시간, 기본값 현재

    # 관계 설정
    posts = relationship("PostModel", back_populates="owner")  # 게시글과 1:N 관계
    comments = relationship("Comment", back_populates="user")  # 댓글과 1:N 관계
    logins = relationship("LoginHistory", back_populates="user")  # 로그인 기록과 1:N 관계

# 로그인 기록 테이블
class LoginHistory(Base):
    __tablename__ = "login_history"  # DB 테이블 이름
    id = Column(Integer, primary_key=True, index=True)  # 로그인 기록 고유 ID, 기본키, 인덱스
    user_id = Column(Integer, ForeignKey("users.id"))  # 어느 사용자가 로그인했는지 연결 (users.id 참조)
    login_time = Column(DateTime, default=datetime.utcnow)  # 로그인 시간 기록, 기본값 현재 UTC

    user = relationship("User", back_populates="logins")  
    # User 모델과 양방향 관계 설정

# 게시글 테이블
class PostModel(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)  # PK, 인덱스
    title = Column(String, nullable=False)  # 제목
    content = Column(Text, nullable=False)  # 내용
    create_date = Column(DateTime, nullable=False, default=datetime.utcnow)  # 작성일
    owner_id = Column(Integer, ForeignKey("users.id"))  # 작성자 외래키

    # 관계 설정
    owner = relationship("User", back_populates="posts")  # Post.owner → User 접근 가능
    comments = relationship("Comment", back_populates="post")  # 게시글-댓글 1:N 관계

# 댓글 테이블
class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)  # 댓글 내용
    create_date = Column(DateTime, nullable=False, default=datetime.utcnow)  # 작성일
    post_id = Column(Integer, ForeignKey("posts.id"))  # 어떤 게시글에 달린 댓글인지
    user_id = Column(Integer, ForeignKey("users.id"))  # 누가 쓴 댓글인지

    # 관계 설정
    post = relationship("PostModel", back_populates="comments")  # Comment → PostModel 접근
    user = relationship("User", back_populates="comments")  # Comment → User 접근

# 질문 테이블
class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)  # 질문 제목
    content = Column(Text, nullable=False)  # 질문 내용
    create_date = Column(DateTime, nullable=False)  # 작성일

    # 답변과 1:N 관계
    answers = relationship("Answer", back_populates="question")

# 답변 테이블
class Answer(Base):
    __tablename__ = "answer"
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)  # 답변 내용
    create_date = Column(DateTime, nullable=False)  # 작성일
    question_id = Column(Integer, ForeignKey("question.id"))  # 어떤 질문에 속하는지

    question = relationship("Question", back_populates="answers")  # ORM 관계
