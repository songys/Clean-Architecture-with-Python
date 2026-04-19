"""
이 모듈은 작업 연산을 위한 요청 및 응답 데이터 전송 객체(DTO)를 포함한다.
이 DTO들은 외부 계층과 애플리케이션 핵심부 사이의 데이터 변환을 처리한다.
"""
# 작업(Task) 관련 요청/응답 DTO 모음
# - 작업 완료, 생성, 우선순위 설정 요청과 작업 응답 DTO로 구성
# - 각 요청 DTO는 __post_init__으로 입력 검증, to_execution_params로 도메인 타입 변환 수행

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Self
from uuid import UUID

from todo_app.domain.entities.task import Task
from todo_app.domain.value_objects import Deadline, Priority, TaskStatus


# 작업 완료 요청 DTO - 작업 ID와 완료 메모의 유효성 검증
@dataclass(frozen=True)
class CompleteTaskRequest:
    """작업 완료를 위한 요청 데이터."""

    task_id: str
    completion_notes: Optional[str] = None

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.task_id.strip():
            raise ValueError("작업 ID는 필수입니다")
        if self.completion_notes and len(self.completion_notes) > 1000:
            raise ValueError("완료 메모는 1000자를 초과할 수 없습니다")
        try:
            UUID(self.task_id)
        except ValueError:
            raise ValueError("잘못된 작업 ID 형식입니다")

    # 문자열 task_id를 UUID 도메인 타입으로 변환하는 메서드
    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 매개변수로 변환한다."""
        return {
            "task_id": UUID(self.task_id),
            "completion_notes": self.completion_notes,
        }


# 새 작업 생성 요청 DTO - 제목, 설명, 마감일, 우선순위, 프로젝트 ID 검증
@dataclass(frozen=True)
class CreateTaskRequest:
    """새 작업 생성을 위한 요청 데이터."""

    title: str
    description: str
    due_date: Optional[str] = None
    priority: Optional[str] = None
    project_id: Optional[str] = None

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.title.strip():
            raise ValueError("제목은 필수입니다")
        if len(self.title) > 200:
            raise ValueError("제목은 200자를 초과할 수 없습니다")
        if len(self.description) > 2000:
            raise ValueError("설명은 2000자를 초과할 수 없습니다")
        if self.project_id:
            try:
                UUID(self.project_id)
            except ValueError:
                raise ValueError("잘못된 프로젝트 ID 형식입니다")

    # 문자열 형태의 입력 데이터를 도메인 타입(Deadline, Priority, UUID)으로 변환하는 메서드
    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 매개변수로 변환한다."""
        params = {
            "title": self.title.strip(),
            "description": self.description.strip(),
        }

        # 문자열 날짜를 Deadline 값 객체로 변환
        if self.due_date:
            params["deadline"] = Deadline(datetime.fromisoformat(self.due_date))

        # 문자열 우선순위를 Priority 열거형으로 변환
        if self.priority:
            params["priority"] = Priority[self.priority.upper()]

        # 문자열 프로젝트 ID를 UUID로 변환
        if self.project_id:
            params["project_id"] = UUID(self.project_id)

        return params


# 작업 응답 DTO - 도메인 엔터티(Task)를 외부에 전달하기 위한 경계 횡단 객체
@dataclass(frozen=True)
class TaskResponse:
    """도메인->애플리케이션 경계를 넘기 위한 응답 데이터."""

    id: str  # 경계 횡단 시 UUID를 문자열로 변환
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    due_date: Optional[datetime] = None
    project_id: Optional[str] = None
    completion_date: Optional[datetime] = None
    completion_notes: Optional[str] = None

    # 도메인 엔터티(Task)로부터 응답 DTO를 생성하는 팩토리 메서드
    @classmethod
    def from_entity(cls, task: Task) -> Self:
        """Task 엔터티로부터 응답을 생성한다."""
        return cls(
            id=str(task.id),  # 경계 횡단을 위한 기본 변환
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date.due_date if task.due_date else None,
            project_id=str(task.project_id) if task.project_id else None,
            completion_date=task.completed_at,
            completion_notes=task.completion_notes,
        )


# 작업 우선순위 설정 요청 DTO - 작업 ID와 우선순위 값의 유효성 검증
@dataclass(frozen=True)
class SetTaskPriorityRequest:
    """작업 우선순위 업데이트를 위한 요청 데이터."""

    task_id: str
    priority: str

    def __post_init__(self) -> None:
        """요청 데이터 검증"""
        if not self.task_id.strip():
            raise ValueError("작업 ID는 필수입니다")

        try:
            priority_value = self.priority.strip().upper()
            if not priority_value:
                raise ValueError
            if priority_value not in [p.name for p in Priority]:
                raise ValueError
        except (AttributeError, ValueError):
            raise ValueError(f"우선순위는 다음 중 하나여야 합니다: {', '.join(p.name for p in Priority)}")
        try:
            UUID(self.task_id)
        except ValueError:
            raise ValueError("잘못된 작업 ID 형식입니다")

    # 문자열 입력을 UUID와 Priority 열거형으로 변환하는 메서드
    def to_execution_params(self) -> dict:
        """요청 데이터를 유스 케이스 매개변수로 변환한다."""
        return {
            "task_id": UUID(self.task_id),
            "priority": Priority[self.priority.upper()],
        }
