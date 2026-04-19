"""
이 모듈은 Project 엔터티 영속성을 위한 리포지토리 인터페이스를 정의한다.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from todo_app.domain.entities.project import Project


class ProjectRepository(ABC):
    """Project 엔터티 영속성을 위한 리포지토리 인터페이스."""

    @abstractmethod
    def get(self, project_id: UUID) -> Project:
        """
        ID로 프로젝트를 조회한다.

        Args:
            project_id: 프로젝트의 고유 식별자

        Returns:
            요청된 Project 엔터티

        Raises:
            ProjectNotFoundError: 해당 ID의 프로젝트가 존재하지 않는 경우
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Project]:
        """
        모든 프로젝트를 조회한다.
        """
        pass

    @abstractmethod
    def save(self, project: Project) -> None:
        """
        프로젝트를 리포지토리에 저장한다.

        Args:
            project: 저장할 Project 엔터티
        """
        pass

    @abstractmethod
    def delete(self, project_id: UUID) -> None:
        """
        리포지토리에서 프로젝트를 삭제한다.

        Args:
            project_id: 삭제할 프로젝트의 고유 식별자
        """
        pass

    @abstractmethod
    def get_inbox(self) -> Project:
        """INBOX 프로젝트를 가져온다."""
        pass
