from typing import Generic, TypeVar, Optional
from dataclasses import dataclass

T = TypeVar("T")  # OperationResult의 성공 값 타입을 위한 제네릭 타입 변수


# 오류 정보를 화면 표시용으로 캡슐화하는 불변 뷰 모델
@dataclass(frozen=True)
class ErrorViewModel:
    """선택적 오류 코드를 포함하는 오류를 표현한다.

    Attributes:
        message: 사람이 읽을 수 있는 오류 메시지
        code: 프로그래밍 방식의 오류 처리를 위한 선택적 오류 코드
    """

    message: str
    code: Optional[str] = None


# 성공 또는 실패를 명시적으로 표현하는 Either 패턴의 인터페이스 계층 구현체
# - 컨트롤러가 결과를 반환할 때 성공/실패를 타입 안전하게 전달하는 수단
# - 외부 인터페이스(CLI, 웹 등)가 결과를 일관되게 처리할 수 있게 하는 공통 응답 형식
@dataclass
class OperationResult(Generic[T]):
    """값으로 성공하거나 오류로 실패할 수 있는 작업의 결과를 표현한다.

    이 클래스는 Either 패턴을 구현하며, 결과는 성공 또는 실패 중 하나만
    될 수 있고 둘 다이거나 둘 다 아닌 경우는 허용되지 않는다.
    이를 통해 명시적 오류 처리가 가능하고 None 확인을 피할 수 있다.
    또한 Mypy와 기타 정적 타입 검사기를 사용한 타입 확인이 가능하다.

    Type Parameters:
        T: 성공 값의 타입

    Attributes:
        _success: 작업이 성공한 경우의 성공 값
        _error: 작업이 실패한 경우의 오류 세부 정보
    """

    _success: Optional[T] = None
    _error: Optional[ErrorViewModel] = None

    def __init__(self, success: Optional[T] = None, error: Optional[ErrorViewModel] = None):
        """성공 값 또는 오류로 결과를 초기화한다.

        Args:
            success: 작업이 성공한 경우의 성공 값
            error: 작업이 실패한 경우의 오류 세부 정보

        Raises:
            ValueError: 성공과 오류가 모두 제공되거나 둘 다 제공되지 않은 경우
        """
        if (success is None and error is None) or (success is not None and error is not None):
            raise ValueError("성공 또는 오류 중 하나만 제공해야 하며, 둘 다 또는 둘 다 아닌 경우는 허용되지 않는다")
        self._success = success
        self._error = error

    @property
    def is_success(self) -> bool:
        """작업이 성공했는지 여부를 나타낸다."""
        return self._success is not None

    @property
    def success(self) -> T:
        """성공 값을 반환한다.

        Raises:
            ValueError: 오류 결과에서 성공 값에 접근하는 경우
        """
        if self._success is None:
            raise ValueError("오류 결과에서는 성공 값에 접근할 수 없다")
        return self._success

    @property
    def error(self) -> ErrorViewModel:
        """오류 세부 정보를 반환한다.

        Raises:
            ValueError: 성공 결과에서 오류 값에 접근하는 경우
        """
        if self._error is None:
            raise ValueError("성공 결과에서는 오류 값에 접근할 수 없다")
        return self._error

    @classmethod
    def succeed(cls, value: T) -> "OperationResult[T]":
        """주어진 값으로 성공 결과를 생성한다.

        Args:
            value: 성공 값

        Returns:
            성공을 나타내는 새로운 OperationResult 인스턴스
        """
        return cls(success=value)

    @classmethod
    def fail(cls, message: str, code: Optional[str] = None) -> "OperationResult[T]":
        """주어진 오류 메시지와 선택적 코드로 실패 결과를 생성한다.

        Args:
            message: 오류 메시지
            code: 선택적 오류 코드

        Returns:
            실패를 나타내는 새로운 OperationResult 인스턴스
        """
        return cls(error=ErrorViewModel(message, code))
