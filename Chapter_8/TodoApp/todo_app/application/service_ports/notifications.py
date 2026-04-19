# todo_app/application/service_ports/notifications.py
"""
이 모듈은 외부 알림 서비스를 위한 알림 인터페이스(포트)를 정의한다.
"""

from abc import ABC, abstractmethod

from todo_app.domain.entities.task import Task


# 알림 서비스 포트: 외부 알림 시스템에 대한 추상 인터페이스
# 구체 구현(SendGrid, 콘솔 출력 등)은 인프라 계층에서 제공
# 테스트 시 Mock으로 대체하여 알림 전송 여부만 검증 가능
class NotificationPort(ABC):
    """작업 이벤트에 대한 알림을 전송하기 위한 인터페이스."""

    @abstractmethod
    def notify_task_completed(self, task: Task) -> None:
        """작업이 완료되었을 때 알림을 전송한다."""
        pass

    @abstractmethod
    def notify_task_high_priority(self, task: Task) -> None:
        """작업이 높은 우선순위로 설정되었을 때 알림을 전송한다."""
        pass

    @abstractmethod
    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """작업의 마감일이 다가올 때 알림을 전송한다."""
        pass
