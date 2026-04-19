# === 컨테이너 타입 힌팅 (list, dict 등) ===
# 파이썬 3.9+부터 내장 타입(list, dict, set 등)을 직접 타입 힌트에 사용 가능
# 클린 아키텍처에서 계층 간 데이터 구조를 명확히 정의할 때 유용

# items: list[str] — 문자열 리스트
# quantities: list[int] — 정수 리스트
# 반환값: dict[str, int] — 문자열 키와 정수 값으로 구성된 딕셔너리
def process_order(items: list[str], quantities: list[int]) -> dict[str, int]:
    # zip()으로 두 리스트를 묶어 딕셔너리 컴프리헨션으로 변환
    return {item: quantity for item, quantity in zip(items, quantities)}


# 사용법
order = process_order(["apple", "banana", "orange"], [2, 3, 1])
print(order)
# 출력: {'apple': 2, 'banana': 3, 'orange': 1}
