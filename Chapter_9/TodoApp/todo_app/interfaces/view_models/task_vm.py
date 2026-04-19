from dataclasses import dataclass
from typing import Optional


# 프레젠터가 생성하고 뷰(템플릿/CLI)에 전달하는 작업 뷰 모델
# 도메인 엔터티가 아닌 표시 전용 데이터 - 프레젠터가 인터페이스별 포맷을 적용한 결과
# frozen=True로 불변 보장 - 뷰에서 데이터 변경 방지
@dataclass(frozen=True)
class TaskViewModel:
    """작업의 뷰 전용 표현."""
    id: str
    title: str
    description: str
    status_display: str  # 프레젠터가 포맷한 상태 (CLI: "[TODO]", 웹: "TODO")
    priority_display: str  # 프레젠터가 포맷한 우선순위 (CLI: "Minor", 웹: "LOW")
    due_date_display: Optional[str]  # 프레젠터가 포맷한 날짜 문자열
    project_display: Optional[str]  # 가능한 경우 프로젝트 이름
    completion_info: Optional[str]  # 프레젠터가 포맷한 완료 상세

