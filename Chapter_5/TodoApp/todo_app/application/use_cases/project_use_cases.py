"""
이 모듈은 프로젝트 연산을 위한 유스 케이스를 포함한다.
"""
# 프로젝트 관련 유스케이스 모음
# - CreateProjectUseCase: 새 프로젝트 생성
# - CompleteProjectUseCase: 프로젝트 완료 (미완료 작업 일괄 완료 + 롤백 지원)

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


# 새 프로젝트 생성 유스케이스
@dataclass
class CreateProjectUseCase:
    """새 프로젝트를 생성하는 유스 케이스."""

    project_repository: ProjectRepository

    # 프로젝트 생성 흐름: 요청 DTO에서 매개변수 추출 -> 도메인 엔터티 생성 -> 리포지토리에 저장
    def execute(self, request: CreateProjectRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            # 요청 DTO에서 검증된 매개변수 추출
            params = request.to_execution_params()

            # 도메인 엔터티 생성
            project = Project(name=params["name"], description=params["description"])

            # 리포지토리에 저장
            self.project_repository.save(project)

            # 도메인 엔터티를 응답 DTO로 변환하여 반환
            return Result.success(ProjectResponse.from_entity(project))

        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))


# 프로젝트 완료 유스케이스 - 미완료 작업 일괄 완료 + 실패 시 롤백 지원
# - deepcopy로 초기 상태 스냅샷을 저장하여, 실패 시 원래 상태로 복원하는 트랜잭션 패턴
@dataclass
class CompleteProjectUseCase:
    """프로젝트를 완료로 표시하는 유스 케이스."""

    project_repository: ProjectRepository
    task_repository: TaskRepository
    notification_service: NotificationPort

    # 프로젝트 완료 흐름: 스냅샷 저장 -> 작업 완료 -> 프로젝트 완료 -> 알림 (실패 시 롤백)
    def execute(self, request: CompleteProjectRequest) -> Result:
        """유스 케이스를 실행한다."""
        try:
            params = request.to_execution_params()
            project = self.project_repository.get(params["project_id"])

            # 초기 상태의 스냅샷 저장 (실패 시 롤백을 위한 깊은 복사)
            project_snapshot = deepcopy(project)
            task_snapshots = {task.id: deepcopy(task) for task in project.incomplete_tasks}

            try:
                # 미완료된 모든 작업 완료 처리
                for task in project.incomplete_tasks:
                    task.complete()
                    self.task_repository.save(task)

                # 프로젝트 자체를 완료로 표시
                project.mark_completed(
                    notes=params["completion_notes"],
                )

                self.project_repository.save(project)
                # 스냅샷의 미완료 작업 목록으로 알림 전송 (완료 처리 전 상태 기준)
                for task in project_snapshot.incomplete_tasks:
                    self.notification_service.notify_task_completed(task)
                return Result.success(CompleteProjectResponse.from_entity(project))

            except (ValidationError, BusinessRuleViolation) as e:
                # 실패 시 스냅샷으로 프로젝트와 작업 상태 복원 (롤백)
                for task_id, task_snapshot in task_snapshots.items():
                    self.task_repository.save(task_snapshot)
                self.project_repository.save(project_snapshot)
                raise  # 외부 try 블록에서 포착하도록 예외를 다시 발생

        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(params["project_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
