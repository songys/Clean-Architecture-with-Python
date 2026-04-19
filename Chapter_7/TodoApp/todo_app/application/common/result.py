"""
이 모듈은 애플리케이션 계층의 핵심 오류 처리 및 결과 타입을 포함한다.
이 타입들은 모든 유스 케이스에서 성공과 실패 케이스를 일관되게 처리하는 방법을 제공한다.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, Generic, TypeVar, Self

T = TypeVar('T')  # Success type

class ErrorCode(Enum):
    """애플리케이션 계층에서 가능한 오류 코드의 열거형."""

    NOT_FOUND = "NOT_FOUND"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    UNAUTHORIZED = "UNAUTHORIZED"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Error:
    """
    유스 케이스 실행 중 발생한 오류를 나타낸다.

    이 클래스는 애플리케이션 계층 전반에 걸쳐 오류를 표준화된 방식으로 표현하며,
    특정 오류 타입(ErrorCode)과 추가 컨텍스트를 포함한다.

    Attributes:
        code: 발생한 오류 타입
        message: 사람이 읽을 수 있는 오류 설명
        details: 오류에 대한 선택적 추가 컨텍스트
    """

    code: ErrorCode
    message: str
    details: Optional[dict[str, Any]] = None

    @classmethod
    def not_found(cls, entity: str, entity_id: str) -> Self:
        """특정 엔터티에 대한 NOT_FOUND 오류 생성."""
        return cls(
            code=ErrorCode.NOT_FOUND,
            message=f"{entity} with id {entity_id} not found",
        )

    @classmethod
    def validation_error(cls, message: str) -> Self:
        """지정된 메시지로 VALIDATION_ERROR 생성."""
        return cls(code=ErrorCode.VALIDATION_ERROR, message=message)

    @classmethod
    def business_rule_violation(cls, message: str) -> Self:
        """지정된 메시지로 BUSINESS_RULE_VIOLATION 오류 생성."""
        return cls(code=ErrorCode.BUSINESS_RULE_VIOLATION, message=message)


@dataclass(frozen=True)
class Result(Generic[T]):
    """
    유스 케이스 실행 결과를 Either 타입으로 나타낸다.

    이 클래스는 작업의 결과를 캡슐화하며, T 타입의 값을 포함하는 성공이거나
    Error를 포함하는 실패 중 하나이다. 한 번에 하나의 상태만 존재하도록 강제하여
    작업 결과를 명확하고 타입 안전한 방식으로 처리한다.

    Attributes:
        _value: 성공한 경우 작업의 성공 값.
        _error: 실패한 경우 오류 정보.

    Methods:
        is_success: 결과가 성공이면 True, 실패이면 False를 반환한다.
        value: 결과가 성공이면 성공 값을 반환하고, 그렇지 않으면 ValueError를 발생시킨다.
        error: 결과가 실패이면 오류를 반환하고, 그렇지 않으면 ValueError를 발생시킨다.
        success: 성공 결과를 생성하는 클래스 메서드.
        failure: 실패 결과를 생성하는 클래스 메서드.
    """

    _value: Optional[T] = None
    _error: Optional[Error] = None

    def __post_init__(self):
        if (self._value is None and self._error is None) or \
           (self._value is not None and self._error is not None):
            raise ValueError("값 또는 오류 중 하나만 제공해야 하며, 둘 다 제공할 수 없다")

    @property
    def is_success(self) -> bool:
        """결과가 성공적인 작업인지 확인한다."""
        return self._value is not None

    @property
    def value(self) -> T:
        """성공 값을 가져온다. 결과가 오류이면 ValueError를 발생시킨다."""
        if self._value is None:
            raise ValueError("오류 결과에서 값에 접근할 수 없다")
        return self._value

    @property
    def error(self) -> Error:
        """오류 값을 가져온다. 결과가 성공이면 ValueError를 발생시킨다."""
        if self._error is None:
            raise ValueError("성공 결과에서 오류에 접근할 수 없다")
        return self._error

    @classmethod
    def success(cls, value: T) -> 'Result[T]':
        """주어진 값으로 성공 결과를 생성한다."""
        return cls(_value=value)

    @classmethod
    def failure(cls, error: Error) -> 'Result[T]':
        """주어진 오류로 실패 결과를 생성한다."""
        return cls(_error=error)
