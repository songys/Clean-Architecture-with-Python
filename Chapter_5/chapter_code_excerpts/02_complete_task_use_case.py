# 작업 완료 유스케이스(Use Case) 구현 예제
# - 유스케이스: 애플리케이션 계층에서 비즈니스 흐름을 조율하는 단위
# - 리포지토리를 통해 도메인 객체를 가져오고, 도메인 로직을 실행한 뒤, 결과를 반환하는 구조

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from todo_app.application.common.result import Result, Error
from todo_app.application.repositories.task_repository import (
    TaskRepository,
)
from todo_app.domain.exceptions import (
    TaskNotFoundError,
    ValidationError,
)


# 불변 데이터 클래스로 정의한 작업 완료 유스케이스
# - 의존성(TaskRepository)을 생성자 주입으로 받아, 특정 구현에 결합되지 않는 구조
@dataclass(frozen=True)
class CompleteTaskUseCase:
    """작업을 완료로 표시하고 이해관계자에게 알리는 유스 케이스"""

    # 작업 저장소 인터페이스 (구체적인 DB 구현이 아닌 추상 인터페이스에 의존)
    task_repository: TaskRepository

    # 유스케이스의 핵심 실행 메서드 - Result 객체로 성공/실패를 명시적으로 반환
    def execute(
        self,
        task_id: UUID,
        completion_notes: Optional[str] = None,
    ) -> Result:

        try:
            # 입력 검증
            # 리포지토리에서 작업 조회 후 도메인 로직(complete) 실행
            task = self.task_repository.get(task_id)
            task.complete(notes=completion_notes)
            # 변경된 작업 상태를 리포지토리에 저장
            self.task_repository.save(task)

            # 단순화된 작업 데이터 반환
            return Result.success(
                {
                    "id": str(task.id),
                    "status": "completed",
                    "completion_date": task.completed_at.isoformat(),
                }
            )

        # 도메인 예외를 Result 실패로 변환하여 반환
        except TaskNotFoundError:
            return Result.failure(Error.not_found("Task", str(task_id)))
        except ValidationError as e:
            return Result.failure(Error.validation_error(str(e)))
