# 발전된 프로젝트 완료 유스케이스
# - 요청 DTO(CompleteProjectRequest)와 응답 DTO(CompleteProjectResponse)를 활용한 개선 버전
# - 초기 버전(05번)과 비교: 원시 매개변수 대신 DTO를 통해 입출력 경계를 명확히 분리

from dataclasses import dataclass

from todo_app.domain.entities.task import Task
from todo_app.application.common.result import Result, Error
from todo_app.application.dtos.project_dtos import (
    CompleteProjectRequest,
    CompleteProjectResponse,
)
from todo_app.application.repositories.project_repository import (
    ProjectRepository,
)
from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.domain.exceptions import (
    ValidationError,
    ProjectNotFoundError,
)


# 알림 서비스 스텁 (실제 구현은 인프라 계층에서 제공)
class NotificationService:
    """mypy를 위한 스텁"""

    def notify_task_completed(self, task: Task) -> None:
        pass


# DTO를 활용한 발전된 프로젝트 완료 유스케이스
# - execute 메서드가 CompleteProjectRequest DTO를 입력으로 받고, CompleteProjectResponse DTO를 결과로 반환
@dataclass(frozen=True)
class CompleteProjectUseCase:
    project_repository: ProjectRepository
    task_repository: TaskRepository
    notification_service: NotificationService

    def execute(self, request: CompleteProjectRequest) -> Result:
        try:
            # 요청 DTO에서 검증 완료된 실행 매개변수를 추출
            params = request.to_execution_params()
            project = self.project_repository.get(params["project_id"])
            project.mark_completed(notes=params["completion_notes"])

            # 미완료된 모든 작업 완료 처리
            # ... 간결함을 위해 생략

            self.project_repository.save(project)

            # 도메인 엔터티를 응답 DTO로 변환하여 반환
            response = CompleteProjectResponse.from_entity(project)
            return Result.success(response)

        except ProjectNotFoundError:
            return Result.failure(Error.not_found("Project", str(params["project_id"])))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
