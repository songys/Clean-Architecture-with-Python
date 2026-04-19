"""
이 모듈은 Project 엔터티 영속성을 위한 리포지토리 인터페이스를 정의한다.
"""
# 프로젝트 리포지토리 인터페이스 정의
# - 애플리케이션 계층에서 정의하고, 인프라 계층에서 구현하는 의존성 역전 원칙(DIP) 적용
# - 유스케이스가 구체적인 데이터 저장 방식(DB 종류 등)에 의존하지 않도록 추상화

from abc import ABC, abstractmethod
from uuid import UUID

from todo_app.domain.entities.project import Project


# 프로젝트 영속성을 위한 추상 리포지토리 인터페이스
# - 구현체(예: PostgreSQL, MongoDB)는 인프라 계층에서 제공
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
            ProjectNotFoundError: 주어진 ID의 프로젝트가 존재하지 않는 경우
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
