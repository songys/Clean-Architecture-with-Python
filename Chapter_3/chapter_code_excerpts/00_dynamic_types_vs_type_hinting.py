# === 동적 타입(Dynamic Typing) 시연 ===
# 파이썬의 동적 타입 특성 — 같은 변수에 다른 타입의 값 재할당 가능
x = 5  # x는 정수
x = "hello"  # 이제 x는 문자열이 됨

"""
이런 유연성 덕분에 빠르게 개발하고 표현력 있는 코드를 작성할 수 있지만,
주의하지 않으면 런타임 오류가 발생할 수 있다. 다음 예제를 살펴보자.
"""


# 타입 힌트가 없는 함수 — 매개변수 타입을 강제하지 않는 예시
def add_numbers(a, b):
    return a + b


result = add_numbers(5, 3)  # 정상 작동, 결과는 8
# 아래 호출은 int와 str의 덧셈 시도로 인한 TypeError 발생 사례
result = add_numbers(
    5, "3"
)  # TypeError 발생: + 연산자는 'int'와 'str' 타입을 지원하지 않음


"""
타입 힌트는 파이썬 3.5에서 도입되었으며, 개발자가 변수와 함수 매개변수뿐만 아니라
반환 값에 대해 예상되는 타입을 주석으로 달 수 있게 한다. 타입 힌트와 관련하여,
2장의 add_numbers 함수를 다시 살펴보자.
"""


# === 타입 힌트(Type Hinting) 적용 버전 ===
# 매개변수와 반환값에 타입을 명시하여 코드의 의도를 분명히 전달하는 방식
def add_numbers(a: int, b: int) -> int:
    return a + b


result = add_numbers(5, 3)  # 정상 작동, 결과는 8
# 타입 힌트 덕분에 IDE나 mypy 같은 정적 분석 도구가 실행 전에 타입 불일치 경고 가능
result = add_numbers(5, "3")  # IDE나 타입 검사기가 오류로 표시함
