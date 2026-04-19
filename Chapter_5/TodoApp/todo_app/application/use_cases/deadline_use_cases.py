# 마감일 확인 유스케이스
# - 모든 활성 작업의 마감일을 점검하고, 임박한 작업에 대해 알림을 전송하는 유스케이스
# - 배치 처리 형태로 여러 작업을 한 번에 확인하여 알림 발송

from dataclasses import field, dataclass
from datetime import timedelta

from todo_app.application.common.result import Result, Error
from todo_app.application.service_ports.notifications import (
    NotificationPort,
)
from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.domain.exceptions import (
    TaskNotFoundError,
    ValidationError,
    BusinessRuleViolation,
)


# 마감일 점검 유스케이스 - 활성 작업의 마감일 임박 여부 확인 후 알림 전송
# - warning_threshold: 마감일 경고 기준 시간 (기본값: 1일)
@dataclass
class CheckDeadlinesUseCase:
    """다가오는 작업 마감일을 확인하고 알림을 전송하는 유스 케이스."""

    task_repository: TaskRepository
    notification_service: NotificationPort
    warning_threshold: timedelta = field(default=timedelta(days=1))

    # 모든 활성 작업의 마감일을 점검하는 실행 메서드
    def execute(self) -> Result:
        """모든 작업을 확인하고 다가오는 마감일에 대해 알림을 전송한다."""
        try:
            # 리포지토리에서 완료되지 않은 활성 작업 목록 조회
            tasks = self.task_repository.get_active_tasks()
            notifications_sent = 0

            for task in tasks:
                # 마감일이 경고 임계값 이내인 작업에 대해 알림 전송
                if task.due_date and task.due_date.is_approaching(self.warning_threshold):
                    # 남은 일수 계산 (초 단위를 일 단위로 변환)
                    remaining_days = int(
                        task.due_date.time_remaining().total_seconds() / (24 * 3600)
                    )
                    self.notification_service.notify_task_deadline_approaching(task, remaining_days)
                    notifications_sent += 1

            # 전송된 알림 수를 포함한 성공 결과 반환
            return Result.success({"notifications_sent": notifications_sent})

        # 도메인 예외를 Result 실패로 변환
        except TaskNotFoundError as e:
            return Result.failure(Error.not_found("Task", str(e)))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
