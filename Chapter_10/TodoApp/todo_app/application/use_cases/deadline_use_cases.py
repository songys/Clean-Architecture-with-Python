# 마감일 확인 유스 케이스
# - 주기적으로 실행하여 마감 임박 작업에 대한 알림 발송
# - 구조화된 로깅으로 확인 과정 및 결과 추적
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

import logging

logger = logging.getLogger(__name__)


@dataclass
class CheckDeadlinesUseCase:
    """다가오는 작업 마감일을 확인하고 알림을 보내는 유스 케이스.
    - warning_threshold 이내의 마감일을 가진 작업에 알림 발송
    - 확인한 작업 수와 발송한 알림 수를 로깅하여 운영 모니터링 지원
    """

    task_repository: TaskRepository
    notification_service: NotificationPort
    # 마감일 경고 임계값 (기본: 1일)
    warning_threshold: timedelta = field(default=timedelta(days=1))

    def execute(self) -> Result:
        """모든 작업을 확인하고 다가오는 마감일에 대해 알림을 보낸다."""
        try:
            logger.info(
                "Checking task deadlines",
                extra={"context": {"warning_threshold_days": self.warning_threshold.days}},
            )
            tasks = self.task_repository.get_active_tasks()
            notifications_sent = 0

            for task in tasks:
                if task.due_date and task.due_date.is_approaching(self.warning_threshold):
                    remaining_days = int(
                        task.due_date.time_remaining().total_seconds() / (24 * 3600)
                    )
                    logger.info(
                        "Task deadline approaching",
                        extra={
                            "context": {
                                "task_id": str(task.id),
                                "remaining_days": remaining_days,
                            }
                        },
                    )
                    self.notification_service.notify_task_deadline_approaching(task, remaining_days)
                    notifications_sent += 1

            logger.info(
                "Deadline check completed",
                extra={
                    "context": {
                        "total_tasks_checked": len(tasks),
                        "notifications_sent": notifications_sent,
                    }
                },
            )
            return Result.success({"notifications_sent": notifications_sent})

        except TaskNotFoundError as e:
            logger.error("Task not found during deadline check", extra={"context": {"error": str(e)}})
            return Result.failure(Error.not_found("Task", str(e)))
        except ValidationError as e:
            logger.error("Validation error during deadline check", extra={"context": {"error": str(e)}})
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            logger.error("Business rule violation during deadline check", extra={"context": {"error": str(e)}})
            return Result.failure(Error.business_rule_violation(str(e)))
