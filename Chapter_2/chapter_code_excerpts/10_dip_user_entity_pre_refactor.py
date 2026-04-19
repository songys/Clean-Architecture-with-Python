# ============================================================
# DIP(의존성 역전 원칙) 위반 사례 - 리팩토링 전
# 비즈니스 로직(UserEntity)이 특정 데이터베이스(MySQL)에 직접 의존
# 데이터베이스를 변경하면 비즈니스 로직도 함께 수정해야 하는 문제
# ============================================================


# DIP 위반: 고수준 모듈(비즈니스 로직)이 저수준 모듈(MySQL)을 직접 생성
# MySQL을 PostgreSQL 등으로 바꾸려면 이 클래스의 코드를 수정해야 하는 구조
class UserEntity:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.database = MySQLDatabase()  # 저수준 모듈에 대한 직접 의존성

    # 특정 데이터베이스 구현에 강하게 결합된 저장 메서드
    def save(self):
        self.database.insert("users", {"id": self.user_id})


# 저수준 모듈: 특정 데이터베이스의 구체적 구현
class MySQLDatabase:
    def insert(self, table: str, data: dict):
        print(f"MySQL의 {table} 테이블에 {data} 삽입 중")
