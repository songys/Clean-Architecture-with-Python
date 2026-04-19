# 7장의 CLI 프레젠터
# 터미널 환경에 적합한 텍스트 기반 포맷을 적용하는 CLI 전용 프레젠터 메서드
def present_task(self, task_response: TaskResponse) -> TaskViewModel:
    """CLI 표시를 위해 작업 포맷."""
    return TaskViewModel(
        id=task_response.id,
        title=task_response.title,
        status_display=f"[{task_response.status.value}]",  # CLI 전용 대괄호 형식
        priority_display=self._format_priority(task_response.priority),  # CLI 전용 색상 지정
    )
# 웹 프레젠터(06번 파일)와 비교하면, 동일한 TaskResponse를
# 각 인터페이스에 맞게 다르게 변환하는 것을 확인 가능
