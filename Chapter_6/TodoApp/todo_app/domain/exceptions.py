"""
이 모듈은 할 일 관리 애플리케이션의 도메인 전용 예외를 포함한다.
이러한 예외는 도메인 모델에 특화된 오류 조건을 나타낸다.
"""

from uuid import UUID


# 모든 도메인 예외의 기반 클래스 - 도메인 계층에서 발생하는 오류를 구분하기 위한 계층 구조
class DomainError(Exception):
    """도메인 전용 오류의 기반 클래스"""

    pass


# 존재하지 않는 작업에 접근할 때 발생하는 예외
class TaskNotFoundError(DomainError):
    """존재하지 않는 작업에 접근하려 할 때 발생한다."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class ProjectNotFoundError(DomainError):
    """존재하지 않는 프로젝트에 접근하려 할 때 발생한다."""

    def __init__(self, project_id: UUID) -> None:
        self.project_id = project_id
        super().__init__(f"Project with id {project_id} not found")


class ValidationError(DomainError):
    """도메인 검증 규칙이 위반되었을 때 발생한다."""

    pass


class BusinessRuleViolation(DomainError):
    """비즈니스 규칙이 위반되었을 때 발생한다."""

    pass
