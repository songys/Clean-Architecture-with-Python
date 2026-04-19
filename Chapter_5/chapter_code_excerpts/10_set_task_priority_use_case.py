# 작업 우선순위 설정 유스케이스
# - 포트(NotificationPort) 인터페이스를 활용하여 알림 서비스와의 결합도를 낮춘 구현 예제
# - 요청 DTO(SetTaskPriorityRequest)로 입력을 받고, 응답 DTO(TaskResponse)로 결과를 반환

from dataclasses import dataclass

from todo_app.application.common.result import Result, Error
from todo_app.application.dtos.task_dtos import (
    TaskResponse,
    SetTaskPriorityRequest,
)
from todo_app.application.service_ports.notifications import (
    NotificationPort,
)
from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.domain.exceptions import ValidationError
from todo_app.domain.value_objects import Priority


# 작업 우선순위를 변경하는 유스케이스
# - notification_service: 구체적 구현이 아닌 NotificationPort 인터페이스에 의존 (의존성 역전)
@dataclass
class SetTaskPriorityUseCase:
    task_repository: TaskRepository
    notification_service: NotificationPort  # 기능을 정의한 인터페이스에 의존

    def execute(self, request: SetTaskPriorityRequest) -> Result:
        try:
            # 요청 DTO에서 검증된 매개변수 추출
            params = request.to_execution_params()

            # 리포지토리에서 작업 조회 후 우선순위 변경
            task = self.task_repository.get(params["task_id"])
            task.priority = params["priority"]

            self.task_repository.save(task)

            # 높은 우선순위 설정 시 알림 전송 (포트 인터페이스 활용)
            if task.priority == Priority.HIGH:
                self.notification_service.notify_task_high_priority(task)

            # 도메인 엔터티를 응답 DTO로 변환하여 반환
            return Result.success(TaskResponse.from_entity(task))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
