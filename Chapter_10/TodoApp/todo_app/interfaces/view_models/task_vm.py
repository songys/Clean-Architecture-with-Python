# 작업 뷰 모델 모듈
# - 프레젠터가 생성하고 UI(CLI/Web)에서 소비하는 표시용 데이터 구조
# - 불변(frozen) 객체로 뷰 계층에서 데이터 변경 방지
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TaskViewModel:
    """작업의 뷰 전용 표현.
    - 도메인 엔터티와 분리된 표시 전용 데이터
    - 각 필드는 이미 포맷된 문자열 (프레젠터가 변환)
    """
    id: str
    title: str
    description: str
    status_display: str  # 사람이 읽을 수 있는 상태
    priority_display: str  # 사람이 읽을 수 있는 우선순위
    due_date_display: Optional[str]  # 포맷된 날짜 문자열
    project_display: Optional[str]  # 가능한 경우 프로젝트 이름
    completion_info: Optional[str]  # 포맷된 완료 세부 정보
