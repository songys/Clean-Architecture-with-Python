# todo_app/application/service_ports/notifications.py
"""
이 모듈은 외부 알림 서비스에 대한 알림 인터페이스(포트)를 정의한다.
"""

from abc import ABC, abstractmethod

from todo_app.domain.entities.task import Task


class NotificationPort(ABC):
    """작업 이벤트에 대한 알림 전송 인터페이스."""

    @abstractmethod
    def notify_task_completed(self, task: Task) -> None:
        """작업이 완료되었을 때 알림을 보낸다."""
        pass

    @abstractmethod
    def notify_task_high_priority(self, task: Task) -> None:
        """작업이 높은 우선순위로 설정되었을 때 알림을 보낸다."""
        pass

    @abstractmethod
    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """작업의 마감일이 다가올 때 알림을 보낸다."""
        pass
