"""
이 모듈은 애플리케이션 계층의 핵심 오류 처리 및 결과 타입을 포함한다.
이 타입들은 모든 유스 케이스에 걸쳐 성공과 실패 케이스를 일관되게 처리하는 방법을 제공한다.
"""
# Result 패턴과 Error 코드 정의
# - 유스케이스 실행 결과를 예외가 아닌 명시적 반환값(Result)으로 표현
# - 모든 유스케이스에서 일관된 오류 처리를 위한 표준 에러 체계

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Self


# 애플리케이션 계층 전반에서 사용하는 에러 코드 열거형
# - 유스케이스 실행 실패 시 오류의 종류를 분류하기 위한 체계
class ErrorCode(Enum):
    """애플리케이션 계층에서 사용 가능한 에러 코드 열거형."""

    NOT_FOUND = "NOT_FOUND"                           # 엔터티를 찾을 수 없음
    VALIDATION_ERROR = "VALIDATION_ERROR"             # 입력 데이터 검증 실패
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"  # 비즈니스 규칙 위반
    UNAUTHORIZED = "UNAUTHORIZED"                     # 권한 없음
    CONFLICT = "CONFLICT"                             # 상태 충돌


# 불변(frozen) 데이터 클래스로 정의한 표준 에러 정보
# - 에러 코드, 메시지, 선택적 상세 정보를 하나의 객체로 캡슐화
@dataclass(frozen=True)
class Error:
    """
    유스 케이스 실행 중 발생한 오류를 나타낸다.

    이 클래스는 애플리케이션 계층 전반에 걸쳐 오류를 표준화된 방식으로 표현하며,
    구체적인 오류 유형(ErrorCode를 통해)과 추가 컨텍스트를 포함한다.

    Attributes:
        code: 발생한 오류의 유형
        message: 사람이 읽을 수 있는 오류 설명
        details: 오류에 대한 선택적 추가 컨텍스트
    """

    code: ErrorCode
    message: str
    details: Optional[dict[str, Any]] = None

    # "엔터티를 찾을 수 없음" 오류를 간편하게 생성하는 팩토리 메서드
    @classmethod
    def not_found(cls, entity: str, entity_id: str) -> Self:
        """특정 엔터티에 대한 NOT_FOUND 오류를 생성한다."""
        return cls(
            code=ErrorCode.NOT_FOUND,
            message=f"ID가 {entity_id}인 {entity}을(를) 찾을 수 없음",
        )

    # "검증 오류"를 간편하게 생성하는 팩토리 메서드
    @classmethod
    def validation_error(cls, message: str) -> Self:
        """지정된 메시지로 VALIDATION_ERROR를 생성한다."""
        return cls(code=ErrorCode.VALIDATION_ERROR, message=message)

    # "비즈니스 규칙 위반" 오류를 간편하게 생성하는 팩토리 메서드
    @classmethod
    def business_rule_violation(cls, message: str) -> Self:
        """지정된 메시지로 BUSINESS_RULE_VIOLATION 오류를 생성한다."""
        return cls(code=ErrorCode.BUSINESS_RULE_VIOLATION, message=message)


# 유스케이스 실행 결과를 나타내는 불변 데이터 클래스
# - 성공(value)과 실패(error)를 하나의 타입으로 표현하는 Result 패턴
# - 팩토리 메서드(success, failure)로 명확한 결과 생성
@dataclass(frozen=True)
class Result:
    """
    유스 케이스 실행의 결과를 나타내며, 성공 또는 실패 중 하나이다.

    이 클래스는 성공과 실패 결과를 모두 처리하는 방법을 제공하며,
    애플리케이션 계층 전반에 걸쳐 오류 처리가 명시적이고 일관되도록 보장한다.

    Attributes:
        value: 성공 값 (성공한 경우)
        error: 오류 상세 정보 (실패한 경우)
    """

    value: Any = None
    error: Optional[Error] = None

    # 에러가 없으면 성공으로 판단하는 속성
    @property
    def is_success(self) -> bool:
        """결과가 성공적인 연산을 나타내는지 확인한다."""
        return self.error is None

    # 성공 결과를 생성하는 팩토리 메서드
    @classmethod
    def success(cls, value: Any) -> Self:
        """주어진 값으로 성공 결과를 생성한다."""
        return cls(value=value)

    # 실패 결과를 생성하는 팩토리 메서드
    @classmethod
    def failure(cls, error: Error) -> Self:
        """주어진 오류로 실패 결과를 생성한다."""
        return cls(error=error)
