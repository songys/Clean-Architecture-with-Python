"""
웹 UI용 데이터 포맷팅을 위한 웹 전용 프레젠터.
- TaskPresenter/ProjectPresenter 추상 클래스의 웹 구현
- HTML 템플릿에서 사용하기 적합한 형식으로 데이터 포맷팅
- CLI 프레젠터와 동일한 인터페이스를 구현하되 출력 형식만 다름
"""

from datetime import datetime, timezone
from typing import Optional

from todo_app.domain.value_objects import TaskStatus
from todo_app.application.dtos.project_dtos import CompleteProjectResponse, ProjectResponse
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.interfaces.presenters.base import ProjectPresenter, TaskPresenter
from todo_app.interfaces.view_models.base import ErrorViewModel
from todo_app.interfaces.view_models.project_vm import ProjectCompletionViewModel, ProjectViewModel
from todo_app.interfaces.view_models.task_vm import TaskViewModel


class WebTaskPresenter(TaskPresenter):
    """웹 전용 작업 프레젠터."""

    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """웹 표시용으로 작업을 포맷한다."""
        return TaskViewModel(
            id=task_response.id,
            title=task_response.title,
            description=task_response.description,
            status_display=task_response.status.value,
            priority_display=task_response.priority.name,
            due_date_display=self._format_due_date(task_response.due_date),
            project_display=task_response.project_id,
            completion_info=self._format_completion_info(
                task_response.completion_date, task_response.completion_notes
            ),
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """웹 표시용으로 오류를 포맷한다."""
        return ErrorViewModel(message=error_msg, code=code or "ERROR")

    def _format_due_date(self, due_date: Optional[datetime]) -> str:
        """웹 표시용으로 마감일을 포맷한다."""
        if not due_date:
            return ""

        is_overdue = due_date < datetime.now(timezone.utc)
        date_str = due_date.strftime("%Y-%m-%d")
        return f"기한 초과: {date_str}" if is_overdue else date_str

    def _format_completion_info(
        self, completion_date: Optional[datetime], completion_notes: Optional[str]
    ) -> str:
        """웹 표시용으로 완료 정보를 포맷한다."""
        if not completion_date:
            return ""

        base_info = f"{completion_date.strftime('%Y-%m-%d %H:%M')}에 완료"
        if completion_notes:
            return f"{base_info}\n메모: {completion_notes}"
        return base_info


class WebProjectPresenter(ProjectPresenter):
    """웹 전용 프로젝트 프레젠터."""

    def __init__(self):
        self.task_presenter = WebTaskPresenter()

    def present_project(self, project_response: ProjectResponse) -> ProjectViewModel:
        """웹 표시용으로 프로젝트를 포맷한다."""
        return ProjectViewModel(
            id=project_response.id,
            name=project_response.name,
            description=project_response.description or "",
            project_type=project_response.project_type.name,
            status_display=project_response.status.value,
            task_count=len(project_response.tasks),
            completed_task_count=sum(
                1 for task in project_response.tasks if task.status == TaskStatus.DONE
            ),
            completion_info=self._format_completion_info(project_response.completion_date),
            tasks=[self.task_presenter.present_task(task) for task in project_response.tasks],
        )

    def present_completion(
        self, completion_response: CompleteProjectResponse
    ) -> ProjectCompletionViewModel:
        """웹 표시용으로 프로젝트 완료를 포맷한다."""
        return ProjectCompletionViewModel(
            project_id=completion_response.id,
            completion_notes=None,  # 또는 가능한 경우 completion_response에서 가져오기
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """웹 표시용으로 오류를 포맷한다."""
        return ErrorViewModel(message=error_msg, code=code or "ERROR")

    def _format_completion_info(self, completion_date: Optional[datetime]) -> str:
        """웹 표시용으로 완료 정보를 포맷한다."""
        if not completion_date:
            return ""
        return completion_date.strftime("%Y-%m-%d %H:%M")
