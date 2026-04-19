"""
도메인 계층의 예외 클래스 모듈.
- 도메인 모델에 특화된 오류 조건을 표현하는 예외 계층 구조
- 외부 계층(application, infrastructure)에서 이 예외를 잡아 적절히 처리
- 도메인 예외를 통해 비즈니스 규칙 위반을 명확하게 전달
"""

from typing import Optional
from uuid import UUID


class DomainError(Exception):
    """도메인 특화 오류의 기본 클래스.
    - 모든 도메인 예외의 공통 부모 클래스
    """

    pass


class TaskNotFoundError(DomainError):
    """존재하지 않는 작업에 접근하려고 할 때 발생한다."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"ID가 {task_id}인 작업을 찾을 수 없음")


class ProjectNotFoundError(DomainError):
    """존재하지 않는 프로젝트에 접근하려고 할 때 발생한다."""

    def __init__(self, project_id: Optional[UUID]) -> None:
        self.project_id = project_id
        super().__init__(f"ID가 {project_id}인 프로젝트를 찾을 수 없음")


class InboxNotFoundError(DomainError):
    """존재하지 않는 INBOX 프로젝트에 접근하려고 할 때 발생한다."""

    pass


class ValidationError(DomainError):
    """도메인 검증 규칙이 위반되었을 때 발생한다."""

    pass


class BusinessRuleViolation(DomainError):
    """비즈니스 규칙이 위반되었을 때 발생한다."""

    pass
