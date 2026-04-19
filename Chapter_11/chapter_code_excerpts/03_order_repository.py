# ──────────────────────────────────────────────────────────────
# 1단계: 도메인 계층 - OrderRepository 인터페이스 (추상 클래스)
# 도메인이 필요로 하는 저장소 작업을 정의하되,
# 구체적인 DB 기술(SQLite, PostgreSQL 등)에는 의존하지 않는 추상화
# → 의존성 역전 원칙(DIP)의 핵심 구현
# ──────────────────────────────────────────────────────────────
from abc import ABC, abstractmethod
from order_system.domain.entities.order import Order
from typing import List, Optional
from uuid import UUID


# 주문 저장소 인터페이스
# 도메인 계층에 위치하며, 인프라 계층의 구현체가 이 인터페이스를 충족
class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        """주문을 리포지토리에 저장"""
        pass

    @abstractmethod
    def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """ID로 주문을 조회"""
        pass

    @abstractmethod
    def get_by_customer(self, customer_id: UUID) -> List[Order]:
        """고객의 모든 주문을 조회"""
        pass
