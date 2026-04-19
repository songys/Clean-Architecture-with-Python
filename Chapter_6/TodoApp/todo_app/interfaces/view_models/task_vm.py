from dataclasses import dataclass
from typing import Optional


# 프레젠터가 도메인 데이터를 화면에 바로 표시할 수 있는 형태로 변환하여 담는 뷰 모델
# - frozen=True로 불변성 보장 - 뷰가 데이터를 실수로 변경하는 것을 방지
# - 모든 표시 필드가 이미 형식화된 문자열이므로 뷰(UI)에서 추가 변환 없이 바로 사용 가능
@dataclass(frozen=True)
class TaskViewModel:
    """화면(UI) 표시를 위한 작업 전용 표현 모델"""
    id: str  # 작업의 고유 식별자 (UUID를 문자열로 변환)
    title: str  # 작업 제목
    description: str  # 작업 설명
    status_display: str  # 화면 표시용으로 미리 형식화해 둔 상태 (예: "[TODO]", "[DONE]")
    priority_display: str  # 화면 표시용으로 미리 형식화해 둔 우선순위 (예: "High", "Minor")
    due_date_display: Optional[str]  # 화면 표시용으로 미리 형식화되어 있는 마감일
    project_display: Optional[str]  # 화면 표시용 프로젝트 컨텍스트
    completion_info: Optional[str]  # 화면 표시용 완료 정보

