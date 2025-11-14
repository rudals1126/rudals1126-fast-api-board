# 회원가입 내역 보기
# C:\Users\rudal>cd C:\pro
# DB에 생성된 테이블
# C:\pro>python check_users.py

import sys
# 파이썬 시스템 모듈 import
# sys.path를 통해 모듈 검색 경로를 추가할 수 있음

sys.path.append(r"C:\Users\rudal\OneDrive\바탕 화면\por")
# 프로젝트 폴더를 모듈 검색 경로에 추가

from fastapi import FastAPI
# FastAPI 프레임워크의 핵심 클래스 import

from app.api.users import router as users_router
# users.py에서 router를 가져와 이름을 users_router로 변경
from app.api.posts import router as posts_router
# posts.py에서 게시글 router 가져와 이름을 posts_router로 변경
from app.api.comments import router as comments_router
# comments.py에서 댓글 router 가져와 이름을 comments_router로 변경
from app.database import Base, engine # 모든 ORM 모델 테이블을 DB에 생성

from app.database.models import User, PostModel, Comment, LoginHistory  # ORM 모델(User, Post, Comment, LoginHistory) 임포트
from loge_excel import init_excel, register_user, save_login_history, add_comment

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

from fastapi import Form

init_excel()

Base.metadata.create_all(bind=engine)  # DB에 등록된 모든 ORM 모델의 테이블 생성


# FastAPI 앱 생성
app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/posts")
def posts_page(request: Request):
    return templates.TemplateResponse("post.html", {"request": request})

@app.get("/find-id")
def find_id_page(request: Request):
    return templates.TemplateResponse("find_id.html", {"request": request})

@app.get("/reset-password")
def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@app.get("/change-password")
def change_password_page(request: Request):
    return templates.TemplateResponse("change_password.html", {"request": request})


# 라우터 등록 
app.include_router(users_router)      # 사용자 관련 API
app.include_router(posts_router)      # 게시글 관련 API
app.include_router(comments_router)   # 댓글 관련 API
app.include_router(users_router)      # 계정삭제 API   
# 루트 경로 API
@app.get("/")
def root():
    # "/" 경로로 GET 요청 들어오면 실행
    return {"message": "환영합니다 블로그입니다"}

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    # uvicorn은 FastAPI 실행용 ASGI 서버
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # main.py의 app 객체 실행
    # host="0.0.0.0" → 외부 접속 가능
    # port=8000 → 서버 포트
    # reload=True → 코드 변경 시 자동 재시작
