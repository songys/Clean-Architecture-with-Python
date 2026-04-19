# 의존성 역전 원칙(DIP)을 통한 외부 의존성 처리 - 올바른 아키텍처 예시

# ============================================================
# 도메인 계층: 추상 리포지토리 인터페이스 정의
# (예: todo_app/domain/repositories/task_repository.py)
# ============================================================
from abc import ABC, abstractmethod

from todo_app.domain.entities.task import Task


# 추상 리포지토리: 도메인 계층에 속하는 인터페이스(계약)
# 구체적인 저장 방식(DB, 파일 등)은 알지 못함
class TaskRepository(ABC):
    @abstractmethod
    def save(self, task: Task):
        pass

    @abstractmethod
    def get(self, task_id: str) -> Task:
        pass


# ============================================================
# 도메인 계층: 도메인 서비스 - 추상 리포지토리에만 의존
# (예: todo_app/domain/services/task_service.py)
# ============================================================
class TaskService:
    # 생성자 주입(Constructor Injection): 추상 인터페이스를 통해 의존성 주입
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    # 작업 생성 유스케이스 - Task 엔티티 생성 후 리포지토리에 저장
    def create_task(self, title: str, description: str) -> Task:
        task = Task(title, description)
        self.task_repository.save(task)
        return task

    # 작업 완료 유스케이스 - 조회 → 상태 변경 → 저장
    def mark_task_as_complete(self, task_id: str) -> Task:
        task = self.task_repository.get(task_id)
        task.complete()
        self.task_repository.save(task)
        return task


# ============================================================
# 외부(인프라) 계층: 추상 리포지토리의 구체 구현
# (예: todo_app/infrastructure/persistence/sqlite_task_repository.py)
# ============================================================
class SQLiteTaskRepository(TaskRepository):
    # SQLite 데이터베이스를 사용하는 구체적인 저장소 구현
    def __init__(self, db_connection):
        self.db = db_connection

    def save(self, task: Task):
        # 구현 세부 사항...
        pass

    def get(self, task_id: str) -> Task:
        # 구현 세부 사항...
        pass
