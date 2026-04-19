# ============================================================
# OCP(개방-폐쇄 원칙) 적용 후 - 리팩토링 완료
# 추상 클래스(Shape)와 다형성을 활용하여 확장에 열려 있고 수정에 닫힌 구조
# 새 도형 추가 시 기존 코드를 전혀 변경하지 않아도 되는 설계
# ============================================================

import math
from abc import ABC, abstractmethod


# 모든 도형의 공통 인터페이스 역할을 하는 추상 기본 클래스
class Shape(ABC):
    @abstractmethod
    def area(self):
        """각 도형이 자신의 넓이 계산 방법을 직접 구현하도록 강제하는 추상 메서드"""
        pass


# Shape를 상속받아 자신만의 넓이 계산 로직을 구현한 사각형 클래스
class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


# Shape를 상속받아 자신만의 넓이 계산 로직을 구현한 원 클래스
class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius**2


# OCP 준수: AreaCalculator는 Shape 추상 타입에만 의존
# 새 도형이 추가되어도 이 클래스는 수정 불필요 (확장에 열려 있고 수정에 닫힘)
class AreaCalculator:
    def calculate_area(self, shape: Shape):
        return shape.area()


# 사용법
rectangle = Rectangle(5, 4)
circle = Circle(3)

calculator = AreaCalculator()
print(f"사각형 면적: {calculator.calculate_area(rectangle)}")
print(f"원 면적: {calculator.calculate_area(circle)}")


# OCP의 장점: AreaCalculator 수정 없이 새 도형(삼각형) 추가
class Triangle(Shape):
    def __init__(self, base, height):
        self.base = base
        self.height = height

    def area(self):
        return 0.5 * self.base * self.height


triangle = Triangle(6, 4)
# 기존 calculator 인스턴스를 그대로 사용 가능 - OCP 덕분에 무수정 확장
print(f"삼각형 면적: {calculator.calculate_area(triangle)}")
