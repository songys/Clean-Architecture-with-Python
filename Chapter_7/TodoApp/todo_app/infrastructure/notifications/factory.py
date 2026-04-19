# 알림 서비스 팩토리 — 환경 설정에 따라 적절한 구현체를 생성
from todo_app.application.service_ports.notifications import NotificationPort
from todo_app.infrastructure.notifications.recorder import NotificationRecorder
from todo_app.infrastructure.notifications.sendgrid import SendGridNotifier
from todo_app.infrastructure.config import Config

def create_notification_service() -> NotificationPort:
    """
    알림 서비스 팩토리 함수 — 구성에 따라 적절한 알림 서비스 생성.
    SendGrid API 키와 이메일이 모두 설정된 경우 SendGridNotifier 반환,
    그렇지 않으면 개발용 NotificationRecorder로 자동 폴백.
    """
    api_key = Config.get_sendgrid_api_key()
    notification_email = Config.get_notification_email()

    # SendGrid 인증 정보가 모두 있으면 실제 이메일 서비스 사용
    if api_key and notification_email:
        return SendGridNotifier()

    # 미설정 시 콘솔 출력 기반 알림 기록기로 폴백
    return NotificationRecorder()