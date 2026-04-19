# todo_app/application/service_ports/notifications.py
"""
이 모듈은 외부 알림 서비스를 위한 알림 인터페이스(포트)를 정의한다.

애플리케이션 계층에 위치하며, 외부 알림 서비스(SendGrid 등)와의 계약을 명시.
구현 세부사항(이메일, SMS 등)은 인프라스트럭처 계층의 어댑터에서 결정.
"""

from abc import ABC, abstractmethod

from todo_app.domain.entities.task import Task


class NotificationPort(ABC):
    """작업 이벤트에 대한 알림 전송 포트(인터페이스) — 외부 서비스와의 경계."""

    @abstractmethod
    def notify_task_completed(self, task: Task) -> None:
        """작업 완료 시 알림 전송."""
        pass

    @abstractmethod
    def notify_task_high_priority(self, task: Task) -> None:
        """높은 우선순위 설정 시 알림 전송."""
        pass

    @abstractmethod
    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """마감일 임박 시 알림 전송 — 남은 일수 포함."""
        pass
