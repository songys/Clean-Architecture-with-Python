# Flask 요청 추적 미들웨어 (횡단 관심사의 인프라스트럭처 계층 구현)
# - 모든 웹 요청에 트레이스 ID를 자동으로 부여하여 요청 단위 로그 추적 가능
# - 인프라 계층에 위치하여 프레임워크 의존적 코드를 격리
from functools import wraps
from flask import request, g
from ..logging.trace import set_trace_id, get_trace_id
import logging


def trace_requests(flask_app):
    """모든 요청에 추적 ID를 추가한다.

    이 미들웨어는:
    1. 요청 간 추적 ID를 생성하거나 전파한다
    2. 응답 헤더에 추적 ID를 추가한다
    """

    @flask_app.before_request
    def before_request():
        # 클라이언트가 X-Trace-ID 헤더로 전달한 ID가 있으면 사용 (분산 추적 지원)
        trace_id = request.headers.get("X-Trace-ID") or None
        # ContextVar에 트레이스 ID 설정 (이 요청의 모든 로그에 자동 포함)
        g.trace_id = set_trace_id(trace_id)

    @flask_app.after_request
    def after_request(response):
        # 응답 헤더에 트레이스 ID 포함 (클라이언트가 로그 추적 시 활용 가능)
        response.headers["X-Trace-ID"] = g.trace_id
        return response

    # werkzeug 로거에 필터를 추가하여 모든 HTTP 요청 로그에도 트레이스 ID 포함
    # - 표준 포맷의 %(trace_id)s 패턴으로 출력
    logging.getLogger("werkzeug").addFilter(
        lambda record: setattr(record, "trace_id", get_trace_id()) or True
    )
