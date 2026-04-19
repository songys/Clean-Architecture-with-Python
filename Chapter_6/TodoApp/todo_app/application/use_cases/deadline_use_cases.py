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


# 마감일 임박 확인 유스케이스 - 활성 작업들의 마감일을 검사하고 필요 시 알림 발송
@dataclass
class CheckDeadlinesUseCase:
    """다가오는 작업 마감일을 확인하고 알림을 보내는 유스 케이스"""

    task_repository: TaskRepository  # 활성 작업 조회를 위한 리포지토리
    notification_service: NotificationPort  # 마감일 임박 알림 발송을 위한 서비스 포트
    warning_threshold: timedelta = field(default=timedelta(days=1))  # 알림 발송 기준 임계값 (기본 1일)

    def execute(self) -> Result:
        """모든 작업을 확인하고 다가오는 마감일에 대해 알림을 보낸다."""
        try:
            tasks = self.task_repository.get_active_tasks()
            notifications_sent = 0

            for task in tasks:
                if task.due_date and task.due_date.is_approaching(self.warning_threshold):
                    remaining_days = int(
                        task.due_date.time_remaining().total_seconds() / (24 * 3600)
                    )
                    self.notification_service.notify_task_deadline_approaching(task, remaining_days)
                    notifications_sent += 1

            return Result.success({"notifications_sent": notifications_sent})

        except TaskNotFoundError as e:
            return Result.failure(Error.not_found("Task", str(e)))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
