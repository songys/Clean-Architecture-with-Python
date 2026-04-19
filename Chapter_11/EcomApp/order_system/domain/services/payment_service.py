# order_system/domain/services/payment_service.py
# ──────────────────────────────────────────────────────────────
# 도메인 계층 - PaymentService 인터페이스 (추상 클래스)
# 레거시에서 requests.post()로 직접 호출하던 외부 결제 서비스를
# 추상 인터페이스로 분리 → 테스트 시 DummyPaymentService로 교체 가능
# ──────────────────────────────────────────────────────────────
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from ..entities.order import Order


# 결제 처리 결과를 담는 데이터 클래스
@dataclass
class PaymentResult:
    success: bool                            # 결제 성공 여부
    error_message: Optional[str] = None      # 실패 시 오류 메시지


# 결제 서비스 인터페이스 (도메인 계층에 위치)
# 실제 결제 게이트웨이 호출은 인프라 계층의 구현체가 담당
class PaymentService(ABC):
    @abstractmethod
    def process_payment(self, order: Order) -> PaymentResult:
        """주문에 대한 결제를 처리"""
        pass
