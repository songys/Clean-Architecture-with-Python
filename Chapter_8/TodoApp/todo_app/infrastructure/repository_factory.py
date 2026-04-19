"""
구성에 따라 리포지토리를 생성하는 팩토리 함수.
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


# 리포지토리 팩토리: 설정에 따라 파일 또는 메모리 저장소 인스턴스를 생성하고 연결
def create_repositories() -> Tuple[TaskRepository, ProjectRepository]:
    """
    구성에 따라 적절한 리포지토리 구현을 생성하고 설정한다.

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
        raise ValueError(f"유효하지 않은 리포지토리 타입: {repo_type}")
