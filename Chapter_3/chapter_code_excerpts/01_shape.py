import math
from abc import ABC, abstractmethod


# === 타입 힌트를 활용한 도형(Shape) 계층 구조 ===
# 추상 기본 클래스(ABC)로 인터페이스를 정의하고,
# 타입 힌트로 계약(contract)을 명시하는 클린 아키텍처 패턴

# 추상 기본 클래스 — 모든 도형이 구현해야 할 인터페이스(계약) 정의
class Shape(ABC):
    # 반환 타입 float를 명시하여, 모든 하위 클래스가 동일한 계약을 따르도록 강제
    @abstractmethod
    def area(self) -> float:
        pass


# Shape 인터페이스를 구현하는 구체 클래스 — 직사각형
class Rectangle(Shape):
    # 생성자의 매개변수 타입(float)과 반환 타입(None)을 명시
    # -> None은 생성자가 값을 반환하지 않음을 명확히 표현
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    # 추상 메서드 area()의 구체적 구현 — 직사각형의 넓이 계산
    def area(self) -> float:
        return self.width * self.height


# Shape 인터페이스를 구현하는 구체 클래스 — 원
class Circle(Shape):
    def __init__(self, radius: float) -> None:

        self.radius = radius

    # 원의 넓이 공식: π × r²
    def area(self) -> float:
        return math.pi * self.radius**2


# Shape 추상 타입에 의존하는 클래스 — 의존성 역전 원칙(DIP) 적용 사례
# 구체 클래스(Rectangle, Circle)가 아닌 추상 인터페이스(Shape)에 의존
class AreaCalculator:
    # 매개변수 타입을 Shape(추상 클래스)로 지정하여 다형성 보장
    def calculate_area(self, shape: Shape) -> float:

        return shape.area()
