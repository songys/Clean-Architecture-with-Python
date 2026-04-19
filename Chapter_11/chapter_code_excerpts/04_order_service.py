# ──────────────────────────────────────────────────────────────
# 1단계: 도메인 계층 - PaymentService 인터페이스 (추상 클래스)
# 레거시에서 requests.post()로 직접 호출하던 외부 결제 서비스를
# 추상 인터페이스로 분리한 결과물
# → 테스트 시 Mock 구현체로 교체 가능
# ──────────────────────────────────────────────────────────────
from order_system.domain.entities.order import Order
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID


# 주문 저장소 인터페이스 (03_order_repository.py와 동일 구조)
# 도메인 계층이 인프라(DB)에 의존하지 않도록 보장하는 추상화
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
