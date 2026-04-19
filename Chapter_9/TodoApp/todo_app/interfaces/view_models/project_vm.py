from dataclasses import dataclass
from typing import Optional

from todo_app.interfaces.view_models.task_vm import TaskViewModel


# 프레젠터가 생성하고 뷰(템플릿/CLI)에 전달하는 프로젝트 뷰 모델
# frozen=True로 불변 보장 - 뷰에서 데이터 변경 방지
@dataclass(frozen=True)
class ProjectViewModel:
    """프로젝트의 뷰 전용 표현."""

    id: str
    name: str
    description: str
    project_type: str
    status_display: str
    task_count: int
    completed_task_count: int
    completion_info: Optional[str]
    tasks: list[TaskViewModel]


# 프로젝트 완료 시 표시할 정보를 담는 뷰 모델
@dataclass(frozen=True)
class ProjectCompletionViewModel:
    """프로젝트 완료의 뷰 전용 표현."""

    project_id: str
    completion_notes: Optional[str]


# 계층적 프로젝트-작업 목록 표시를 위한 뷰 모델
@dataclass(frozen=True)
class ProjectListItemViewModel:
    """계층적 목록에서의 프로젝트 뷰 모델."""

    id: str
    name: str
    is_inbox: bool
    tasks: list["TaskListItemViewModel"]


# 프로젝트 목록 내 개별 작업 항목을 위한 뷰 모델
@dataclass(frozen=True)
class TaskListItemViewModel:
    """계층적 목록에서의 작업 뷰 모델."""

    id: str
    letter_id: str  # 'a', 'b' 등
    title: str
    status_display: str
    priority_display: str
    due_date_display: Optional[str]
