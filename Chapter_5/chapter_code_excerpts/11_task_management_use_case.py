# 작업 관리 유스케이스 - 선택적 서비스 등록 패턴
# - 시스템이 발전하면서 분석(analytics), 감사(audit) 등 선택적 서비스를 유연하게 추가하는 패턴
# - 필수 서비스(리포지토리, 알림)와 선택적 서비스(분석, 감사)를 구분하여 관리

from dataclasses import field, dataclass
from typing import Any
from uuid import UUID

from todo_app.application.common.result import Result, Error
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.application.serviceports.notifications import (
    NotificationPort,
)
from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.domain.exceptions import ValidationError


# 선택적 서비스 등록을 지원하는 작업 관리 유스케이스
# - 필수 의존성: task_repository, notification_service (생성 시 주입)
# - 선택적 의존성: _optional_services 딕셔너리로 런타임에 동적 등록
@dataclass(frozen=True)
class TaskManagementUseCase:
    task_repository: TaskRepository
    notification_service: NotificationPort
    # 선택적 서비스를 저장하는 딕셔너리 (기본값: 빈 딕셔너리)
    _optional_services: dict[str, Any] = field(default_factory=dict)

    # 런타임에 선택적 서비스를 등록하는 메서드
    def register_service(self, name: str, service: Any) -> None:
        """선택적 서비스를 등록"""
        self._optional_services[name] = service

    # 작업 완료 비즈니스 흐름
    def complete_task(self, task_id: UUID) -> Result:
        try:
            task = self.task_repository.get(task_id)
            task.complete()
            self.task_repository.save(task)

            # 필수 알림 처리
            self.notification_service.notify_task_completed(task)

            # 선택적 연동 서비스 처리 (등록된 경우에만 실행)
            # - 왈러스 연산자(:=)로 서비스 존재 여부 확인과 동시에 변수 할당
            if analytics := self._optional_services.get("analytics"):
                analytics.track_task_completion(task.id)
            if audit := self._optional_services.get("audit"):
                audit.log_task_completion(task.id)

            return Result.success(TaskResponse.from_entity(task))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
