# FastAPI에서 라우터, 의존성 주입, HTTP 예외 처리 기능 import
from fastapi import APIRouter, Depends, HTTPException
# SQLAlchemy 세션(Session) 사용
from sqlalchemy.orm import Session
# DB 세션 가져오기 (get_db 함수)
from database import get_db
# Comment 모델 가져오기 (ORM 클래스)
from models import Comment
# 댓글 요청/응답 스키마 가져오기
from schemas import CommentCreate, CommentResponse
# 댓글 생성/수정 시간 기록용 datetime
from datetime import datetime
from loge_excel import add_comment as excel_add_comment
 # 엑셀 기록용 함수 import

# 댓글 관련 API 라우터 생성
# prefix="/comments" → 모든 경로 앞에 /comments가 붙음
# tags=["comments"] → Swagger 문서에서 'comments' 카테고리로 묶임
router = APIRouter(prefix="/comments", tags=["comments"])

# 댓글 작성 API
@router.post("/", response_model=CommentResponse)  # POST 요청, 응답 모델 CommentResponse 사용
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    #클라이언트가 보내는 댓글 데이터를 받아 DB에 저장 후CommentResponse 형태로 반환

    # 댓글 ORM 객체 생성 (DB에 들어갈 데이터 준비)
    db_comment = Comment(
        post_id=comment.post_id,          # 댓글이 달릴 게시글 ID
        user_id=comment.user_id,          # 댓글 작성자 ID
        content=comment.content,          # 댓글 내용
        create_date=datetime.utcnow()     # 댓글 생성 시각 기록
    )
    db.add(db_comment)      # DB 세션에 추가 (아직 DB에 반영 전)
    db.commit()             # DB에 실제로 저장(commit)
    db.refresh(db_comment)  # 새로 저장된 객체 갱신 (DB 반영 값 가져오기)
    excel_add_comment(comment.post_id, comment.user_id, comment.content) # 엑셀자동저장
    return db_comment       # 클라이언트에게 CommentResponse 형태로 반환
    
# 특정 게시글 댓글 조회 API
@router.get("/{post_id}", response_model=list[CommentResponse])  # GET 요청, 댓글 리스트 반환
def read_comments(post_id: int, db: Session = Depends(get_db)):
    # 특정 게시글(post_id)에 달린 모든 댓글 조회

    # DB에서 post_id가 일치하는 모든 댓글 조회
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    # 댓글이 없으면 HTTP 404 예외 발생
    if not comments:
        raise HTTPException(status_code=404, detail="댓글이 없습니다.")
    # 조회된 댓글 리스트 반환
    return comments

# 댓글 수정 API
@router.put("/{comment_id}", response_model=CommentResponse)  # PUT 요청, 수정된 댓글 반환
def update_comment(comment_id: int, content: str, db: Session = Depends(get_db)):
    """
    comment_id에 해당하는 댓글의 내용을 수정
    """
    # DB에서 해당 댓글 조회
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:  # 댓글이 없으면 404 예외 발생
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    
    comment.content = content            # 댓글 내용 수정
    comment.create_date = datetime.utcnow()  # 수정 시각 갱신
    db.commit()                          # DB에 반영
    db.refresh(comment)                  # 수정된 객체 새로고침
    return comment                       # 클라이언트에게 반환

# 댓글 삭제 API
@router.delete("/{comment_id}")  # DELETE 요청
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """
    comment_id에 해당하는 댓글 삭제
    """
    # DB에서 댓글 조회
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:  # 댓글이 없으면 404 예외 발생
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    
    db.delete(comment)  # DB에서 삭제
    db.commit()         # 삭제 반영
    return {"message": "댓글이 삭제되었습니다."}  # 성공 메시지 반환
