# === 인메모리/파일 리포지토리 구현 ===
# 동일한 리포지토리 인터페이스(포트)에 대해 두 가지 구현체 제공
# 클린 아키텍처의 핵심: 저장소 교체 시 비즈니스 로직 변경 불필요

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict
from uuid import UUID


# 애플리케이션 계층에서 정의한 리포지토리 포트(인터페이스)
class TaskRepository(ABC):
    """Task 엔터티 저장을 위한 리포지토리 인터페이스 — 영속성 세부 구현과 무관한 계약"""

    @abstractmethod
    def get(self, task_id: UUID) -> Task:
        """ID로 작업을 조회"""
        pass

    @abstractmethod
    def save(self, task: Task) -> None:
        """작업을 리포지토리에 저장"""
        pass

    # ... 나머지 인터페이스 메서드


# --- 구현체 1: 인메모리 저장소 ---
class InMemoryTaskRepository(TaskRepository):
    """TaskRepository의 인메모리 구현 — 테스트 및 개발 환경에 적합한 경량 저장소"""

    def __init__(self) -> None:
        # 딕셔너리 기반의 메모리 내 저장소
        self._tasks: Dict[UUID, Task] = {}

    def get(self, task_id: UUID) -> Task:
        """ID로 작업 조회 — 월리스 연산자(:=)를 활용한 간결한 조회"""
        if task := self._tasks.get(task_id):
            return task
        raise TaskNotFoundError(task_id)

    def save(self, task: Task) -> None:
        """작업 저장 — 딕셔너리에 직접 할당"""
        self._tasks[task.id] = task

    # 추가 인터페이스 메서드 구현


# --- 구현체 2: JSON 파일 저장소 ---
class FileTaskRepository(TaskRepository):
    """TaskRepository의 JSON 파일 기반 구현 — 데이터를 파일 시스템에 영속화"""

    def __init__(self, data_dir: Path):
        # 데이터 디렉터리 내 tasks.json 파일에 저장
        self.tasks_file = data_dir / "tasks.json"
        self._ensure_file_exists()

    def get(self, task_id: UUID) -> Task:
        """ID로 작업 조회 — JSON 파일에서 읽어와 도메인 객체로 변환"""
        tasks = self._load_tasks()
        for task_data in tasks:
            if UUID(task_data["id"]) == task_id:
                return self._dict_to_task(task_data)
        raise TaskNotFoundError(task_id)

    def save(self, task: Task) -> None:
        """작업 저장 — 도메인 객체를 딕셔너리로 변환 후 JSON 파일에 기록"""
        # ... 나머지 구현


# 리포지토리 다형성 시연 — 어떤 구현체든 동일한 인터페이스로 작동
task = repository.get(task_id)
task.complete()
repository.save(task)
