from database import Base, engine  
# database.py 파일에서 Base와 engine을 가져온다
# Base: 모든 모델 클래스(User, Post 등)의 기반 클래스 (SQLAlchemy에서 제공)
# engine: DB와의 실제 연결 객체 (SQLite, MySQL 등)

import models  
# models.py에서 정의한 User, PostModel 등 ORM(데이터베이스 테이블과 매핑된 클래스)을 불러옴 
# Base.metadata는 이 models 안에 정의된 테이블 구조 정보를 알고 있음

# 데이터베이스 및 테이블 생성
Base.metadata.create_all(bind=engine)
# Base.metadata.create_all() → Base를 상속받은 모든 클래스의 테이블을 실제 DB에 생성
# bind=engine → 어떤 데이터베이스에 연결할지 지정 (여기서는 database.py에서 만든 SQLite 엔진 사용)
# 예를 들어 models.py에 User, PostModel이 있다면 users, posts 테이블이 생성됨

print("DB 및 테이블 생성 완료!")
# 프로그램이 실행되면 콘솔에 이 문구가 표시됨
