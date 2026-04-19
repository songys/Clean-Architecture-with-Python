"""
이 모듈은 프로젝트 작업을 위한 유스 케이스를 포함한다.
"""

from copy import deepcopy
from dataclasses import dataclass

from todo_app.application.common.result import Result, Error
from todo_app.application.dtos.project_dtos import (
    CreateProjectRequest,
    ProjectResponse,
    CompleteProjectRequest,
    CompleteProjectResponse,
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
from todo_app.domain.entities.project import Project
from todo_app.domain.exceptions import (
    ValidationError,
    BusinessRuleViolation,
    ProjectNotFoundError,
)


# 새 프로젝트 생성 비즈니스 로직을 캡슐화하는 유스케이스
@dataclass
class CreateProjectUseCase:
    """새로운 프로젝트를 생성하는 유스 케이스"""

    project_repository: ProjectRepository  # 프로젝트 영속성을 위한 리포지토리 인터페이스

    def execute(self, request: CreateProjectRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()

            project = Project(name=params["name"], description=params["description"])

            self.project_repository.save(project)

            return Result.success(ProjectResponse.from_entity(project))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


# 프로젝트 완료 유스케이스 - 미완료 작업 일괄 완료, 프로젝트 상태 변경, 알림 발송을 조율
# - 실패 시 프로젝트와 작업 상태를 원래대로 복원하는 롤백 메커니즘 포함
@dataclass
class CompleteProjectUseCase:
    """프로젝트를 완료로 표시하는 유스 케이스"""

    project_repository: ProjectRepository
    task_repository: TaskRepository
    notification_service: NotificationPort

    def execute(self, request: CompleteProjectRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            project = self.project_repository.get(params["project_id"])

            # 초기 상태 스냅샷 저장
            project_snapshot = deepcopy(project)
            task_snapshots = {task.id: deepcopy(task) for task in project.incomplete_tasks}

            try:
                # 미완료 작업 모두 완료 처리
                for task in project.incomplete_tasks:
                    task.complete()
                    self.task_repository.save(task)

                project.mark_completed(
                    notes=params["completion_notes"],
                )

                self.project_repository.save(project)
                for task in project_snapshot.incomplete_tasks:
                    self.notification_service.notify_task_completed(task)
                return Result.success(CompleteProjectResponse.from_entity(project))

            except (ValidationError, BusinessRuleViolation) as e:
                # 프로젝트 상태 복원
                for task_id, task_snapshot in task_snapshots.items():
                    self.task_repository.save(task_snapshot)
                self.project_repository.save(project_snapshot)
                raise  # 외부 try 블록에서 처리하도록 예외를 다시 발생

        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(params["project_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
