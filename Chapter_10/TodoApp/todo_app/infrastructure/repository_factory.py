"""
설정에 따라 리포지토리를 생성하는 팩토리 함수.
- 환경 변수(TODO_REPOSITORY_TYPE)에 따라 메모리 또는 파일 리포지토리 선택
- 리포지토리 구현을 교체해도 상위 계층 코드 변경 불필요 (개방-폐쇄 원칙)
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
    설정에 따라 적절한 리포지토리 구현을 생성하고 구성한다.

    Returns:
        (TaskRepository, ProjectRepository) 튜플
    """
    repo_type = Config.get_repository_type()

    if repo_type == RepositoryType.FILE:
        data_dir = Config.get_data_directory()
        task_repo = FileTaskRepository(data_dir)
        project_repo = FileProjectRepository(data_dir)
        project_repo.set_task_repository(task_repo)
        return task_repo, project_repo
    elif repo_type == RepositoryType.MEMORY:
        # 메모리 리포지토리
        task_repo = InMemoryTaskRepository()
        project_repo = InMemoryProjectRepository()
        # 리포지토리 연결
        project_repo.set_task_repository(task_repo)
        return task_repo, project_repo
    else:
        raise ValueError(f"잘못된 리포지토리 타입: {repo_type}")
