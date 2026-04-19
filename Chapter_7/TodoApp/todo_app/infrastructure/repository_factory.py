"""
구성에 따라 리포지토리를 생성하는 팩토리 함수.

인프라스트럭처 계층의 팩토리 패턴:
환경 변수(Config)에 따라 메모리 또는 파일 기반 리포지토리 구현체를 선택하고,
프로젝트-작업 리포지토리 간 참조를 설정하여 반환.
"""

from pathlib import Path
from typing import Tuple

from todo_app.application.repositories.project_repository import ProjectRepository
from todo_app.application.repositories.task_repository import TaskRepository
from todo_app.infrastructure.persistence.memory import (
    InMemoryTaskRepository,
    InMemoryProjectRepository,
)
from todo_app.infrastructure.persistence.file import (
    FileTaskRepository,
    FileProjectRepository,
)
from todo_app.infrastructure.config import Config, RepositoryType


def create_repositories() -> Tuple[TaskRepository, ProjectRepository]:
    """
    리포지토리 팩토리 함수 — Config 설정에 따라 적절한 구현체를 생성하고 연결.

    Returns:
        (TaskRepository, ProjectRepository) 튜플
    """
    repo_type = Config.get_repository_type()

    if repo_type == RepositoryType.FILE:
        # 파일 기반 영속성 — JSON 파일에 데이터 저장
        data_dir = Config.get_data_directory()
        task_repo = FileTaskRepository(data_dir)
        project_repo = FileProjectRepository(data_dir)
        # 프로젝트 리포지토리에 작업 리포지토리 참조 설정 (작업 로딩용)
        project_repo.set_task_repository(task_repo)
        return task_repo, project_repo
    elif repo_type == RepositoryType.MEMORY:
        # 인메모리 저장소 — 빠르고 가벼운 개발/테스트 환경용
        task_repo = InMemoryTaskRepository()
        project_repo = InMemoryProjectRepository()
        # 리포지토리 간 참조 연결
        project_repo.set_task_repository(task_repo)
        return task_repo, project_repo
    else:
        raise ValueError(f"잘못된 리포지토리 타입: {repo_type}")
