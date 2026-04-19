"""
인터페이스 어댑터 패턴을 시연하기 위한 간단한 알림 구현.

이것은 프레임워크 및 드라이버 계층에 대한 선행적인 관점이다.

이 모듈은 실제 알림 서비스의 복잡성 없이 클린 아키텍처 원칙을
시연하기 위한 알림 인터페이스의 기본 구현을 제공한다. 다음을 보여준다:
- 애플리케이션 계층의 알림 인터페이스가 어떻게 구현되는지
- 알림 관심사가 비즈니스 로직과 어떻게 분리되는지
- 알림 이벤트의 기본 처리

이 구현은 7장에서 실제 알림 서비스로 대체될 것이며,
클린 아키텍처가 핵심 기능을 유지하면서 알림 메커니즘을 교체할 수
있도록 하는 방법을 시연한다.
"""

from dataclasses import dataclass
from todo_app.domain.entities.task import Task
from todo_app.application.service_ports.notifications import NotificationPort


@dataclass
class NotificationRecorder(NotificationPort):
    """
    인터페이스 어댑터 개념을 가르치기 위한 간단한 알림 구현.

    이 클래스는 클린 아키텍처에서 알림 게이트웨이가 어떻게 작동하는지 시연한다:
    - 애플리케이션 계층에서 정의한 인터페이스를 구현
    - 알림 세부 사항을 캡슐화 (이 경우 단순 출력)
    - 알림과 비즈니스 로직 간의 분리를 유지

    단순화되었지만, 이 구현은 실제 알림 서비스 구현에서
    사용될 패턴을 확립한다.
    """

    def __init__(self) -> None:
        self.completed_tasks = []
        self.high_priority_tasks = []
        self.deadline_warnings = []

    def notify_task_completed(self, task: Task) -> None:
        """작업 완료 알림을 기록한다."""
        message = f"Task {task.id} has been completed"
        print(f"NOTIFICATION: {message}")
        self.completed_tasks.append(task.id)

    def notify_task_high_priority(self, task: Task) -> None:
        """높은 우선순위 작업 알림을 기록한다."""
        message = f"Task {task.id} has been set to high priority"
        print(f"NOTIFICATION: {message}")
        self.high_priority_tasks.append(task.id)

    def notify_task_deadline_approaching(self, task: Task, days_remaining: int) -> None:
        """마감일 임박 알림을 기록한다."""
        message = f"Task {task.id} deadline approaching in {days_remaining} days"
        print(f"NOTIFICATION: {message}")
        self.deadline_warnings.append((task.id, days_remaining))
