# 프로젝트 뷰 모델 모듈
# - 프로젝트 및 작업 목록의 표시용 데이터 구조
# - 불변(frozen) 객체로 뷰 계층에서 데이터 변경 방지
from dataclasses import dataclass
from typing import Optional

from todo_app.interfaces.view_models.task_vm import TaskViewModel


@dataclass(frozen=True)
class ProjectViewModel:
    """프로젝트의 뷰 전용 표현.
    - 프로젝트 정보와 소속 작업들의 뷰 모델을 함께 포함
    """

    id: str
    name: str
    description: str
    project_type: str
    status_display: str
    task_count: int
    completed_task_count: int
    completion_info: Optional[str]
    tasks: list[TaskViewModel]


@dataclass(frozen=True)
class ProjectCompletionViewModel:
    """프로젝트 완료의 뷰 전용 표현."""

    project_id: str
    completion_notes: Optional[str]


@dataclass(frozen=True)
class ProjectListItemViewModel:
    """계층적 목록에서의 프로젝트 뷰 모델."""

    id: str
    name: str
    is_inbox: bool
    tasks: list["TaskListItemViewModel"]


@dataclass(frozen=True)
class TaskListItemViewModel:
    """계층적 목록에서의 작업 뷰 모델."""

    id: str
    letter_id: str  # 'a', 'b' 등
    title: str
    status_display: str
    priority_display: str
    due_date_display: Optional[str]
