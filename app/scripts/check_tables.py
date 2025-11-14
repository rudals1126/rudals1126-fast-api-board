from database import engine, Base  
# database.py 파일에서 engine(데이터베이스 연결 객체)과 Base(ORM 모델의 기반 클래스)를 가져온다
# 여기서는 engine과 Base를 직접 사용하지는 않지만,
# 일반적으로 SQLAlchemy ORM 환경에서는 이 두 개가 DB 연결과 테이블 생성을 담당함
import sqlite3  
# 파이썬 내장 모듈 sqlite3를 불러온다
# SQLite 데이터베이스 파일(myapi.db)에 직접 접근해서 SQL 문을 실행할 수 있게 해줌

# SQLite 데이터베이스 연결
conn = sqlite3.connect("myapi.db")  
# 'myapi.db' 파일을 열어서 데이터베이스에 연결
# 만약 파일이 없으면 새로운 DB 파일을 자동으로 생성함

cursor = conn.cursor()  
# SQL 명령어를 실행할 수 있는 커서(Cursor) 객체를 생성
# 커서를 이용해서 DB 내 테이블 목록, 데이터 조회 등을 수행할 수 있음

# 데이터베이스 안의 모든 테이블 이름 조회
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")  
# SQLite 내부의 sqlite_master 테이블은 DB 구조 정보를 저장함
# 그중에서 type이 'table'인 항목을 조회해서 모든 테이블 이름을 가져옴

tables = cursor.fetchall()  
# 실행 결과를 모두 가져옴 → 리스트 형태로 반환
# 예: [('users',), ('posts',)] 이런 식으로 저장됨


# 테이블 목록 출력
print("현재 DB에 생성된 테이블 목록:")  
# 사용자에게 결과를 보기 쉽게 제목 출력

for table in tables:  
    print("-", table[0])  
    # 테이블 이름만 꺼내서 보기 쉽게 출력
    # 예: - users
    #     - posts


# 데이터베이스 연결 종료
conn.close()  
# DB 연결을 닫아서 리소스 낭비 방지
# (항상 작업이 끝나면 close()로 닫는 것이 좋음)
