"""
이 모듈은 작업 연산을 위한 유스 케이스를 포함한다.
"""
# 작업 관련 유스케이스 모음
# - CompleteTaskUseCase: 작업 완료 (실패 시 롤백 지원)
# - CreateTaskUseCase: 새 작업 생성 (프로젝트 연결 지원)
# - SetTaskPriorityUseCase: 작업 우선순위 변경 (높은 우선순위 시 알림 전송)

from copy import deepcopy
from dataclasses import dataclass

from todo_app.application.common.result import Result, Error
from todo_app.application.dtos.task_dtos import (
    CompleteTaskRequest,
    CreateTaskRequest,
    TaskResponse,
    SetTaskPriorityRequest,
)
from todo_app.application.service_ports.notifications import (
    NotificationPort,
)
from todo_app.application.repositories.project_repository import (
    ProjectRepository,
)
from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.domain.entities.task import Task
from todo_app.domain.exceptions import (
    TaskNotFoundError,
    ProjectNotFoundError,
    ValidationError,
    BusinessRuleViolation,
)
from todo_app.domain.value_objects import Priority


# 작업 완료 유스케이스 - 실패 시 스냅샷을 이용한 롤백 지원
@dataclass
class CompleteTaskUseCase:
    """작업을 완료로 표시하고 이해관계자에게 알리는 유스 케이스."""

    task_repository: TaskRepository
    notification_service: NotificationPort

    # 작업 완료 흐름: 스냅샷 저장 -> 완료 처리 -> 저장 -> 알림 (실패 시 롤백)
    def execute(self, request: CompleteTaskRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            task = self.task_repository.get(params["task_id"])

            # 초기 상태의 스냅샷 저장 (실패 시 롤백을 위한 깊은 복사)
            task_snapshot = deepcopy(task)

            try:
                # 도메인 로직 실행: 작업 완료 처리
                task.complete(notes=params["completion_notes"])
                self.task_repository.save(task)
                # 완료 알림 전송
                self.notification_service.notify_task_completed(task)

                return Result.success(TaskResponse.from_entity(task))

            except (ValidationError, BusinessRuleViolation) as e:
                # 실패 시 스냅샷으로 작업 상태 복원 (롤백)
                self.task_repository.save(task_snapshot)
                raise  # 외부 try 블록에서 포착하도록 예외를 다시 발생

        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(params["task_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


# 새 작업 생성 유스케이스 - 프로젝트 존재 여부 확인 후 작업 생성
@dataclass
class CreateTaskUseCase:
    """새 작업을 생성하는 유스 케이스."""

    task_repository: TaskRepository
    project_repository: ProjectRepository

    # 작업 생성 흐름: 프로젝트 존재 확인 -> 도메인 엔터티 생성 -> 리포지토리에 저장
    def execute(self, request: CreateTaskRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()

            # 작업이 프로젝트에 속하는 경우, 프로젝트 존재 여부 확인
            project_id = params.get("project_id")
            if project_id:
                self.project_repository.get(project_id)

            # 도메인 엔터티 생성 (기본 우선순위: MEDIUM)
            task = Task(
                title=params["title"],
                description=params["description"],
                due_date=params.get("deadline"),
                priority=params.get("priority", Priority.MEDIUM),
            )

            # 프로젝트 ID가 제공된 경우 설정
            if project_id:
                task.project_id = project_id

            self.task_repository.save(task)

            return Result.success(TaskResponse.from_entity(task))

        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(params.get("project_id"))))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


# 작업 우선순위 설정 유스케이스 - NotificationPort 인터페이스를 통한 알림 전송
@dataclass
class SetTaskPriorityUseCase:
    task_repository: TaskRepository
    notification_service: NotificationPort  # 기능을 정의한 인터페이스에 의존

    # 우선순위 변경 흐름: 작업 조회 -> 우선순위 변경 -> 저장 -> 높은 우선순위 시 알림 전송
    def execute(self, request: SetTaskPriorityRequest) -> Result:
        try:
            params = request.to_execution_params()

            # 리포지토리에서 작업 조회 후 우선순위 변경
            task = self.task_repository.get(params["task_id"])
            task.priority = params["priority"]

            self.task_repository.save(task)

            # 높은 우선순위 설정 시 포트를 통해 알림 전송
            if task.priority == Priority.HIGH:
                self.notification_service.notify_task_high_priority(task)

            return Result.success(TaskResponse.from_entity(task))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
