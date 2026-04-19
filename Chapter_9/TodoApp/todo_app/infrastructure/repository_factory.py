"""
구성에 따라 리포지토리를 생성하는 팩토리 함수.
환경 변수 설정에 따라 메모리/파일 기반 구현체를 자동 선택
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


# 리포지토리 팩토리 - 환경 변수에 따라 영속성 구현체 자동 선택
# 추상 리포지토리 타입으로 반환하여 의존성 역전 원칙 준수
def create_repositories() -> Tuple[TaskRepository, ProjectRepository]:
    """
    구성에 따라 적절한 리포지토리 구현을 생성하고 구성한다.

    Returns:
        (TaskRepository, ProjectRepository) 튜플
    """
    # 환경 변수 TODO_REPOSITORY_TYPE으로 리포지토리 유형 결정
    repo_type = Config.get_repository_type()

    # 파일 기반 영속성 - JSON 파일로 데이터 저장
    if repo_type == RepositoryType.FILE:
        data_dir = Config.get_data_directory()
        task_repo = FileTaskRepository(data_dir)
        project_repo = FileProjectRepository(data_dir)
        project_repo.set_task_repository(task_repo)
        return task_repo, project_repo
    # 메모리 기반 영속성 - 딕셔너리로 데이터 저장 (애플리케이션 종료 시 소멸)
    elif repo_type == RepositoryType.MEMORY:
        task_repo = InMemoryTaskRepository()
        project_repo = InMemoryProjectRepository()
        # 리포지토리 연결
        project_repo.set_task_repository(task_repo)
        return task_repo, project_repo
    else:
        raise ValueError(f"잘못된 리포지토리 유형: {repo_type}")
