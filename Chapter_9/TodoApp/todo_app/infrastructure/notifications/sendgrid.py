# todo_app/infrastructure/notifications/sendgrid.py
# SendGrid 이메일 API를 사용하는 알림 포트 구현체
# NotificationPort 인터페이스를 구현하여 의존성 역전 원칙 준수
# [수정] sendgrid 미설치 시에도 동작하도록 보호
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
except ImportError:
    SendGridAPIClient = None  # type: ignore
    Mail = None  # type: ignore
import logging

from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.domain.entities.task import Task
from todo_app.infrastructure.config import Config

logger = logging.getLogger(__name__)


# NotificationPort의 실제 이메일 발송 구현체
# NotificationRecorder(개발용)와 교체 가능한 프로덕션용 구현체
class SendGridNotifier(NotificationPort):
    """알림 포트의 SendGrid 구현."""

    def __init__(self) -> None:
        self.api_key = Config.get_sendgrid_api_key()
        self.notification_email = Config.get_notification_email()
        self._init_sg_client()

    def _init_sg_client(self):
        if not self.api_key:
            logger.error("SendGrid API key not found, skipping client initialization")
            raise ValueError("SendGrid API key not found")
        self.client = SendGridAPIClient(self.api_key)

    def notify_task_completed(self, task: Task) -> None:
        """구성된 경우 완료된 작업에 대해 이메일 알림을 보낸다."""
        if not (self.client and self.notification_email):
            logger.warning(
                f"SendGrid not configured, skipping notification, task_id: {str(task.id)}"
            )
            return
        obfuscated_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if self.api_key else "None"
        logger.info(
            f"Attempting to send notification with SendGrid - "
            f"API Key: {obfuscated_key}, "
            f"Email: {self.notification_email}"
        )
        try:
            message = Mail(
                from_email=self.notification_email,
                to_emails=self.notification_email,
                subject=f"Task Completed: {task.title}",
                html_content=f"<strong>Task '{task.title}'</strong> has been completed.",
            )
            response = self.client.send(message)
            logger.info(
                f"Notification sent successfully - task_id: {str(task.id)}, "
                f"notification_email: {self.notification_email}, "
                f"response: {response.status_code}"
            )
        except Exception as e:
            # 오류를 로깅하되 비즈니스 운영을 방해하지 않음
            logger.error(
                f"Failed to send completion notification for task {str(task.id)}: {str(e)}"
            )

    def notify_task_high_priority(self, task: Task) -> None:
        """미구현 - NotificationPort 인터페이스 사용."""
        pass

    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """미구현 - NotificationPort 인터페이스 사용."""
        pass
