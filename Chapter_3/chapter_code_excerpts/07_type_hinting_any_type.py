# === Any 타입 — 모든 타입을 허용하는 특수 타입 힌트 ===
# 타입을 알 수 없거나 매우 다양한 외부 시스템과 연동할 때 사용
# 클린 아키텍처에서는 최후의 수단 — 가능하면 구체적인 타입 사용 권장
from typing import Any


# data: Any — 문자열, 정수, 딕셔너리 등 어떤 타입이든 수용 가능
# 로깅 같은 범용 유틸리티 함수에서 사용하는 Any 타입의 적절한 사용 사례
def log_data(data: Any) -> None:
    print(f"Logged: {data}")


# 사용법 — 다양한 타입의 데이터를 동일한 함수로 처리
log_data("문자열")
log_data(42)
log_data({"key": "value"})
