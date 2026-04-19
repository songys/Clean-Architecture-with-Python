# todo_app/infrastructure/web/routes.py

# Flask 라우트 - HTTP 요청과 도메인 로직 사이의 경계 역할
# 웹 특유의 관심사(쿼리 파라미터, 플래시 메시지, 템플릿 렌더링)를 처리
@bp.route("/")
def index():
    """모든 프로젝트와 해당 작업들을 나열."""
    # Flask의 current_app에서 Application 컨테이너 가져오기
    app = current_app.config["APP_CONTAINER"]
    # 웹 특유의 상태 처리 - URL 쿼리 파라미터에서 완료 작업 표시 여부 추출
    show_completed = request.args.get("show_completed", "false").lower() == "true"

    # 컨트롤러를 통해 비즈니스 로직 실행 (인터페이스 독립적)
    result = app.project_controller.handle_list()
    if not result.is_success:
        # 웹 전용 사용자 피드백 - 플래시 메시지로 오류 표시
        error = project_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("todo.index"))

    # 프레젠터가 생성한 뷰 모델을 HTML 템플릿에 전달
    return render_template("index.html", projects=result.success, show_completed=show_completed)
