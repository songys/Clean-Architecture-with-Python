# 도메인 엔터티 기본 클래스 — 모든 엔터티의 공통 동작 정의
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Entity:
    """엔터티 기본 클래스 — UUID 기반 식별자 자동 생성 및 동등성 비교."""
    # 'id' 필드에 대해 고유한 UUID를 자동 생성;
    #   __init__ 메서드에서 제외됨
    id: UUID = field(default_factory=uuid4, init=False)

    def __eq__(self, other: object) -> bool:
        """엔터티 동등성 비교 — ID로만 판단 (속성값이 아닌 식별자 기반)"""
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        """해시 — 딕셔너리/집합에서 사용 가능하도록 ID 기반 해시"""
        return hash(self.id)
