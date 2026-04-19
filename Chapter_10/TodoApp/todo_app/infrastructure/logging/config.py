# todo_app/infrastructure/logging/config.py
# 인프라스트럭처 계층의 로깅 설정 모듈
# - 로깅 구현 세부사항(JSON 포맷, 파일 핸들러 등)을 인프라 계층에 격리
# - 다른 계층은 파이썬 표준 logging 모듈만 사용하면 됨
from logging.config import dictConfig
from pathlib import Path
import json
import logging
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID
from todo_app.infrastructure.logging.trace import get_trace_id


class JsonLogEncoder(json.JSONEncoder):
    """로그 레코드를 위한 커스텀 JSON 인코더.
    - datetime, UUID, set, Exception 등 기본 JSON 직렬화가 불가능한 타입 처리
    """

    def default(self, o):
        # json.dumps가 기본적으로 처리할 수 없는 일반적인 타입 처리
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, Exception):
            return str(o)
        # 나머지는 기본 클래스에 위임
        return super().default(o)


class JsonFormatter(logging.Formatter):
    """로그 레코드를 JSON 형식으로 포맷하는 커스텀 포맷터.
    - 단일 책임 원칙: JSON 형식화 로직을 하나의 컴포넌트에 캡슐화
    - 타임스탬프, 로그 레벨, 트레이스 ID, 비즈니스 컨텍스트 등 구조화된 정보 포함
    """

    def __init__(self, app_context: str):
        super().__init__()
        # CLI 또는 WEB 컨텍스트 구분 (로그에서 어떤 인터페이스에서 발생했는지 식별)
        self.app_context = app_context
        self.encoder = JsonLogEncoder()

    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON으로 포맷한다."""
        log_data = {
            "timestamp": datetime.now(timezone.utc),  # 인코더가 datetime 처리
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app_context": self.app_context,
            "trace_id": get_trace_id(),
        }

        # extra 매개변수로 로깅할 때(예: logger.info("msg", extra={"context": {...}})),
        # 파이썬의 로깅 메커니즘은 이러한 매개변수를 LogRecord 객체의 속성으로 직접 추가한다.
        # 즉, extra={"context": {"key": "value"}}는 record.extra.context가 아닌
        # record.context로 접근할 수 있다.
        #
        # 이 접근 방식은 커스텀 데이터를 'context' 아래에 네임스페이싱함으로써
        # LogRecord의 내장 속성('msg', 'args', 'exc_info' 등)과의
        # 이름 충돌을 피하는 데 도움이 된다.
        context = {}
        for key, value in record.__dict__.items():
            if key == "context":
                context = value
                break

        if context:
            log_data["context"] = context

        return self.encoder.encode(log_data)


def configure_logging(app_context: Literal["CLI", "WEB"]) -> None:
    """
    합리적인 기본값으로 애플리케이션 로깅을 설정한다.

    Args:
        app_context: CLI 또는 WEB 컨텍스트 여부
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # dictConfig를 사용한 로깅 설정
    # - 포맷터(formatters): 로그 메시지의 출력 형식 정의
    # - 핸들러(handlers): 로그 메시지의 출력 대상 정의
    # - 로거(loggers): 특정 모듈/패키지의 로깅 동작 정의
    config = {
        "version": 1,
        "formatters": {
            # 애플리케이션 로그용 JSON 포맷터 (트레이스 ID, 비즈니스 컨텍스트 포함)
            "json": {"()": JsonFormatter, "app_context": app_context},
            # 프레임워크(werkzeug) 로그용 표준 텍스트 포맷터
            "standard": {
                "format": "%(asctime)s [%(trace_id)s] %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            # 표준 콘솔 출력 (Flask용)
            "standard_console": {"class": "logging.StreamHandler", "formatter": "standard"},
            # JSON 콘솔 출력 (우리 앱용)
            "json_console": {"class": "logging.StreamHandler", "formatter": "json"},
            # 애플리케이션 로그 파일 핸들러 (JSON 형식으로 app.log에 기록)
            "app_file": {
                "class": "logging.FileHandler",
                "filename": log_dir / "app.log",
                "formatter": "json",
            },
            # 접근 로그 파일 핸들러 (표준 형식으로 access.log에 기록)
            "access_file": {
                "class": "logging.FileHandler",
                "filename": log_dir / "access.log",
                "formatter": "standard",
            },
        },
        "loggers": {
            # 애플리케이션 로거 - CLI에서는 파일만, WEB에서는 콘솔+파일에 기록
            "todo_app": {
                "handlers": ["app_file"] if app_context == "CLI" else ["json_console", "app_file"],
                "level": "INFO",
            },
            # Flask의 werkzeug 로거 - HTTP 요청 로그를 별도 관리
            "werkzeug": {
                "handlers": ["standard_console", "access_file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    dictConfig(config)
