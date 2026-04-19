# 요청 DTO(Data Transfer Object) - 프로젝트 완료 요청
# - 외부(API 등)에서 들어오는 데이터를 검증하고, 유스케이스가 사용할 수 있는 형태로 변환하는 역할
# - 바깥 계층(API)의 문자열 데이터를 안쪽 계층(도메인)의 UUID 등 도메인 타입으로 변환하는 경계 객체

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from todo_app.domain.exceptions import ValidationError


# 불변 데이터 클래스로 정의한 프로젝트 완료 요청 DTO
# - frozen=True: 요청 데이터의 불변성 보장
@dataclass(frozen=True)
class CompleteProjectRequest:
    """프로젝트 완료 요청을 위한 데이터 구조"""

    project_id: str  # API에서 전달됨 (UUID로 변환될 예정)
    completion_notes: Optional[str] = None

    # 객체 생성 시 자동으로 입력 데이터를 검증하는 메서드
    # - 빈 ID, 과도한 메모 길이 등 잘못된 입력을 유스케이스 도달 전에 차단
    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.project_id.strip():
            raise ValidationError("프로젝트 ID는 필수입니다")

        if self.completion_notes and len(self.completion_notes) > 1000:
            raise ValidationError(
                "완료 메모 1000자 초과 불가능"
            )

    # 검증 완료된 데이터를 유스케이스 실행 매개변수로 변환하는 메서드
    # - 문자열 형태의 project_id를 UUID 도메인 타입으로 변환
    def to_execution_params(self) -> dict:
        """검증된 요청 데이터를 유스 케이스 매개변수로 변환"""
        return {
            "project_id": UUID(self.project_id),
            "completion_notes": self.completion_notes,
        }
