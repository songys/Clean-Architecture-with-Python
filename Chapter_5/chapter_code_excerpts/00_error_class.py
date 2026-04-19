# 애플리케이션 계층에서 사용하는 표준 에러 클래스 정의
# - 유스케이스 실행 중 발생하는 오류를 일관된 형태로 표현하기 위한 구조
# - 에러 코드(ErrorCode)와 에러 정보(Error)로 구성

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Self


# 에러 유형을 열거형으로 정의한 에러 코드
# - 유스케이스 실행 결과에서 어떤 종류의 오류인지 구분하기 위한 분류 체계
class ErrorCode(Enum):
    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    # 필요에 따라 다른 에러 코드 추가


# 불변(frozen) 데이터 클래스로 정의한 에러 정보 객체
# - frozen=True: 생성 후 값 변경 불가, 안전한 에러 정보 전달 보장
@dataclass(frozen=True)
class Error:
    """표준화된 에러 정보"""

    # 에러의 종류를 나타내는 코드
    code: ErrorCode
    # 사람이 읽을 수 있는 에러 메시지
    message: str
    # 에러에 대한 추가 상세 정보 (선택 사항)
    details: Optional[dict[str, Any]] = None

    # "엔터티를 찾을 수 없음" 에러를 간편하게 생성하는 팩토리 메서드
    @classmethod
    def not_found(cls, entity: str, entity_id: str) -> Self:
        return cls(
            code=ErrorCode.NOT_FOUND,
            message=f"ID가 {entity_id}인 {entity}을(를) 찾을 수 없음",
        )

    # "검증 오류" 에러를 간편하게 생성하는 팩토리 메서드
    @classmethod
    def validation_error(cls, message: str) -> Self:
        return cls(code=ErrorCode.VALIDATION_ERROR, message=message)
