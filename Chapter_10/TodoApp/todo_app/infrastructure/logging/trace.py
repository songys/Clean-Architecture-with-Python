# 요청 추적을 위한 트레이스 ID 관리 모듈 (횡단 관심사)
# - 하나의 요청이 여러 아키텍처 계층(컨트롤러 -> 유스케이스 -> 리포지토리)을
#   거칠 때 동일한 ID로 모든 로그를 연결하여 추적 가능
# - ContextVar를 사용하여 스레드/비동기 환경에서도 안전한 저장소 제공
from uuid import uuid4
from contextvars import ContextVar
from typing import Optional

# 추적 ID를 보관하는 스레드 안전 컨텍스트 변수
# - ContextVar: 각 스레드/비동기 태스크별로 독립적인 값 유지
# - 웹 서버에서 동시에 여러 요청을 처리해도 트레이스 ID가 섞이지 않음
# 빈 문자열 대신 None 기본값으로 초기화
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def get_trace_id() -> str:
    """현재 추적 ID를 가져오거나 설정되지 않은 경우 새로 생성한다.
    - 로그 포맷터(JsonFormatter)에서 호출하여 모든 로그에 트레이스 ID 포함
    - 아직 설정되지 않은 경우 자동으로 새 UUID 생성
    """
    current = trace_id_var.get()
    if current is None:
        current = str(uuid4())
        trace_id_var.set(current)
    return current


def set_trace_id(trace_id: Optional[str] = None) -> str:
    """현재 컨텍스트의 추적 ID를 설정한다.
    - 외부에서 전달된 ID가 있으면 사용 (분산 추적, 테스트 시 유용)
    - 없으면 새 UUID 생성
    """
    new_id = trace_id or str(uuid4())
    trace_id_var.set(new_id)
    return new_id
