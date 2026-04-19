from dataclasses import dataclass
from uuid import UUID


# 삭제 연산의 결과를 나타내는 DTO - 삭제된 엔터티의 ID 보존
@dataclass(frozen=True)
class DeletionOutcome:
    """삭제 연산의 결과를 나타낸다."""

    entity_id: UUID

    def __str__(self) -> str:
        return f"Successfully deleted entity with ID: {self.entity_id}"
