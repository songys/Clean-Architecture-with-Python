# ============================================================
# LSP(리스코프 치환 원칙) 적용 후 - 리팩토링 완료
# 상속 대신 구성(Composition)을 활용하여 동력원을 추상화한 구조
# 어떤 동력원이든 Vehicle에 주입하면 동일한 인터페이스로 동작
# ============================================================

from abc import ABC, abstractmethod


# 모든 동력원의 공통 인터페이스 역할을 하는 추상 기본 클래스
# 연료 탱크, 배터리 등 다양한 동력원이 이 계약을 따르는 구조
class PowerSource(ABC):
    def __init__(self, capacity: float):
        self._capacity = capacity
        self._level = capacity  # 초기 에너지 수준 = 최대 용량

    def level(self) -> float:
        return self._level

    @abstractmethod
    def consume(self, distance: float) -> float:
        """주행 거리만큼 에너지를 소비하고 소비량을 반환하는 추상 메서드"""
        pass


# 내연기관 연료 탱크 구현 - PowerSource를 상속한 구체 클래스
class FuelTank(PowerSource):
    def consume(self, distance: float) -> float:
        fuel_consumed = distance / 10  # 단순화를 위해 1리터당 10km 가정
        if self._level - fuel_consumed < 0:
            raise ValueError("해당 거리를 주행할 만큼의 연료가 부족합니다")
        self._level -= fuel_consumed
        return fuel_consumed


# 전기차 배터리 구현 - PowerSource를 상속한 구체 클래스
class Battery(PowerSource):
    def consume(self, distance: float) -> float:
        energy_consumed = distance / 5  # 단순화를 위해 1kWh당 5km 가정
        if self._level - energy_consumed < 0:
            raise ValueError("해당 거리를 주행할 만큼의 충전량이 되어 있지 않습니다")
        self._level -= energy_consumed
        return energy_consumed


# Vehicle: 동력원을 외부에서 주입받는 구성(Composition) 패턴 적용
# 어떤 PowerSource든 교체 가능하므로 LSP를 자연스럽게 준수
class Vehicle:
    def __init__(self, power_source: PowerSource):
        self._power_source = power_source  # 동력원을 생성자 주입으로 받음

    def power_level(self) -> float:
        return self._power_source.level()

    def drive(self, distance: float) -> float:
        return self._power_source.consume(distance)


# 통일된 인터페이스로 모든 차량 타입을 동일하게 처리하는 함수
def drive_vehicle(vehicle: Vehicle, distance: float) -> None:
    try:
        energy_consumed = vehicle.drive(distance)
        print(f"소비된 에너지: {energy_consumed:.2f} 단위")  # 단위가 통일되어 혼동 없음
    except ValueError as e:
        print(f"여행 완료 불가: {e}")


# 사용법 - 동력원만 교체하면 차량 타입이 자연스럽게 변경
fuel_car = Vehicle(FuelTank(50))  # 50리터 탱크
drive_vehicle(fuel_car, 100)  # 출력: 소비된 에너지: 10.00 단위

electric_car = Vehicle(Battery(50))  # 50kWh 배터리
drive_vehicle(electric_car, 100)  # 출력: 소비된 에너지: 20.00 단위
