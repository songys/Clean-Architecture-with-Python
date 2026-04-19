"""
아키텍처 경계에서는 성공한 작업과 실패한 작업을 모두 처리할 수 있는
명확하고 일관된 방법이 필요하다. 작업은 여러 이유로 실패할 수 있다.
유효하지 않은 입력, 비즈니스 규칙 위반, 시스템 오류 등이 그 원인이며,
각 타입의 실패는 외부 인터페이스에서 서로 다르게 처리해야 할 수 있다.
마찬가지로, 성공한 작업은 요청한 인터페이스에 적합한 형식으로 결과를
주어야 한다. 앞에서 보여준 컨트롤러 예제에서 이 메커니즘이 작동하는
모습을 확인했다.

class TaskController:

    def handle_create(
        self,
        title: str,
        description: str
    ) -> OperationResult[TaskViewModel]:
"""

from dataclasses import dataclass


# 성공 또는 실패를 명시적으로 표현하는 Either 패턴의 구현체
# - 컨트롤러가 결과를 반환할 때 성공/실패를 타입 안전하게 전달하는 수단
# - 외부 인터페이스(CLI, 웹 등)가 결과를 일관되게 처리할 수 있게 하는 공통 응답 형식
@dataclass
class OperationResult(Generic[T]):
    """컨트롤러 작업의 실행 결과를 표현하는 객체"""

    _success: Optional[T] = None  # 성공 시 뷰 모델을 담는 필드

    _error: Optional[ErrorViewModel] = None  # 실패 시 오류 정보를 담는 필드

    @classmethod
    def succeed(cls, value: T) -> "OperationResult[T]":
        """주어진 뷰 모델을 포함한 성공 결과를 생성"""

        return cls(_success=value)

    @classmethod
    def fail(cls, message: str, code: Optional[str] = None) -> "OperationResult[T]":
        """오류 정보를 포함한 실패 결과를 생성"""

        return cls(_error=ErrorViewModel(message, code))
