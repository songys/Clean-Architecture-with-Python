# 의존성 규칙(Dependency Rule) 위반 사례 모음
# 도메인 계층이 외부 계층(DB, UI)에 직접 의존하면 안 되는 이유를 보여주는 반면교사
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from todo_app.domain.entities.entity import Entity
from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import (
    TaskStatus,
    Deadline,
    Priority,
)


# 인프라 계층의 DB 연결 클래스 (외부 관심사)
class DbConnection:
    pass


# 프레젠테이션 계층의 UI 컴포넌트 클래스 (외부 관심사)
class UiComponent:
    pass


# --- 위반 사례 1: 도메인 엔티티가 데이터베이스에 직접 의존 ---
@dataclass
class TaskWithDatabase:
    """
    DB 연결을 통한 의존성 규칙 위반
    """

    title: str
    description: str
    db: DbConnection  # 의존성 규칙 위반 - 도메인이 인프라에 직접 의존
    due_date: Optional[Deadline] = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = field(default=TaskStatus.TODO, init=False)

    def mark_as_complete(self):
        self.status = TaskStatus.DONE
        self.db.update(self)  # 도메인 로직 안에서 DB 직접 호출 - 테스트 및 교체 어려움


# --- 위반 사례 2: 도메인 엔티티가 UI 컴포넌트에 직접 의존 ---
@dataclass
class ProjectWithUI(Entity):
    """
    UI 관심사를 통한 의존성 규칙 위반
    """

    name: str
    ui: UiComponent  # 의존성 규칙 위반 - 도메인이 프레젠테이션에 직접 의존
    description: str = ""
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)

    def add_task(self, task: Task):
        self._tasks[task.id] = task
        self.ui.refresh()  # 의존성 규칙 위반 - 도메인 로직 안에서 UI 직접 조작
