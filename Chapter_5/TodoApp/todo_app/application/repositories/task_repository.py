"""
이 모듈은 Task 엔터티 영속성을 위한 리포지토리 인터페이스를 정의한다.
"""
# 작업 리포지토리 인터페이스 정의
# - 애플리케이션 계층에서 정의하고, 인프라 계층에서 구현하는 의존성 역전 원칙(DIP) 적용
# - 기본 CRUD 외에 프로젝트별 작업 조회, 활성 작업 조회 등 유스케이스에 필요한 쿼리 메서드 포함

from abc import ABC, abstractmethod
from typing import Sequence
from uuid import UUID

from todo_app.domain.entities.task import Task


# 작업 영속성을 위한 추상 리포지토리 인터페이스
# - 유스케이스가 필요로 하는 작업 저장/조회/삭제 기능을 계약으로 정의
class TaskRepository(ABC):
    """Task 엔터티 영속성을 위한 리포지토리 인터페이스."""

    @abstractmethod
    def get(self, task_id: UUID) -> Task:
        """
        ID로 작업을 조회한다.

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
        리포지토리의 모든 활성 작업을 조회한다.

        Returns:
            모든 활성 Task의 시퀀스
        """
        pass
