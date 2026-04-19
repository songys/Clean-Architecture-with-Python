# 애플리케이션 계층에서 정의하는 리포지토리 인터페이스
# - 도메인/애플리케이션 계층은 저장소의 구체적 구현을 알 필요 없음
# - 의존성 역전 원칙(DIP)의 적용: 상위 계층이 인터페이스를 정의하고 하위 계층이 구현


from abc import ABC, abstractmethod
from uuid import UUID


# 작업 영속성을 위한 추상 리포지토리 인터페이스 (포트)
class TaskRepository(ABC):

    @abstractmethod
    def get(self, task_id: UUID) -> Task:
        """ID를 기준으로 작업(Task)을 조회"""

        pass


# 인프라 계층에서 인터페이스를 구체적으로 구현 (어댑터)
# - 애플리케이션 계층의 인터페이스를 SQLite 데이터베이스로 구현하는 예시
# - 인터페이스만 준수하면 다른 저장소(PostgreSQL, MongoDB 등)로 교체 가능


class SqliteTaskRepository(TaskRepository):

    def get(self, task_id: UUID) -> Task:

        # 인터페이스의 구체적 구현 - SQLite 데이터베이스에서 작업 조회

        pass
