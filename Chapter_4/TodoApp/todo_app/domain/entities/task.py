# 할 일(Task) 엔티티: 핵심 비즈니스 규칙을 캡슐화하는 도메인 객체
from dataclasses import dataclass, field
from typing import Optional

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_objects import (
    Deadline,
    Priority,
    TaskStatus,
)


@dataclass
class Task(Entity):
    title: str                                      # 작업 제목
    description: str                                # 작업 상세 설명
    due_date: Optional[Deadline] = None             # 마감일 (선택 사항)
    priority: Priority = Priority.MEDIUM            # 우선순위 (기본값: MEDIUM)
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)  # 상태 (기본값: TODO, 외부 설정 불가)

    # 작업 시작: TODO → IN_PROGRESS 상태 전이
    # 비즈니스 규칙 - TODO 상태에서만 시작 가능
    def start(self) -> None:
        if self.status != TaskStatus.TODO:
            raise ValueError("'TODO' 상태인 작업만 시작할 수 있습니다")
        self.status = TaskStatus.IN_PROGRESS

    # 작업 완료: 현재 상태 → DONE 상태 전이
    # 비즈니스 규칙 - 이미 완료된 작업의 중복 완료 방지
    def complete(self) -> None:
        if self.status == TaskStatus.DONE:
            raise ValueError("작업이 이미 완료되었습니다")
        self.status = TaskStatus.DONE

    # 마감일 초과 여부 확인 - Deadline 값 객체에 로직 위임
    def is_overdue(self) -> bool:
        return self.due_date is not None and self.due_date.is_overdue()
