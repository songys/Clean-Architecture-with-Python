# === 수동 검증 vs 프레임워크 자동 검증 비교 ===
# 유효성 검증을 직접 구현하는 방식과 Pydantic을 활용하는 선언적 방식의 차이

# 작업 관리 - 수동 검증
# 내부 시스템용 모델: 개발자가 직접 검증 로직을 작성
class CreateTaskRequest:
    """새 작업 생성을 위한 요청 데이터"""

    title: str
    description: str

    # dataclass의 __post_init__을 활용한 수동 유효성 검증
    # 객체 생성 직후 자동으로 호출되어 필드 값을 검사하는 메서드
    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("제목은 비어 있을 수 없습니다")

    # 프레젠테이션 형식에서 도메인 형식으로의 변환 메서드
    def to_execution_params(self) -> dict:
        return {"title": self.title.strip(), "description": self.description.strip()}


# FastAPI/Pydantic - 자동 검증
# 프레임워크가 제공하는 선언적 검증 방식
from pydantic import BaseModel, Field


# Pydantic의 BaseModel을 상속하면 자동으로 타입 검증과 직렬화/역직렬화를 지원
# Field(..., min_length=1): "..."은 필수 필드를 의미, min_length로 최소 길이 제약 선언
# 수동 검증 코드 없이도 유효하지 않은 데이터를 자동으로 거부
class CreateTaskRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str
