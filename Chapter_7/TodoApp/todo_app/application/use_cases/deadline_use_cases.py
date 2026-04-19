# 마감일 확인 유스 케이스 — 활성 작업 중 임박한 마감일을 감지하여 알림 전송
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


@dataclass
class CheckDeadlinesUseCase:
    """다가오는 작업 마감일을 확인하고 알리는 유스 케이스."""

    task_repository: TaskRepository          # 활성 작업 조회용 리포지토리
    notification_service: NotificationPort    # 알림 전송용 포트
    warning_threshold: timedelta = field(default=timedelta(days=1))  # 경고 임계값 (기본 1일)

    def execute(self) -> Result:
        """활성 작업을 순회하며 임박한 마감일을 감지하고 알림 전송."""
        try:
            # 완료되지 않은 모든 작업 조회
            tasks = self.task_repository.get_active_tasks()
            notifications_sent = 0

            for task in tasks:
                # 마감일이 있고 경고 임계값 이내인 작업 필터링
                if task.due_date and task.due_date.is_approaching(self.warning_threshold):
                    # 남은 시간을 일 단위로 변환
                    remaining_days = int(
                        task.due_date.time_remaining().total_seconds() / (24 * 3600)
                    )
                    # 알림 포트를 통해 마감일 임박 알림 전송
                    self.notification_service.notify_task_deadline_approaching(task, remaining_days)
                    notifications_sent += 1

            return Result.success({"notifications_sent": notifications_sent})

        except TaskNotFoundError as e:
            return Result.failure(Error.not_found("Task", str(e)))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
        except BusinessRuleViolation as e:
            return Result.failure(Error.business_rule_violation(str(e)))
