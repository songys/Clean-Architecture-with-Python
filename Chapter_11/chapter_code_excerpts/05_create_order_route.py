# order_system/domain/repositories/order_repository.py
# ──────────────────────────────────────────────────────────────
# 2단계: 변환 경계 식별
# 레거시 create_order() 라우트 핸들러의 책임 분석 결과,
# 주문 생성 프로세스가 입력 검증 → 재고 확인 → 결제 처리 → 주문 저장이라는
# 명확한 단계로 나뉘어 변환의 좋은 출발점
# ──────────────────────────────────────────────────────────────
from order_system.domain.entities.order import Order
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID


# 주문 저장소 인터페이스
# 코드 수정 전 먼저 회귀 테스트를 구축하여 기존 동작의 안전망 확보 필요
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


