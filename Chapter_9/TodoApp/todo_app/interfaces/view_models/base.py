from typing import Generic, TypeVar, Optional
from dataclasses import dataclass

T = TypeVar("T")  # 성공 값의 제네릭 타입 파라미터


# 오류 정보를 뷰에 전달하기 위한 불변 뷰 모델
@dataclass(frozen=True)
class ErrorViewModel:
    """선택적 오류 코드가 포함된 오류를 나타낸다.

    Attributes:
        message: 사람이 읽을 수 있는 오류 메시지
        code: 프로그래밍적 오류 처리를 위한 선택적 오류 코드
    """

    message: str
    code: Optional[str] = None


# 컨트롤러에서 뷰(라우트/CLI)로 결과를 전달하기 위한 Either 패턴 구현체
# 성공 시 뷰 모델, 실패 시 ErrorViewModel을 포함
@dataclass
class OperationResult(Generic[T]):
    """값으로 성공하거나 오류로 실패할 수 있는 작업의 결과를 나타낸다.

    이 클래스는 Either 패턴을 구현하며, 결과는 성공 또는 실패 중 하나만 가능하고
    둘 다이거나 둘 다 아닌 경우는 없다. 이는 명시적인 오류 처리와 None 검사
    회피에 도움이 된다. 또한 Mypy 및 기타 정적 타입 검사기를 통한 타입 검사를 가능하게 한다.

    Type Parameters:
        T: 성공 값의 타입

    Attributes:
        _success: 작업이 성공한 경우의 성공 값
        _error: 작업이 실패한 경우의 오류 상세
    """

    _success: Optional[T] = None
    _error: Optional[ErrorViewModel] = None

    def __init__(self, success: Optional[T] = None, error: Optional[ErrorViewModel] = None):
        """성공 값 또는 오류 중 하나로 결과를 초기화한다.

        Args:
            success: 작업이 성공한 경우의 성공 값
            error: 작업이 실패한 경우의 오류 상세

        Raises:
            ValueError: 성공과 오류 모두 제공되지 않거나 둘 다 제공된 경우
        """
        if (success is None and error is None) or (success is not None and error is not None):
            raise ValueError("성공 또는 오류 중 하나만 제공되어야 하며, 둘 다 제공될 수 없습니다")
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
            raise ValueError("오류 결과에서 성공 값에 접근할 수 없습니다")
        return self._success

    @property
    def error(self) -> ErrorViewModel:
        """오류 상세를 반환한다.

        Raises:
            ValueError: 성공 결과에서 오류 값에 접근하는 경우
        """
        if self._error is None:
            raise ValueError("성공 결과에서 오류 값에 접근할 수 없습니다")
        return self._error

    @classmethod
    def succeed(cls, value: T) -> "OperationResult[T]":
        """주어진 값으로 성공 결과를 생성한다.

        Args:
            value: 성공 값

        Returns:
            성공을 나타내는 새 OperationResult 인스턴스
        """
        return cls(success=value)

    @classmethod
    def fail(cls, message: str, code: Optional[str] = None) -> "OperationResult[T]":
        """주어진 오류 메시지와 선택적 코드로 실패 결과를 생성한다.

        Args:
            message: 오류 메시지
            code: 선택적 오류 코드

        Returns:
            실패를 나타내는 새 OperationResult 인스턴스
        """
        return cls(error=ErrorViewModel(message, code))
