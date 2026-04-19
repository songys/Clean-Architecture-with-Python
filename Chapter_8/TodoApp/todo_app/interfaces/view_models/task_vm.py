from dataclasses import dataclass
from typing import Optional


# 뷰 모델(ViewModel): UI 표시 전용 읽기 전용 데이터 객체
# 도메인 엔티티나 DTO와 달리 비즈니스 로직 없이 표시 데이터만 포함
# 프레젠터 테스트에서 이 객체의 필드값이 올바른 형식인지 검증
@dataclass(frozen=True)
class TaskViewModel:
    """작업의 뷰 전용 표현."""
    id: str
    title: str
    description: str
    status_display: str  # 사람이 읽을 수 있는 상태 (예: "[TODO]", "[DONE]")
    priority_display: str  # 사람이 읽을 수 있는 우선순위 (예: "High", "Normal")
    due_date_display: Optional[str]  # 포맷팅된 날짜 문자열
    project_display: Optional[str]  # 프로젝트 이름 (있는 경우)
    completion_info: Optional[str]  # 포맷팅된 완료 세부 정보

