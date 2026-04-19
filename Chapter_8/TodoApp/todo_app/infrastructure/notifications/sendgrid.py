# todo_app/infrastructure/notifications/sendgrid.py
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


# NotificationPort의 실제 구현: SendGrid API를 통한 이메일 알림 전송
# 테스트 시에는 이 클래스 대신 Mock이나 NotificationRecorder를 사용
class SendGridNotifier(NotificationPort):
    """알림 포트의 SendGrid 구현."""

    def __init__(self) -> None:
        self.api_key = Config.get_sendgrid_api_key()
        self.notification_email = Config.get_notification_email()
        self._init_sg_client()

    def _init_sg_client(self):
        if not self.api_key:
            logger.error("SendGrid API 키를 찾을 수 없어 클라이언트 초기화를 건너뜁니다")
            raise ValueError("SendGrid API 키를 찾을 수 없습니다")
        self.client = SendGridAPIClient(self.api_key)

    def notify_task_completed(self, task: Task) -> None:
        """구성된 경우 완료된 작업에 대한 이메일 알림을 전송한다."""
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
            # 오류를 기록하되 비즈니스 운영을 방해하지 않음
            logger.error(
                f"Failed to send completion notification for task {str(task.id)}: {str(e)}"
            )

    def notify_task_high_priority(self, task: Task) -> None:
        """미구현 - NotificationPort 인터페이스 사용."""
        pass

    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """미구현 - NotificationPort 인터페이스 사용."""
        pass
