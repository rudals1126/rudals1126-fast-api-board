from sqlalchemy.orm import Session  
# SQLAlchemy에서 DB와 통신하기 위해 사용하는 Session 클래스를 불러온디
# DB와 실제로 데이터를 주고받는 세션 객체를 생성할 때 타입 힌트로 사용 가능
from database import SessionLocal  
# 'database.py'에서 정의한 SessionLocal 함수를 가져온다
# SessionLocal()을 호출하면 실제 DB 세션 객체를 생성할 수 있음
import models  
# 'models.py'에 정의된 ORM 클래스(User, PostModel 등)를 가죠옴
# User 클래스는 users 테이블과 매핑되어 있음


# DB 세션 생성
db: Session = SessionLocal()  
# SessionLocal()을 호출해 DB와 연결된 세션 객체를 생성하고 db 변수에 저장
# 이후 이 세션을 이용해 DB에 쿼리를 보내고 결과를 받을 수 있음

# 모든 사용자 조회
users = db.query(models.User).all()  
# DB 세션(db)을 이용해 User 테이블(users) 전체 데이터를 조회
# .all() → 조회 결과를 리스트로 반환
# 이제 users 변수는 User 객체들의 리스트가 됨

# 사용자 정보 출력
for user in users:
    print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Hashed Password: {user.hashed_password}, Created At: {user.created_at}")
    # 리스트에 있는 각 User 객체에 대해 아래 정보 출력:
    # - ID: DB에 저장된 사용자 고유 번호
    # - Username: 회원가입 시 설정한 사용자 이름
    # - Email: 회원가입 시 설정한 이메일
    # - Hashed Password: DB에 암호화되어 저장된 비밀번호
    # - Created At: 회원가입 시각 (UTC 기준)

# DB 세션 종료
db.close()  
# DB 세션을 종료하고 연결을 닫음
# 세션을 닫지 않으면 DB 연결이 계속 유지되어 리소스를 낭비할 수 있음
