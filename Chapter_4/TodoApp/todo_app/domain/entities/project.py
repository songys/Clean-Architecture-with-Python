# 프로젝트(Project) 엔티티: 여러 Task를 관리하는 애그리게이트 루트(Aggregate Root)
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from todo_app.domain.entities.entity import Entity
from todo_app.domain.entities.task import Task


@dataclass
class Project(Entity):
    name: str                                           # 프로젝트 이름
    description: str = ""                               # 프로젝트 설명 (선택 사항)
    # 내부 작업 딕셔너리: UUID를 키로 사용하여 O(1) 조회 성능 보장
    # 언더스코어(_) 접두사로 외부 직접 접근 방지 (캡슐화)
    _tasks: dict[UUID, Task] = field(default_factory=dict, init=False)

    # 작업 추가: 애그리게이트 루트를 통해서만 작업 추가 가능
    def add_task(self, task: Task) -> None:
        self._tasks[task.id] = task

    # 작업 제거: 존재하지 않는 ID도 안전하게 처리 (pop의 기본값 None)
    def remove_task(self, task_id: UUID) -> None:
        self._tasks.pop(task_id, None)

    # 작업 조회: ID로 특정 작업 검색 (없으면 None 반환)
    def get_task(self, task_id: UUID) -> Optional[Task]:
        return self._tasks.get(task_id)

    # 작업 목록 프로퍼티: 내부 딕셔너리를 리스트로 변환하여 반환
    # 불변 복사본 반환으로 외부에서의 내부 상태 직접 변경 방지
    @property
    def tasks(self) -> list[Task]:
        return list(self._tasks.values())
