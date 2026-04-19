# web_main.py
# 웹 인터페이스 진입점 - 컴포지션 루트에서 로깅을 가장 먼저 초기화
# - 애플리케이션 시작 시점에 로깅 설정을 완료하여
#   이후 모든 코드가 프레임워크 독립적인 표준 logging 모듈만 사용 가능
def main():
    """로깅을 초기에 설정"""
    # WEB 컨텍스트로 로깅 초기화 (CLI의 경우 "CLI"를 전달)
    configure_logging(app_context="WEB")

    # ...
