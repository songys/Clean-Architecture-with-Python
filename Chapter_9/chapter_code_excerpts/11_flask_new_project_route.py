# todo_app/infrastructure/web/routes.py

# 프로젝트 생성 라우트 - HTTP 폼 제출을 도메인 작업으로 변환하는 어댑터
# GET: 폼 페이지 표시 / POST: 폼 데이터로 프로젝트 생성
@bp.route("/projects/new", methods=["GET", "POST"])
def new_project():
    """새 프로젝트 생성."""
    if request.method == "POST":
        # 웹 특유의 입력 추출 - HTML 폼 필드에서 데이터 가져오기
        name = request.form["name"]
        app = current_app.config["APP_CONTAINER"]
        # 컨트롤러에 기본 타입(str)만 전달 - 인터페이스 독립적 처리
        result = app.project_controller.handle_create(name)

        if not result.is_success:
            error = project_presenter.present_error(result.error.message)
            flash(error.message, "error")
            return redirect(url_for("todo.index"))

        # 컨트롤러 응답의 뷰 모델에서 프로젝트 이름 사용
        project = result.success
        flash(f'프로젝트 "{project.name}" 생성 성공', "success")
        return redirect(url_for("todo.index"))

    # GET 요청 시 프로젝트 생성 폼 페이지 렌더링
    return render_template("project_form.html")
