# 리팩토링 후: 의존성 역전 원칙(DIP)을 적용한 알림 책임 분리
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_objects import (
    Deadline,
    Priority,
    TaskStatus,
)


# 리팩토링 후 Task 엔티티 - 순수한 비즈니스 로직만 포함
@dataclass
class Task(Entity):
    title: str
    description: str
    due_date: Optional[Deadline] = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)

    def mark_as_complete(self):
        self.status = TaskStatus.DONE
        # 여기서는 이메일을 전송하지 않음
        # 이제 이 책임은 외부 계층에 있음


# 추상 알림 인터페이스: 도메인 계층에 정의된 알림 계약
# 구체적인 알림 방식(이메일, SMS 등)은 외부 계층에서 결정
class TaskCompleteNotifier(ABC):
    @abstractmethod
    def notify_completion(self, task):
        pass


# 구체 구현: 외부(인프라) 계층에서 이메일 알림을 구현
# 도메인 엔티티는 이 구현체의 존재를 알지 못함 (의존성 역전)
class EmailTaskCompleteNotifier(TaskCompleteNotifier):
    def notify_completion(self, task):
        print(f"이메일 전송: 작업 '{task.title}' 완료")
