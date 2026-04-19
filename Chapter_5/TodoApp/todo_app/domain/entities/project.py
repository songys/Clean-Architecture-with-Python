# 프로젝트 도메인 엔터티
# - Entity 기반 클래스를 상속하여 고유 ID와 동등성 비교 기능 획득
# - 여러 작업(Task)을 포함하고, 프로젝트 완료 시 관련 비즈니스 규칙 적용

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from todo_app.domain.entities.entity import Entity
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import (
    TaskStatus,
    ProjectStatus,
)


# 프로젝트 엔터티 - 여러 작업을 포함하는 도메인 객체
# - 상태 관리(ACTIVE → COMPLETED), 작업 추가/제거, 완료 처리 등 비즈니스 규칙 포함
@dataclass
class Project(Entity):
    """여러 작업을 포함하는 프로젝트."""

    name: str                   # 프로젝트 이름
    description: str = ""       # 프로젝트 설명 (기본값: 빈 문자열)
    # 아래 필드들은 init에서 제외되어 생성자에서 직접 설정 불가 (내부 상태 관리용)
    status: ProjectStatus = field(default=ProjectStatus.ACTIVE, init=False)  # 초기 상태: ACTIVE
    completed_at: Optional[datetime] = field(default=None, init=False)  # 완료 일시
    completion_notes: Optional[str] = field(default=None, init=False)   # 완료 메모
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)  # 작업 저장소 (ID → Task 매핑)

    def add_task(self, task: Task) -> None:
        """프로젝트에 작업을 추가한다."""
        if self.status == ProjectStatus.COMPLETED:
            raise ValueError("완료된 프로젝트에는 작업을 추가할 수 없습니다")
        self._tasks[task.id] = task
        task.project_id = self.id

    def remove_task(self, task_id: UUID) -> None:
        """프로젝트에서 작업을 제거한다."""
        if task := self._tasks.pop(task_id, None):
            task.project_id = None

    def get_task(self, task_id: UUID) -> Optional[Task]:
        """ID로 작업을 조회한다."""
        return self._tasks.get(task_id)

    @property
    def tasks(self) -> list[Task]:
        """프로젝트의 모든 작업을 조회한다."""
        return list(self._tasks.values())

    @property
    def incomplete_tasks(self) -> list[Task]:
        """프로젝트의 미완료 작업을 모두 조회한다."""
        return [task for task in self.tasks if task.status != TaskStatus.DONE]

    def mark_completed(self, notes: Optional[str] = None) -> None:
        """
        프로젝트를 완료로 표시한다.

        Args:
            notes: 선택적 완료 메모
        """
        self.status = ProjectStatus.COMPLETED
        self.completed_at = datetime.now()
        self.completion_notes = notes
