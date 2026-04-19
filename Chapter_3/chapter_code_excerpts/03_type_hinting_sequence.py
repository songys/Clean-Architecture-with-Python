# === Sequence 타입 — 유연한 컬렉션 타입 힌트 ===
# Sequence는 리스트, 튜플 등 모든 시퀀스 타입을 포괄하는 추상 타입
# SOLID 원칙 중 리스코프 치환 원칙(LSP)과 개방-폐쇄 원칙(OCP)에 부합
from typing import Sequence


# Sequence[float]를 사용하여 리스트, 튜플 등 다양한 시퀀스 타입 수용 가능
# 특정 컬렉션 타입(list, tuple)에 의존하지 않는 유연한 인터페이스 설계
def calculate_total(items: Sequence[float]) -> float:
    return sum(items)


# 사용법 — 리스트와 튜플 모두 동일한 함수에서 처리 가능
print(calculate_total([1.0, 2.0, 3.0]))  # 리스트로 동작
print(calculate_total((4.0, 5.0, 6.0)))  # 튜플로도 동작
