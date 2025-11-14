from pydantic import BaseModel, EmailStr  # 데이터 검증용 Pydantic import
from datetime import datetime  # 시간 처리

class UserCreate(BaseModel):  # 회원가입 요청용 스키마
    username: str  # 사용자명
    email: EmailStr  # 이메일, 자동 검증
    password: str  # 평문 비밀번호, DB 저장 전 hash 처리 필요

class UserResponse(BaseModel):  # 회원가입 응답용 스키마
    id: int  # 사용자 고유 ID
    username: str  # 사용자명
    email: EmailStr  # 이메일

    class Config:
        from_attributes = True  # ORM 객체 바로 반환 가능

class PostCreate(BaseModel):  # 게시글 생성 요청 스키마
    title: str  # 제목
    content: str  # 내용

class PostResponse(BaseModel):  # 게시글 응답 스키마
    id: int  # 게시글 ID
    title: str  # 제목
    content: str  # 내용
    create_date: datetime  # 작성일
    owner_id: int  # 작성자 ID

    class Config:
        from_attributes = True  # ORM 객체 바로 반환 가능

# 댓글 작성용 요청 스키마
class CommentCreate(BaseModel):
    post_id: int       # 어떤 게시글에 달리는 댓글인지
    user_id: int       # 댓글 작성자
    content: str       # 댓글 내용

# 댓글 응답용 스키마
class CommentResponse(BaseModel):
    id: int            # 댓글 ID
    post_id: int       # 게시글 ID
    user_id: int       # 작성자 ID
    content: str       # 댓글 내용
    create_date: datetime  # 작성일시

    model_config = { 
        "from_attributes": True  # ORM 객체 바로 반환 가능
    }