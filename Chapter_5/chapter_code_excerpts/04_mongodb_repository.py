# 리포지토리 인터페이스의 구체적 구현 예제 (MongoDB)
# - 애플리케이션 계층에서 정의한 TaskRepository 인터페이스를 인프라 계층에서 MongoDB로 구현
# - 의존성 역전 원칙(DIP): 유스케이스는 이 구현체가 아닌 인터페이스에만 의존

from uuid import UUID

from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import TaskNotFoundError


# MongoDB 클라이언트 스텁 (실제로는 pymongo 등의 라이브러리 사용)
class MongoClient:
    def __init__(self):
        self.task_management = None

    """mypy를 위한 스텁 클래스"""

    ...


# TaskRepository 추상 인터페이스를 MongoDB로 구현한 구체 클래스
# - 인터페이스에 정의된 get, save, delete 메서드를 MongoDB 연산으로 변환
class MongoDbTaskRepository(TaskRepository):
    """TaskRepository 인터페이스의 MongoDB 구현체"""

    def __init__(self, client: MongoClient):
        self.client = client
        # MongoDB의 데이터베이스 및 컬렉션 연결
        self.db = client.task_management
        self.tasks = self.db.tasks

    def get(self, task_id: UUID) -> Task:
        """ID로 작업 조회"""
        # MongoDB 쿼리로 문서 검색
        document = self.tasks.find_one({"_id": str(task_id)})
        if not document:
            # 도메인 예외를 발생시켜 유스케이스가 적절히 처리하도록 전달
            raise TaskNotFoundError(task_id)
        # ... 나머지 메서드 구현

    # 다른 인터페이스 메서드 구현 ...
