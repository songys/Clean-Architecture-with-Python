from dataclasses import dataclass, field
from uuid import UUID, uuid4


# 모든 도메인 엔티티의 기본 클래스
# 엔티티는 고유 식별자(ID)로 구분되며, 값이 같아도 ID가 다르면 다른 객체로 취급
@dataclass
class Entity:
    # 'id' 필드에 대해 고유 UUID를 자동 생성;
    #   __init__ 메서드에서 제외
    id: UUID = field(default_factory=uuid4, init=False)

    # 동일성(Identity) 비교: ID가 같으면 같은 엔티티
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    # 해시값도 ID 기반으로 생성하여 set/dict에서 올바르게 동작
    def __hash__(self) -> int:
        return hash(self.id)
