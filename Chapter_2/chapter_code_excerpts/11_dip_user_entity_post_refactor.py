# ============================================================
# DIP(의존성 역전 원칙) 적용 후 - 리팩토링 완료
# 추상 인터페이스(DatabaseInterface)를 도입하여 의존성 방향을 역전
# 비즈니스 로직은 추상화에만 의존하고, 구체 구현은 외부에서 주입
# 이것이 클린 아키텍처의 핵심 원리
# ============================================================

from abc import ABC, abstractmethod


# 데이터베이스 연산의 추상 인터페이스 (고수준 모듈과 저수준 모듈 사이의 계약)
# 모든 데이터베이스 구현이 이 인터페이스를 따르도록 강제
class DatabaseInterface(ABC):
    @abstractmethod
    def insert(self, table: str, data: dict):
        pass


# DIP 적용: 구체 클래스가 아닌 추상 인터페이스(DatabaseInterface)에만 의존
# 생성자를 통해 외부에서 데이터베이스 구현을 주입받는 구조 (의존성 주입)
class UserEntity:
    def __init__(self, user_id: str, database: DatabaseInterface):
        self.user_id = user_id
        self.database = database  # 추상 타입으로 선언 - 어떤 DB 구현이든 주입 가능

    def save(self):
        self.database.insert("users", {"id": self.user_id})


# DatabaseInterface를 구현한 MySQL 전용 클래스
class MySQLDatabase(DatabaseInterface):
    def insert(self, table: str, data: dict):
        print(f"MySQL의 {table} 테이블에 {data} 삽입 중")


# DatabaseInterface를 구현한 PostgreSQL 전용 클래스
# 새 데이터베이스 추가 시 UserEntity 코드 수정 불필요 (OCP도 함께 준수)
class PostgreSQLDatabase(DatabaseInterface):
    def insert(self, table: str, data: dict):
        print(f"PostgreSQL의 {table} 테이블에 {data} 삽입 중")


# 사용법 - 원하는 데이터베이스 구현을 자유롭게 주입
mysql_db = MySQLDatabase()
user = UserEntity("123", mysql_db)
user.save()
postgres_db = PostgreSQLDatabase()
another_user = UserEntity("456", postgres_db)
another_user.save()


# 테스트용 모의(Mock) 데이터베이스 - DIP 덕분에 테스트 용이성 확보
# 실제 DB 없이도 비즈니스 로직을 검증할 수 있는 가짜 구현
class MockDatabase(DatabaseInterface):
    def __init__(self):
        self.inserted_data = []  # 삽입된 데이터를 메모리에 기록하는 리스트

    def insert(self, table: str, data: dict):
        self.inserted_data.append((table, data))


# 테스트에서 - MockDatabase를 주입하여 DB 연결 없이 동작 검증
mock_db = MockDatabase()
user = UserEntity("test_user", mock_db)
user.save()
assert mock_db.inserted_data == [("users", {"id": "test_user"})]
