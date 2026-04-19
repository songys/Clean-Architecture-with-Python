from datetime import datetime, timezone
from typing import Optional
from todo_app.domain.value_objects import Priority, TaskStatus
from todo_app.interfaces.view_models.base import ErrorViewModel
from todo_app.application.dtos.project_dtos import CompleteProjectResponse, ProjectResponse
from todo_app.interfaces.view_models.project_vm import ProjectCompletionViewModel, ProjectViewModel
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.interfaces.presenters.base import ProjectPresenter, TaskPresenter
from todo_app.interfaces.view_models.task_vm import TaskViewModel


# CLI(터미널) 환경에 적합한 텍스트 기반 포맷을 적용하는 프레젠터 구현체
# 웹 프레젠터(web.py)와 동일한 추상 인터페이스(TaskPresenter)를 구현하되,
# 대괄호, 텍스트 색상 등 터미널 전용 포맷 사용
class CliTaskPresenter(TaskPresenter):
    """CLI 전용 작업 프레젠터."""

    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """CLI 표시용으로 작업을 포맷한다."""
        return TaskViewModel(
            id=task_response.id,
            title=task_response.title,
            description=task_response.description,
            # CLI 전용 대괄호 형식 (예: "[TODO]", "[DONE]")
            status_display=f"[{task_response.status.value}]",
            # CLI 전용 우선순위 표시 (Minor/Normal/High)
            priority_display=self._format_priority(task_response.priority),
            due_date_display=self._format_due_date(task_response.due_date),
            project_display=(
                f"Project: {task_response.project_id}" if task_response.project_id else ""
            ),
            completion_info=self._format_completion_info(
                task_response.completion_date, task_response.completion_notes
            ),
        )

    # CLI 전용 마감일 포맷팅 - "마감일:" 접두사 포함
    def _format_due_date(self, due_date: Optional[datetime]) -> str:
        """마감일을 포맷하고, 기한이 초과되었는지 표시한다."""
        if not due_date:
            return "마감일 없음"

        is_overdue = due_date < datetime.now(timezone.utc)
        date_str = due_date.strftime("%Y-%m-%d")
        return f"기한 초과 - 마감일: {date_str}" if is_overdue else f"마감일: {date_str}"

    # CLI 전용 완료 정보 포맷팅 - "미완료" 문자열 포함
    def _format_completion_info(
        self, completion_date: Optional[datetime], completion_notes: Optional[str]
    ) -> str:
        """메모가 있는 경우 포함하여 완료 정보를 포맷한다."""
        if not completion_date:
            return "미완료"

        base_info = f"{completion_date.strftime('%Y-%m-%d %H:%M')}에 완료"
        if completion_notes:
            return f"{base_info} - {completion_notes}"
        return base_info

    # CLI 전용 우선순위 매핑 (LOW->Minor, MEDIUM->Normal, HIGH->High)
    def _format_priority(self, priority: Priority) -> str:
        """CLI 표시용으로 우선순위를 포맷한다."""
        display_map = {
            Priority.LOW: "Minor",
            Priority.MEDIUM: "Normal",
            Priority.HIGH: "High",
        }
        return display_map[priority]

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        return ErrorViewModel(message=error_msg, code=code)


# CLI 전용 프로젝트 프레젠터 - 내부에 CliTaskPresenter를 포함하여
# 프로젝트의 작업 목록도 CLI 형식으로 변환
class CliProjectPresenter(ProjectPresenter):
    """CLI 전용 프로젝트 프레젠터."""

    def __init__(self):
        # 프로젝트 내 작업들도 CLI 형식으로 변환하기 위한 작업 프레젠터
        self.task_presenter = CliTaskPresenter()

    def present_project(self, project_response: ProjectResponse) -> ProjectViewModel:
        """CLI 표시용으로 프로젝트를 포맷한다."""
        # 각 작업을 CLI 전용 뷰 모델로 변환
        task_vms = [self.task_presenter.present_task(task) for task in project_response.tasks]

        # 완료된 작업 수 계산
        completed = sum(1 for task in project_response.tasks if task.status == TaskStatus.DONE)

        return ProjectViewModel(
            id=str(project_response.id),
            name=project_response.name,
            description=project_response.description,
            project_type=project_response.project_type.name,
            # CLI 전용 대괄호 형식 (예: "[ACTIVE]", "[COMPLETED]")
            status_display=f"[{project_response.status.name}]",
            task_count=len(project_response.tasks),
            completed_task_count=completed,
            completion_info=self._format_completion_info(project_response.completion_date),
            tasks=task_vms,
        )

    def present_completion(
        self, completion_response: CompleteProjectResponse
    ) -> ProjectCompletionViewModel:
        """CLI 표시용으로 프로젝트 완료를 포맷한다."""
        return ProjectCompletionViewModel(
            project_id=str(completion_response.id),
            completion_notes=completion_response.completion_notes,
        )

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        return ErrorViewModel(message=error_msg, code=code)

    def _format_completion_info(self, completion_date: Optional[datetime]) -> str:
        """CLI 표시용으로 완료 정보를 포맷한다."""
        if completion_date:
            return f"{completion_date.strftime('%Y-%m-%d %H:%M')}에 완료"
        return "미완료"
