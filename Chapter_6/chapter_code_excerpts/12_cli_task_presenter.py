from datetime import datetime, timezone
from typing import Optional


# CLI(명령행 인터페이스) 환경에 특화된 프레젠터의 구체적 구현
# - TaskPresenter 추상 인터페이스를 상속하여 CLI용 출력 형식을 정의
# - 도메인 응답의 각 필드를 CLI에서 읽기 좋은 문자열로 변환
# - 웹용 프레젠터를 별도로 구현하면 동일한 유스케이스로 다른 출력 형식 제공 가능
class CliTaskPresenter(TaskPresenter):
    """CLI 환경에 특화된 작업(Task) 프레젠터"""

    # 도메인 응답(TaskResponse)을 CLI 출력용 뷰 모델(TaskViewModel)로 변환하는 메서드
    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """작업 정보를 CLI 출력용 형식으로 변환"""

        return TaskViewModel(
            id=str(task_response.id),
            title=task_response.title,
            description=task_response.description,
            status_display=self._format_status(task_response.status),
            priority_display=self._format_priority(task_response.priority),
            due_date_display=self._format_due_date(task_response.due_date),
            project_display=self._format_project(task_response.project_id),
            completion_info=self._format_completion_info(
                task_response.completion_date, task_response.completion_notes
            ),
        )

    # 마감일을 형식화하고 기한 초과 여부를 시각적으로 표시하는 헬퍼 메서드
    def _format_due_date(self, due_date: Optional[datetime]) -> str:
        """마감일을 포맷하고, 기한 초과 여부를 표시"""

        if not due_date:

            return "No due date"

        # 현재 시각(UTC)과 비교하여 기한 초과 여부 판단
        is_overdue = due_date < datetime.now(timezone.utc)

        date_str = due_date.strftime("%Y-%m-%d")

        # 기한 초과 시 "OVERDUE" 접두사를 붙여 시각적으로 강조
        return f"OVERDUE - Due: {date_str}" if is_overdue else f"Due: {date_str}"

    def present_error(self, error_msg: str, code: Optional[str] = None) -> ErrorViewModel:
        """CLI 출력용 오류 메시지 형식화"""

        return ErrorViewModel(message=error_msg, code=code)
