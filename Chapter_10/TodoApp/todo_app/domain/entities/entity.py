# 도메인 계층의 엔터티 기본 클래스
# - 모든 엔터티의 공통 속성(ID)과 동일성 비교 로직을 정의
# - 엔터티는 고유한 식별자(ID)로 구분되는 도메인 객체
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Entity:
    # 'id' 필드에 대해 고유 UUID를 자동 생성;
    #   __init__ 메서드에서 제외됨
    id: UUID = field(default_factory=uuid4, init=False)

    # 엔터티의 동일성은 ID로만 판단 (값 객체와의 핵심 차이점)
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.id == other.id

    # 해시값도 ID 기반 (딕셔너리/세트에서 사용 가능)
    def __hash__(self) -> int:
        return hash(self.id)
