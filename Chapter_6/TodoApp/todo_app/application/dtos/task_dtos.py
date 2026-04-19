"""
이 모듈은 작업(Task) 관련 요청 및 응답 데이터 전송 객체(DTO)를 포함한다.
이러한 DTO는 외부 계층과 애플리케이션 코어 간의 데이터 변환을 처리한다.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self
from uuid import UUID

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Deadline, Priority, TaskStatus


# 작업 완료를 위한 요청 DTO - 외부 입력을 유스케이스가 이해할 수 있는 형식으로 변환
# - frozen=True로 불변 객체 보장
# - __post_init__에서 입력 검증을 수행하여 유효하지 않은 데이터가 유스케이스에 도달하지 않도록 방지
@dataclass(frozen=True)
class CompleteTaskRequest:
    """작업을 완료하기 위한 요청 데이터"""

    task_id: str  # 완료할 작업의 ID (문자열 형태의 UUID)
    completion_notes: Optional[str] = None  # 선택적 완료 메모

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.task_id.strip():
            raise ValueError("Task ID is required")
        if self.completion_notes and len(self.completion_notes) > 1000:
            raise ValueError("Completion notes cannot exceed 1000 characters")
        try:
            UUID(self.task_id)
        except ValueError:
            raise ValueError("Invalid task ID format")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 실행에 필요한 파라미터로 변환"""
        return {
            "task_id": UUID(self.task_id),
            "completion_notes": self.completion_notes,
        }


# 작업 생성을 위한 요청 DTO - 외부 입력(문자열)을 도메인 타입으로 변환하는 경계 객체
@dataclass(frozen=True)
class CreateTaskRequest:
    """새로운 작업(Task)을 생성하기 위한 요청 데이터"""

    title: str  # 작업 제목 (필수)
    description: str  # 작업 설명 (필수)
    due_date: Optional[str] = None  # 마감일 (ISO 형식 문자열, 선택)
    priority: Optional[str] = None  # 우선순위 (문자열, 선택 - to_execution_params에서 열거형으로 변환)
    project_id: Optional[str] = None  # 소속 프로젝트 ID (문자열 형태의 UUID, 선택)

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.title.strip():
            raise ValueError("Title is required")
        if len(self.title) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        if len(self.description) > 2000:
            raise ValueError("Description cannot exceed 2000 characters")
        if self.project_id:
            try:
                UUID(self.project_id)
            except ValueError:
                raise ValueError("Invalid project ID format")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 실행에 필요한 파라미터로 변환"""
        params = {
            "title": self.title.strip(),
            "description": self.description.strip(),
        }

        if self.due_date:
            params["deadline"] = Deadline(datetime.fromisoformat(self.due_date))

        if self.priority:
            params["priority"] = Priority[self.priority.upper()]

        if self.project_id:
            params["project_id"] = UUID(self.project_id)

        return params


# 유스케이스 실행 결과를 외부 계층에 전달하기 위한 응답 DTO
# - 도메인 엔터티(Task)의 내부 구현을 노출하지 않고 필요한 데이터만 선별하여 전달
# - 프레젠터가 이 응답을 받아 뷰 모델로 변환
@dataclass(frozen=True)
class TaskResponse:
    """도메인->애플리케이션 경계를 넘기 위한 응답 데이터"""

    id: str  # 경계 교차를 위한 UUID -> 문자열 변환
    title: str
    description: str
    status: TaskStatus  # 도메인 값 객체 그대로 전달 (프레젠터가 형식화 담당)
    priority: Priority  # 도메인 값 객체 그대로 전달
    due_date: Optional[datetime] = None
    project_id: Optional[str] = None
    completion_date: Optional[datetime] = None
    completion_notes: Optional[str] = None

    # 도메인 엔터티로부터 응답 DTO를 생성하는 팩토리 메서드
    @classmethod
    def from_entity(cls, task: Task) -> Self:
        """Task 엔터티로부터 응답을 생성한다."""
        return cls(
            id=str(task.id),  # 경계 교차를 위한 기본 변환
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date.due_date if task.due_date else None,
            project_id=str(task.project_id) if task.project_id else None,
            completion_date=task.completed_at,
            completion_notes=task.completion_notes,
        )


# 작업 우선순위 변경을 위한 요청 DTO
@dataclass(frozen=True)
class SetTaskPriorityRequest:
    """작업 우선순위를 업데이트하기 위한 요청 데이터"""

    task_id: str  # 대상 작업의 ID (문자열 형태의 UUID)
    priority: str  # 새 우선순위 (문자열 - to_execution_params에서 열거형으로 변환)

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.task_id.strip():
            raise ValueError("Task ID is required")

        try:
            priority_value = self.priority.strip().upper()
            if not priority_value:
                raise ValueError
            if priority_value not in [p.name for p in Priority]:
                raise ValueError
        except (AttributeError, ValueError):
            raise ValueError(f"Priority must be one of: {', '.join(p.name for p in Priority)}")
        try:
            UUID(self.task_id)
        except ValueError:
            raise ValueError("Invalid task ID format")

    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 실행에 필요한 파라미터로 변환"""
        return {
            "task_id": UUID(self.task_id),
            "priority": Priority[self.priority.upper()],
        }
