# todo_app/infrastructure/logging/config.py
# 트레이스 ID가 포함된 로깅 설정 (포맷터 부분 발췌)
# - JSON 포맷터: 애플리케이션 로그에 트레이스 ID를 JSON 필드로 포함
# - 표준 포맷터: werkzeug 로그에 %(trace_id)s 패턴으로 트레이스 ID 포함
def configure_logging(app_context: Literal["CLI", "WEB"]) -> None:
    config = {
        "formatters": {
            # 애플리케이션용 JSON 포맷터 (JsonFormatter 클래스가 트레이스 ID 자동 포함)
            "json": {"()": JsonFormatter, "app_context": app_context},
            # 프레임워크용 표준 포맷터 (%(trace_id)s로 로그 레코드의 트레이스 ID 참조)
            "standard": {
                "format": "%(asctime)s [%(trace_id)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        # ... 나머지 설정
    }
