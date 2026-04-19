# 웹 인터페이스의 컴포지션 루트 (진입점)
# CLI의 cli_main.py(02번 파일)와 비교하면, 프레젠터만 웹 전용으로 교체
def main():
    """플라스크 웹 애플리케이션을 생성하고 실행한다."""
    # 웹 전용 의존성을 주입하여 Application 컨테이너 생성
    # WebTaskPresenter/WebProjectPresenter: HTML 템플릿에 적합한 포맷 담당
    app_container = create_application(
        notification_service=NotificationRecorder(),
        task_presenter=WebTaskPresenter(),
        project_presenter=WebProjectPresenter(),
    )

    # Flask 웹 앱 생성 및 개발 모드로 실행
    flask_app = create_web_app(app_container)
    flask_app.run(debug=True)


if __name__ == "__main__":
    main()
