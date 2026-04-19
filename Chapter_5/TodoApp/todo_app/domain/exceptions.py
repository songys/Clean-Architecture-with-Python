"""
이 모듈은 할 일 애플리케이션의 도메인 고유 예외를 포함한다.
이 예외들은 도메인 모델에 특화된 오류 상태를 나타낸다.
"""
# 도메인 계층 전용 예외 클래스 계층 구조
# - DomainError를 기반으로 엔터티 미발견, 검증 실패, 비즈니스 규칙 위반 등을 구분
# - 유스케이스에서 이 예외들을 Result 실패로 변환하여 반환

from uuid import UUID


# 도메인 예외의 기반 클래스 - 모든 도메인 예외가 상속
class DomainError(Exception):
    """도메인 고유 오류의 기본 클래스."""

    pass


# 존재하지 않는 작업 접근 시 발생하는 예외
class TaskNotFoundError(DomainError):
    """존재하지 않는 작업에 접근하려 할 때 발생한다."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"ID가 {task_id}인 작업을 찾을 수 없음")


# 존재하지 않는 프로젝트 접근 시 발생하는 예외
class ProjectNotFoundError(DomainError):
    """존재하지 않는 프로젝트에 접근하려 할 때 발생한다."""

    def __init__(self, project_id: UUID) -> None:
        self.project_id = project_id
        super().__init__(f"ID가 {project_id}인 프로젝트를 찾을 수 없음")


# 도메인 검증 규칙 위반 시 발생하는 예외 (예: 잘못된 입력값)
class ValidationError(DomainError):
    """도메인 검증 규칙이 위반되었을 때 발생한다."""

    pass


# 비즈니스 규칙 위반 시 발생하는 예외 (예: 이미 완료된 작업 재완료 시도)
class BusinessRuleViolation(DomainError):
    """비즈니스 규칙이 위반되었을 때 발생한다."""

    pass
