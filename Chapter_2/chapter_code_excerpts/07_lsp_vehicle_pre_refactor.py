# ============================================================
# LSP(리스코프 치환 원칙) 위반 사례 - 리팩토링 전
# 부모 클래스(Vehicle)를 자식 클래스(ElectricCar)로 대체했을 때
# 예상과 다른 동작이 발생하는 문제
# LSP: 자식 클래스는 부모 클래스를 대체해도 프로그램이 올바르게 동작해야 한다는 원칙
# ============================================================


# 내연기관 차량 기준으로 설계된 기본 클래스
class Vehicle:
    def __init__(self, fuel_capacity: float):
        self._fuel_capacity = fuel_capacity
        self._fuel_level = fuel_capacity  # 초기 연료량 = 최대 용량

    def fuel_level(self) -> float:
        return self._fuel_level

    def consume_fuel(self, distance: float) -> None:
        fuel_consumed = distance / 10  # 단순화를 위해 1리터당 10km 가정
        if self._fuel_level - fuel_consumed < 0:
            raise ValueError("거리를 이동하기에 충분한 연료가 없습니다")
        self._fuel_level -= fuel_consumed


# LSP 위반: ElectricCar가 Vehicle을 상속하지만 연료 소비 방식이 근본적으로 다름
# 전기차는 "연료"가 아닌 "전력"을 사용하므로 부모 클래스의 가정과 충돌
class ElectricCar(Vehicle):
    def __init__(self, battery_capacity: float):
        super().__init__(battery_capacity)

    # 부모의 consume_fuel을 오버라이드하지만, 소비율이 다름 (1kWh당 5km vs 1리터당 10km)
    # 결과적으로 drive_vehicle 함수에서 "리터" 단위로 출력하지만 실제로는 "kWh" 값
    def consume_fuel(self, distance: float) -> None:
        energy_consumed = distance / 5  # 단순화를 위해 1kWh당 5km 가정
        if self._fuel_level - energy_consumed < 0:
            raise ValueError("해당 거리를 주행할 만큼의 전력이 부족합니다")
        self._fuel_level -= energy_consumed


# 이 함수는 Vehicle 타입을 기대하며 "리터" 단위를 가정
def drive_vehicle(vehicle: Vehicle, distance: float) -> None:
    initial_fuel = vehicle.fuel_level()
    vehicle.consume_fuel(distance)
    fuel_consumed = initial_fuel - vehicle.fuel_level()
    print(f"연료 소모량: {fuel_consumed:.2f} 리터")


# 사용법
car = Vehicle(50)  # 50리터 탱크
drive_vehicle(car, 100)  # 정상 작동

electric_car = ElectricCar(50)  # 50kWh 배터리
drive_vehicle(electric_car, 100)  # 이 코드는 잘못된 연료 소비량을 출력
