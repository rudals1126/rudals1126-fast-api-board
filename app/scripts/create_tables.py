from database import Base, engine
import models

# 데이터베이스 및 테이블 생성
Base.metadata.create_all(bind=engine)

print("DB 및 테이블 생성 완료!")
