# order_system/domain/repositories/order_repository.py
# ──────────────────────────────────────────────────────────────
# 도메인 계층 - OrderRepository 인터페이스 (추상 클래스)
# 구체적인 DB 기술에 의존하지 않는 저장소 계약
# 인프라 계층(SQLiteOrderRepository 등)이 이 인터페이스를 구현
# → 의존성 역전 원칙(DIP): 도메인이 인프라에 의존하지 않음
# ──────────────────────────────────────────────────────────────
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.order import Order


# 주문 저장소 인터페이스 (도메인 계층에 위치)
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
