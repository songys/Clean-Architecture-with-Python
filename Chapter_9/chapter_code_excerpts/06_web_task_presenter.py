# HTML 템플릿 렌더링에 적합한 형식으로 데이터를 변환하는 웹 전용 프레젠터
# CLI 프레젠터(05번 파일)와 동일한 TaskPresenter 인터페이스를 구현하되,
# 웹 표시에 맞는 포맷 적용 (대괄호 없는 상태값, 날짜 포맷 등)
class WebTaskPresenter(TaskPresenter):

    def present_task(self, task_response: TaskResponse) -> TaskViewModel:
        """웹 표시를 위해 작업을 포맷한다."""
        return TaskViewModel(
            id=task_response.id,
            title=task_response.title,
            description=task_response.description,
            # CLI는 "[TODO]" 형식, 웹은 "TODO" 형식 - 인터페이스별 차이
            status_display=task_response.status.value,
            # CLI는 색상 코드 포함, 웹은 단순 텍스트 - HTML/CSS에서 스타일링 처리
            priority_display=task_response.priority.name,
            # 마감일을 웹 표시용으로 변환 (기한 초과 여부 포함)
            due_date_display=self._format_due_date(task_response.due_date),
            project_display=task_response.project_id,
            # 완료 정보를 웹 표시용으로 포맷팅
            completion_info=self._format_completion_info(
                task_response.completion_date, task_response.completion_notes
            ),
        )
