# === Union과 Optional 타입 — 여러 타입 또는 None을 허용하는 타입 힌트 ===
# 클린 아키텍처의 계층 경계에서 다양한 타입이나 선택적 값 처리에 유용
from typing import Union, Optional


# Union[str, int] — str 또는 int 중 하나를 매개변수로 받을 수 있음을 명시
# 파이썬 3.10+에서는 str | int 구문으로 대체 가능
def process_input(data: Union[str, int]) -> str:
    return str(data)


# Optional[int]는 Union[int, None]과 동일 — 값이 있거나 None일 수 있음을 표현
# Optional[str] 반환 타입 — 사용자를 찾으면 문자열, 못 찾으면 None 반환
def find_user(user_id: Optional[int] = None) -> Optional[str]:
    if user_id is None:
        return None
    # ... 사용자 검색 로직 ...
    return "User found"


# 사용법
result1 = process_input("Hello")  # str로 동작
result2 = process_input(42)  # int로 동작
user = find_user()  # 선택적 매개변수
