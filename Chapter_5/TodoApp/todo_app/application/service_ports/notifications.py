# todo_app/application/service_ports/notifications.py
"""
이 모듈은 외부 알림 서비스를 위한 알림 인터페이스(포트)를 정의한다.
"""
# 알림 포트(Port) 인터페이스 정의
# - 포트: 애플리케이션 계층이 외부 알림 서비스에 요구하는 기능의 추상 정의
# - 구체적인 알림 방식(이메일, SMS, 슬랙 등)은 인프라 계층의 어댑터가 구현
# - 유스케이스는 이 인터페이스에만 의존하여 외부 서비스와의 결합도를 최소화

from abc import ABC, abstractmethod

from todo_app.domain.entities.task import Task


# 작업 관련 알림 전송을 위한 추상 포트 인터페이스
# - 작업 완료, 높은 우선순위 설정, 마감일 임박 등 세 가지 알림 유형 정의
class NotificationPort(ABC):
    """작업 이벤트에 대한 알림을 전송하기 위한 인터페이스."""

    # 작업 완료 시 알림 전송
    @abstractmethod
    def notify_task_completed(self, task: Task) -> None:
        """작업이 완료되었을 때 알림을 전송한다."""
        pass

    # 높은 우선순위 작업 설정 시 알림 전송
    @abstractmethod
    def notify_task_high_priority(self, task: Task) -> None:
        """작업이 높은 우선순위로 설정되었을 때 알림을 전송한다."""
        pass

    # 마감일 임박 시 알림 전송 (남은 일수 정보 포함)
    @abstractmethod
    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """작업의 마감일이 다가올 때 알림을 전송한다."""
        pass
