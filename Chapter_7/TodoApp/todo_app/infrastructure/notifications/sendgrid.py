# todo_app/infrastructure/notifications/sendgrid.py
# NotificationPort 인터페이스의 SendGrid 이메일 서비스 어댑터(구현체)
# 외부 서비스(SendGrid)를 클린 아키텍처의 포트를 통해 통합하는 예시

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


class SendGridNotifier(NotificationPort):
    """알림 포트의 SendGrid 구현 — 외부 이메일 서비스 어댑터."""

    def __init__(self) -> None:
        # Config 클래스에서 환경 변수 기반 인증 정보 조회
        self.api_key = Config.get_sendgrid_api_key()
        self.notification_email = Config.get_notification_email()
        self._init_sg_client()

    def _init_sg_client(self):
        """SendGrid API 클라이언트 초기화 — API 키가 없으면 예외 발생"""
        if not self.api_key:
            logger.error("SendGrid API 키를 찾을 수 없어 클라이언트 초기화를 건너뜁니다")
            raise ValueError("SendGrid API 키를 찾을 수 없다")
        self.client = SendGridAPIClient(self.api_key)

    def notify_task_completed(self, task: Task) -> None:
        """구성된 경우 완료된 작업에 대한 이메일 알림을 전송한다."""
        # 클라이언트나 이메일 미설정 시 조용히 건너뜀
        if not (self.client and self.notification_email):
            logger.warning(
                f"SendGrid not configured, skipping notification, task_id: {str(task.id)}"
            )
            return
        # API 키를 난독화하여 로그에 기록 (보안 고려)
        obfuscated_key = f"{self.api_key[:4]}...{self.api_key[-4:]}" if self.api_key else "None"
        logger.info(
            f"Attempting to send notification with SendGrid - "
            f"API Key: {obfuscated_key}, "
            f"Email: {self.notification_email}"
        )
        try:
            # SendGrid SDK를 사용한 이메일 구성 및 전송
            message = Mail(
                from_email=self.notification_email,
                to_emails=self.notification_email,
                subject=f"작업 완료: {task.title}",
                html_content=f"<strong>작업 '{task.title}'</strong>이(가) 완료되었습니다.",
            )
            response = self.client.send(message)
            logger.info(
                f"Notification sent successfully - task_id: {str(task.id)}, "
                f"notification_email: {self.notification_email}, "
                f"response: {response.status_code}"
            )
        except Exception as e:
            # 알림 실패가 비즈니스 작업을 방해하지 않도록 오류만 기록
            logger.error(
                f"Failed to send completion notification for task {str(task.id)}: {str(e)}"
            )

    def notify_task_high_priority(self, task: Task) -> None:
        """미구현 — 향후 높은 우선순위 작업 알림 확장 지점."""
        pass

    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """미구현 — 향후 마감일 임박 알림 확장 지점."""
        pass
