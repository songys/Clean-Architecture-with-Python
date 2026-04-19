from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeletionOutcome:
    """삭제 작업의 결과를 나타낸다."""

    entity_id: UUID

    def __str__(self) -> str:
        return f"ID가 {self.entity_id}인 엔터티가 성공적으로 삭제되었다"
