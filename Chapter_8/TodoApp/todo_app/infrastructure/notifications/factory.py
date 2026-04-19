from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.infrastructure.notifications.recorder import NotificationRecorder
from todo_app.infrastructure.notifications.sendgrid import SendGridNotifier
from todo_app.infrastructure.config import Config

# 팩토리 패턴: 설정에 따라 적절한 알림 서비스 구현체를 선택하여 생성
# SendGrid 미설정 시 NotificationRecorder(콘솔 출력)로 자동 폴백
def create_notification_service() -> NotificationPort:
    """
    구성에 따라 적절한 알림 서비스를 생성한다.
    SendGrid가 구성되지 않은 경우 NotificationRecorder로 폴백한다.
    """
    api_key = Config.get_sendgrid_api_key()
    notification_email = Config.get_notification_email()
    
    if api_key and notification_email:
        return SendGridNotifier()
    
    return NotificationRecorder()