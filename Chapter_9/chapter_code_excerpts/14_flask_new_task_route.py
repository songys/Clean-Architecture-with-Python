# 작업 생성 라우트 - CLI의 _create_task(13번 파일)와 동일한 패턴이지만
# HTTP의 요청-응답 주기에 맞게 조정된 웹 어댑터
@bp.route("/projects/<project_id>/tasks/new", methods=["GET", "POST"])
def new_task(project_id):
    """프로젝트에 새 작업을 생성."""
    if request.method == "POST":
        app = current_app.config["APP_CONTAINER"]
        # URL 경로 파라미터(project_id)와 폼 필드를 조합하여 컨트롤러에 전달
        # CLI와 동일한 handle_create 메서드 호출 - 인터페이스 독립적 컨트롤러
        result = app.task_controller.handle_create(
            project_id=project_id,
            title=request.form["title"],
            description=request.form["description"],
            priority=request.form["priority"],
            due_date=request.form["due_date"] if request.form["due_date"] else None,
        )

        if not result.is_success:
            # 웹 전용 오류 처리 - 플래시 메시지 + 리다이렉트
            error = task_presenter.present_error(result.error.message)
            flash(error.message, "error")
            return redirect(url_for("todo.index"))

        # 웹 전용 성공 처리 - 플래시 메시지 + 메인 페이지로 리다이렉트
        task = result.success
        flash(f'작업 "{task.title}" 생성 성공', "success")
        return redirect(url_for("todo.index"))

    return render_template("task_form.html", project_id=project_id)
