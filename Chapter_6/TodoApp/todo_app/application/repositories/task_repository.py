"""
이 모듈은 Task 엔터티 영속성을 위한 리포지토리 인터페이스를 정의한다.
"""

from abc import ABC, abstractmethod
from typing import Sequence
from uuid import UUID

from todo_app.domain.entities.task import Task


# 작업 영속성을 위한 추상 리포지토리 인터페이스 (포트)
# - 애플리케이션 계층이 정의하고 인프라 계층이 구현하는 의존성 역전 패턴
# - 유스케이스는 이 인터페이스에만 의존하므로 저장소 구현 교체가 자유로움
class TaskRepository(ABC):
    """Task 엔터티 영속성을 위한 리포지토리 인터페이스"""

    @abstractmethod
    def get(self, task_id: UUID) -> Task:
        """
        ID를 기준으로 작업(Task)을 조회한다.

        Args:
            task_id: 작업의 고유 식별자

        Returns:
            요청된 Task 엔터티

        Raises:
            TaskNotFoundError: 주어진 ID의 작업이 존재하지 않는 경우
        """
        pass

    @abstractmethod
    def save(self, task: Task) -> None:
        """
        작업을 리포지토리에 저장한다.

        Args:
            task: 저장할 Task 엔터티
        """
        pass

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        """
        리포지토리에서 작업을 삭제한다.

        Args:
            task_id: 삭제할 작업의 고유 식별자
        """
        pass

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> Sequence[Task]:
        """
        프로젝트에 속한 모든 작업을 조회한다.

        Args:
            project_id: 프로젝트의 고유 식별자

        Returns:
            프로젝트에 속한 Task 엔터티의 시퀀스
        """
        pass

    @abstractmethod
    def get_active_tasks(self) -> Sequence[Task]:
        """
        리포지토리에서 모든 활성 작업을 조회한다.

        Returns:
            모든 활성 Task의 시퀀스
        """
        pass
