# ============================================================
# OCP(개방-폐쇄 원칙) 위반 사례 - 리팩토링 전
# 새 도형을 추가할 때마다 AreaCalculator의 코드를 수정해야 하는 구조
# isinstance()로 타입을 일일이 확인하는 방식은 OCP 위반의 전형적 패턴
# ============================================================


# 사각형 클래스 - 가로, 세로 속성만 보유
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height


# 원 클래스 - 반지름 속성만 보유
class Circle:
    def __init__(self, radius):
        self.radius = radius


# OCP 위반: 새 도형 추가 시 이 클래스의 calculate_area 메서드를 반드시 수정해야 함
# isinstance()를 사용한 타입 분기 - 도형이 늘어날수록 if-elif 체인이 길어지는 문제
class AreaCalculator:
    def calculate_area(self, shape):
        if isinstance(shape, Rectangle):
            return shape.width * shape.height
        elif isinstance(shape, Circle):
            return 3.14 * shape.radius**2
        else:
            raise ValueError("지원되지 않는 도형")


# 사용법
rectangle = Rectangle(5, 4)
circle = Circle(3)

calculator = AreaCalculator()
print(f"사각형 면적: {calculator.calculate_area(rectangle)}")
print(f"원 면적: {calculator.calculate_area(circle)}")
