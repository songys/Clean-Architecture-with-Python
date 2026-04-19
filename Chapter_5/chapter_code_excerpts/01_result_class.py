# Result 패턴(Result Pattern) 구현
# - 유스케이스 실행 결과를 성공(값)과 실패(에러) 중 하나로 표현하는 패턴
# - 예외(Exception) 대신 명시적 반환값으로 성공/실패를 구분하여 코드 가독성 향상

from dataclasses import dataclass
from typing import Any, Optional, Self

from todo_app.application.common.result import Error


# 불변 데이터 클래스로 정의한 유스케이스 실행 결과
@dataclass(frozen=True)
class Result:
    """유스 케이스 실행의 성공 또는 실패를 나타냄"""

    # 성공 시 반환할 값 (실패 시 None)
    value: Any = None
    # 실패 시 에러 정보 (성공 시 None)
    error: Optional[Error] = None

    # 에러가 없으면 성공으로 판단하는 속성
    @property
    def is_success(self) -> bool:
        return self.error is None

    # 성공 결과를 생성하는 팩토리 메서드
    @classmethod
    def success(cls, value: Any) -> Self:
        return cls(value=value)

    # 실패 결과를 생성하는 팩토리 메서드
    @classmethod
    def failure(cls, error: Error) -> Self:
        return cls(error=error)


"""
이 결과 패턴은 도메인 연산을 깔끔하게 조율할 수 있게 해준다. 다음 사용 예제를 살펴보자:

try:
    project = find_project(project_id)
   	task = create_task(task_details)
    project.add_task(task)
   	notify_stakeholders(task)
    return Result.success(TaskResponse.from_entity(task))
except ProjectNotFoundError:
   	return Result.failure(Error.not_found("Project", str(project_id)))
except ValidationError as e:
   	return Result.failure(Error.validation_error(str(e)))
"""
