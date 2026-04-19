from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.infrastructure.notifications.recorder import NotificationRecorder
from todo_app.infrastructure.notifications.sendgrid import SendGridNotifier
from todo_app.infrastructure.config import Config


# 알림 서비스 팩토리 - 환경 설정에 따라 적절한 구현체 자동 선택
# 의존성 역전 원칙의 실제 적용 - 추상 포트(NotificationPort) 타입으로 반환
def create_notification_service() -> NotificationPort:
    """
    구성에 따라 적절한 알림 서비스를 생성한다.
    SendGrid가 구성되지 않은 경우 NotificationRecorder로 폴백한다.
    """
    api_key = Config.get_sendgrid_api_key()
    notification_email = Config.get_notification_email()

    # SendGrid API 키와 이메일이 설정된 경우에만 실제 이메일 발송 구현체 사용
    if api_key and notification_email:
        return SendGridNotifier()

    # 미설정 시 콘솔 기록용 구현체로 자동 폴백
    return NotificationRecorder()