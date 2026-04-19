"""
이 모듈은 작업(Task) 관련 유스 케이스를 포함한다.
"""

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


# 작업 완료 비즈니스 로직을 캡슐화하는 유스케이스
# - 작업 상태 변경, 저장, 알림 발송을 조율
# - 실패 시 작업 상태를 원래대로 복원하는 롤백 메커니즘 포함
@dataclass
class CompleteTaskUseCase:
    """작업을 완료로 표시하고 관계자에게 알림을 보내는 유스 케이스"""

    task_repository: TaskRepository  # 작업 영속성을 위한 리포지토리 인터페이스
    notification_service: NotificationPort  # 알림 발송을 위한 서비스 포트 인터페이스

    def execute(self, request: CompleteTaskRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            task = self.task_repository.get(params["task_id"])

            # 초기 상태 스냅샷 저장
            task_snapshot = deepcopy(task)

            try:
                task.complete(notes=params["completion_notes"])
                self.task_repository.save(task)
                self.notification_service.notify_task_completed(task)

                return Result.success(TaskResponse.from_entity(task))

            except (ValidationError, BusinessRuleViolation) as e:
                # 작업 상태 복원
                self.task_repository.save(task_snapshot)
                raise  # 외부 try 블록에서 처리하도록 예외를 다시 발생

        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(params["task_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


# 새 작업 생성 비즈니스 로직을 캡슐화하는 유스케이스
# - 프로젝트 존재 여부 확인, 작업 생성, 저장을 조율
@dataclass
class CreateTaskUseCase:
    """새로운 작업을 생성하는 유스 케이스"""

    task_repository: TaskRepository  # 작업 영속성을 위한 리포지토리 인터페이스
    project_repository: ProjectRepository  # 프로젝트 존재 확인을 위한 리포지토리 인터페이스

    def execute(self, request: CreateTaskRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()

            # 작업이 프로젝트에 속하는 경우, 프로젝트 존재 여부를 확인
            project_id = params.get("project_id")
            if project_id:
                self.project_repository.get(project_id)

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


# 작업 우선순위 변경 유스케이스 - 높은 우선순위 설정 시 알림 발송
@dataclass
class SetTaskPriorityUseCase:
    task_repository: TaskRepository
    notification_service: NotificationPort  # 기능 인터페이스에 의존

    def execute(self, request: SetTaskPriorityRequest) -> Result:
        try:
            params = request.to_execution_params()

            task = self.task_repository.get(params["task_id"])
            task.priority = params["priority"]

            self.task_repository.save(task)

            if task.priority == Priority.HIGH:
                self.notification_service.notify_task_high_priority(task)

            return Result.success(TaskResponse.from_entity(task))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
