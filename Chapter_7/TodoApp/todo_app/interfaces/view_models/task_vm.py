from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TaskViewModel:
    """작업의 뷰 전용 표현."""
    id: str
    title: str
    description: str
    status_display: str  # 사람이 읽을 수 있는 상태
    priority_display: str  # 사람이 읽을 수 있는 우선순위
    due_date_display: Optional[str]  # 포맷된 날짜 문자열
    project_display: Optional[str]  # 사용 가능한 경우 프로젝트 이름
    completion_info: Optional[str]  # 포맷된 완료 세부 정보

