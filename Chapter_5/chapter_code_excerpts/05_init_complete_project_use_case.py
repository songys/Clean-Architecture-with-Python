"""
18페이지의 NotificationService 초기 예제
"""
# 프로젝트 완료 유스케이스의 초기 버전
# - 여러 리포지토리와 알림 서비스를 조합하여 복합 비즈니스 흐름을 조율하는 유스케이스
# - 프로젝트의 미완료 작업을 모두 완료 처리 후, 프로젝트 자체를 완료로 표시하는 흐름

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from todo_app.application.common.result import Result, Error
from todo_app.application.repositories.project_repository import (
    ProjectRepository,
)
from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.domain.exceptions import (
    ProjectNotFoundError,
    ValidationError,
)

from todo_app.domain.models.task import Task


# 알림 서비스 스텁 (실제 구현은 인프라 계층에서 제공)
class NotificationService:
    """mypy를 위한 스텁"""

    def notify_task_completed(self, task: Task) -> None:
        pass


# 프로젝트 완료 유스케이스 - 여러 의존성을 조합한 복합 흐름 조율
# - project_repository: 프로젝트 조회/저장을 위한 리포지토리
# - task_repository: 작업 저장을 위한 리포지토리
# - notification_service: 작업 완료 알림 전송을 위한 서비스
@dataclass(frozen=True)
class CompleteProjectUseCase:
    project_repository: ProjectRepository
    task_repository: TaskRepository
    notification_service: NotificationService

    # 프로젝트 완료 비즈니스 흐름을 실행하는 메서드
    def execute(self, project_id: UUID, completion_notes: Optional[str] = None) -> Result:
        try:
            # 프로젝트 존재 여부 검증
            project = self.project_repository.get(project_id)

            # 미완료된 모든 작업 완료 처리
            for task in project.incomplete_tasks:
                task.complete()
                self.task_repository.save(task)
                # 각 작업 완료 시 이해관계자에게 알림 전송
                self.notification_service.notify_task_completed(task)

            # 프로젝트 자체를 완료 처리
            project.mark_completed(notes=completion_notes)
            self.project_repository.save(project)

            # 성공 결과를 딕셔너리 형태로 반환
            return Result.success(
                {
                    "id": str(project.id),
                    "status": project.status,
                    "completion_date": project.completed_at,
                    "task_count": len(project.tasks),
                    "completion_notes": project.completion_notes,
                }
            )

        # 도메인 예외를 Result 실패로 변환하여 반환
        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(project_id)))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
