# 알림 서비스 팩토리
# - 환경 설정에 따라 실제 SendGrid 또는 기록용 레코더를 자동 선택
# - 인터페이스(NotificationPort)를 반환하여 호출자는 구현 세부사항에 무관
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.infrastructure.notifications.recorder import NotificationRecorder
from todo_app.infrastructure.notifications.sendgrid import SendGridNotifier
from todo_app.infrastructure.config import Config

def create_notification_service() -> NotificationPort:
    """
    설정에 따라 적절한 알림 서비스를 생성한다.
    SendGrid API 키와 이메일이 설정된 경우 실제 이메일 발송,
    그렇지 않으면 NotificationRecorder로 폴백한다.
    """
    api_key = Config.get_sendgrid_api_key()
    notification_email = Config.get_notification_email()

    if api_key and notification_email:
        return SendGridNotifier()

    return NotificationRecorder()
