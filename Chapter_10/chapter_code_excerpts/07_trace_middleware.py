# todo_app/infrastructure/web/middleware.py
# Flask 미들웨어를 활용한 요청 단위 트레이스 ID 관리
# - 인프라스트럭처 계층에 위치하여 프레임워크 의존적 코드를 격리
# - 요청 시작 시 트레이스 ID를 설정하고, 응답에 트레이스 ID를 포함
def trace_requests(app):
    """모든 요청에 추적 ID를 추가한다."""

    @app.before_request
    def before_request():
        # 클라이언트가 X-Trace-ID 헤더로 전달한 ID가 있으면 사용 (분산 추적 지원)
        trace_id = request.headers.get("X-Trace-ID") or None
        # ContextVar에 트레이스 ID 설정 (이 요청의 모든 로그에 자동 포함)
        g.trace_id = set_trace_id(trace_id)

    @app.after_request
    def after_request(response):
        # 응답 헤더에 트레이스 ID 포함 (클라이언트가 로그 추적 시 활용 가능)
        response.headers["X-Trace-ID"] = g.trace_id
        return response
