# 리팩토링 전: 도메인 순수성이 위반된 Task 엔티티
# 비즈니스 로직(상태 변경)과 인프라 관심사(이메일 전송)가 혼재
from dataclasses import dataclass, field
from typing import Optional

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_objects import (
    Deadline,
    Priority,
    TaskStatus,
)


# 리팩토링 전 - 이메일 전송 로직이 도메인 엔티티 내부에 존재
@dataclass
class Task(Entity):
    title: str
    description: str
    due_date: Optional[Deadline] = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)

    def mark_as_complete(self):
        self.status = TaskStatus.DONE
        # 이메일 알림 전송 - 도메인 순수성 위반
        # 문제점: 도메인 엔티티가 이메일이라는 인프라 관심사에 직접 의존
        self.send_completion_email()

    # 인프라 관심사가 도메인 엔티티 안에 위치 - 단위 테스트 어려움의 원인
    def send_completion_email(self):
        # 이메일 알림을 전송하는 코드
        print(f"이메일 전송: 작업 '{self.title}' 완료")
