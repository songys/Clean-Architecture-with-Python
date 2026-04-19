# 작업(Task) 도메인 엔터티
# - Entity 기반 클래스를 상속하여 고유 ID와 동등성 비교 기능 획득
# - 작업의 상태 전이(TODO → IN_PROGRESS → DONE), 완료 처리, 기한 초과 확인 등 비즈니스 규칙 포함

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from todo_app.domain.entities.entity import Entity
from todo_app.domain.value_objects import (
    Deadline,
    Priority,
    TaskStatus,
)


# 작업 엔터티 - 완료해야 하는 개별 작업을 나타내는 도메인 객체
# - 상태 전이 규칙, 완료 처리, 기한 초과 확인 등 비즈니스 로직 포함
@dataclass
class Task(Entity):
    """완료해야 하는 작업."""

    title: str                              # 작업 제목
    description: str                        # 작업 설명
    due_date: Optional[Deadline] = None     # 마감일 (값 객체, 선택 사항)
    priority: Priority = Priority.MEDIUM    # 우선순위 (기본값: MEDIUM)
    # 아래 필드들은 init에서 제외되어 내부 상태 관리용으로만 사용
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)       # 초기 상태: TODO
    completed_at: Optional[datetime] = field(default=None, init=False)   # 완료 일시
    completion_notes: Optional[str] = field(default=None, init=False)    # 완료 메모
    project_id: Optional[UUID] = field(default=None, init=False)         # 소속 프로젝트 ID

    # 작업을 진행 중(IN_PROGRESS)으로 전이하는 메서드 - TODO 상태에서만 가능
    def start(self) -> None:
        """작업을 진행 중으로 표시한다."""
        if self.status != TaskStatus.TODO:
            raise ValueError("'TODO' 상태의 작업만 시작할 수 있습니다")
        self.status = TaskStatus.IN_PROGRESS

    # 작업을 완료(DONE)로 전이하는 메서드 - 이미 완료된 작업은 재완료 불가
    def complete(self, notes: Optional[str] = None) -> None:
        """
        작업을 완료로 표시한다.

        Args:
            notes: 선택적 완료 메모

        Raises:
            ValueError: 작업이 이미 완료된 경우
        """
        if self.status == TaskStatus.DONE:
            raise ValueError("작업이 이미 완료되었습니다")
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.completion_notes = notes

    # 마감일 초과 여부를 확인하는 메서드
    def is_overdue(self) -> bool:
        """작업이 기한을 초과했는지 확인한다."""
        return self.due_date is not None and self.due_date.is_overdue()
