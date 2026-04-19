# 어댑터 패턴을 활용한 서비스 변경 대응
# - 외부 서드파티 서비스의 인터페이스가 우리 시스템의 포트와 다를 때,
#   어댑터로 인터페이스 차이를 흡수하여 기존 코드 수정 없이 새 서비스를 연결하는 패턴
# - 핵심 비즈니스 로직 변경 없이 외부 서비스 교체가 가능한 유연한 구조

from uuid import UUID

from todo_app.application.service_ports.notifications import (
    NotificationPort,
)


# 외부 서드파티 알림 서비스 - 우리 시스템과 다른 인터페이스를 가진 외부 서비스
# - send_notification(payload) 형태의 자체 인터페이스 사용
class ModernNotificationService:
    """서로 다른 인터페이스를 가진 외부(서드파티) 알림 서비스"""

    def send_notification(self, payload: dict) -> None:
        # 최신 알림 서비스의 실제 구현
        pass


# 어댑터(Adapter) - 외부 서비스의 인터페이스를 우리 시스템의 포트에 맞게 변환
# - NotificationPort 인터페이스를 구현하여 유스케이스가 그대로 사용 가능
# - 내부적으로 ModernNotificationService의 send_notification을 호출하되,
#   포트에 정의된 notify_task_completed 형태로 래핑
class ModernNotificationAdapter(NotificationPort):
    """기존 애플리케이션의 알림 인터페이스에 맞게 최신 알림 서비스를 연결하기 위한 어댑터"""

    def __init__(self, modern_service: ModernNotificationService):
        self._service = modern_service

    # 포트의 메서드를 외부 서비스의 형식(payload 딕셔너리)으로 변환하여 호출
    def notify_task_completed(self, task_id: UUID) -> None:
        self._service.send_notification(
            {"type": "TASK_COMPLETED", "taskId": str(task_id)}
        )
