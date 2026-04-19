"""
이 모듈은 todo 애플리케이션의 도메인 특화 예외를 포함한다.
이 예외들은 도메인 모델에 특화된 오류 조건을 나타낸다.
"""

from typing import Optional
from uuid import UUID


# 도메인 계층의 예외 계층 구조
# 모든 도메인 예외는 DomainError를 상속하여 계층별 오류 처리 가능
class DomainError(Exception):
    """도메인 특화 오류의 기본 클래스."""

    pass


class TaskNotFoundError(DomainError):
    """존재하지 않는 작업에 접근하려 할 때 발생한다."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class ProjectNotFoundError(DomainError):
    """존재하지 않는 프로젝트에 접근하려 할 때 발생한다."""

    def __init__(self, project_id: Optional[UUID]) -> None:
        self.project_id = project_id
        super().__init__(f"Project with id {project_id} not found")


class InboxNotFoundError(DomainError):
    """존재하지 않는 INBOX 프로젝트에 접근하려 할 때 발생한다."""

    pass


class ValidationError(DomainError):
    """도메인 유효성 검사 규칙이 위반될 때 발생한다."""

    pass


class BusinessRuleViolation(DomainError):
    """비즈니스 규칙이 위반될 때 발생한다."""

    pass
