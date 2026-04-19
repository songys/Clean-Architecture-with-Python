# === Literal 타입 — 허용되는 값을 정확히 지정하는 타입 힌트 ===
# 인터페이스 경계에서 특정 값만 허용하도록 강제할 때 유용
# 유효하지 않은 데이터가 시스템 전체로 퍼지는 것을 방지하는 역할
from typing import Literal

# 타입 별칭 정의 — 로그 레벨로 허용되는 4가지 문자열 값만 지정
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


# level 매개변수에 LogLevel에 정의된 값만 허용
# "CRITICAL" 등 정의되지 않은 값은 타입 검사기가 오류로 표시
def set_log_level(level: LogLevel) -> None:
    print(f"Setting log level to {level}")


# 사용법
set_log_level("DEBUG")  # 유효함
set_log_level("CRITICAL")  # 타입 검사기가 오류로 표시
