# order_system/infrastructure/services/dummy_payment_service.py
# ──────────────────────────────────────────────────────────────
# 인프라 계층 - 더미 결제 서비스 구현체
# PaymentService 인터페이스의 테스트/데모용 구현체
# 실제 프로덕션에서는 Stripe, PayPal 등 외부 게이트웨이 호출로 교체
# → 의존성 역전 원칙 덕분에 도메인 코드 수정 없이 구현체만 교체 가능
# ──────────────────────────────────────────────────────────────
from ...domain.entities.order import Order
from ...domain.services.payment_service import PaymentService, PaymentResult


# 항상 결제 성공을 반환하는 더미 구현체
class DummyPaymentService(PaymentService):
    def process_payment(self, order: Order) -> PaymentResult:
        # 실제 구현에서는 외부 결제 게이트웨이를 호출함
        # 이 데모에서는 성공적인 결제를 시뮬레이션함
        return PaymentResult(success=True)
