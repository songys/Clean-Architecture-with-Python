# === NewType — 기존 타입을 기반으로 별개의 타입을 생성하는 도구 ===
# 클린 아키텍처에서 도메인 개념을 명확히 구분할 때 유용
# 동일한 기본 타입(int)이지만 의미적으로 다른 값의 혼용 방지
from typing import NewType

# UserId와 ProductId 모두 int 기반이지만, 타입 검사기가 별개의 타입으로 인식
UserId = NewType("UserId", int)
ProductId = NewType("ProductId", int)


# 매개변수 타입을 UserId, ProductId로 구분하여 실수로 뒤바뀌는 것을 방지
def process_order(user_id: UserId, product_id: ProductId) -> None:
    print(f"Processing order for User {user_id} and Product {product_id}")


# 사용법
user_id = UserId(1)
product_id = ProductId(1)  # 기본 타입은 같은 int지만 별개의 타입
process_order(user_id, product_id)
# 아래 코드는 타입 오류가 발생함:
# process_order(product_id, user_id)  # UserId와 ProductId의 순서가 뒤바뀐 경우
