"""
할 일 앱을 위한 Flask 라우트.
- Flask 블루프린트를 사용하여 라우트를 모듈화
- 각 라우트에서 Application 컨테이너의 컨트롤러를 호출하여 비즈니스 로직 실행
- 프레젠터를 통해 오류 메시지를 웹에 적합한 형식으로 변환
"""

# [수정] flask 미설치 시에도 동작하도록 보호
try:
    from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
except ImportError:
    Blueprint = type('Blueprint', (), {'__init__': lambda *a, **kw: None, 'route': lambda *a, **kw: (lambda f: f)})  # type: ignore
from todo_app.domain.value_objects import Priority
from todo_app.interfaces.presenters.web import WebProjectPresenter, WebTaskPresenter

bp = Blueprint("todo", __name__)
project_presenter = WebProjectPresenter()
task_presenter = WebTaskPresenter()


@bp.route("/")
def index():
    """모든 프로젝트와 작업을 나열한다."""
    app = current_app.config["APP_CONTAINER"]
    show_completed = request.args.get("show_completed", "false").lower() == "true"

    result = app.project_controller.handle_list()
    if not result.is_success:
        error = project_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("todo.index"))

    return render_template("index.html", projects=result.success, show_completed=show_completed)


@bp.route("/projects/new", methods=["GET", "POST"])
def new_project():
    """새 프로젝트를 생성한다."""
    if request.method == "POST":
        name = request.form["name"]
        app = current_app.config["APP_CONTAINER"]
        result = app.project_controller.handle_create(name)

        if not result.is_success:
            error = project_presenter.present_error(result.error.message)
            flash(error.message, "error")
            return redirect(url_for("todo.index"))

        # 컨트롤러 응답에서 직접 뷰 모델 사용
        project = result.success
        flash(f'프로젝트 "{project.name}"이(가) 성공적으로 생성되었습니다', "success")
        return redirect(url_for("todo.index"))

    return render_template("project_form.html")


@bp.route("/projects/<project_id>/task  s/new", methods=["GET", "POST"])
def new_task(project_id):
    """프로젝트에 새 작업을 생성한다."""
    if request.method == "POST":
        app = current_app.config["APP_CONTAINER"]
        result = app.task_controller.handle_create(
            project_id=project_id,
            title=request.form["title"],
            description=request.form["description"],
            priority=request.form["priority"],
            due_date=request.form["due_date"] if request.form["due_date"] else None,
        )

        if not result.is_success:
            error = task_presenter.present_error(result.error.message)
            flash(error.message, "error")
            return redirect(url_for("todo.index"))

        # 컨트롤러 응답에서 직접 뷰 모델 사용
        task = result.success
        flash(f'작업 "{task.title}"이(가) 성공적으로 생성되었습니다', "success")
        return redirect(url_for("todo.index"))

    return render_template("task_form.html", project_id=project_id)


@bp.route("/tasks/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    """기존 작업을 편집한다."""
    app = current_app.config["APP_CONTAINER"]

    if request.method == "POST":
        # 빈 마감일 처리 - 필드가 비어 있거나 공백만 있으면 빈 문자열로 설정
        # UpdateTaskRequest가 빈 문자열을 받아 None으로 변환하도록 보장
        due_date = request.form.get("due_date", "").strip()

        result = app.task_controller.handle_update(
            task_id=task_id,
            title=request.form["title"],
            description=request.form["description"],
            priority=request.form["priority"],
            due_date=due_date,
        )

        if not result.is_success:
            error = task_presenter.present_error(result.error.message)
            flash(error.message, "error")
            return redirect(url_for("todo.edit_task", task_id=task_id))

        flash("작업이 성공적으로 업데이트되었습니다!", "success")
        return redirect(url_for("todo.index"))

    result = app.task_controller.handle_get(task_id)
    if not result.is_success:
        error = task_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("todo.index"))

    return render_template("edit_task.html", task=result.success)


@bp.route("/tasks/<task_id>/complete", methods=["POST"])
def complete_task(task_id):
    """작업을 완료한다."""
    app = current_app.config["APP_CONTAINER"]

    # 선택적 메모와 함께 작업 완료
    result = app.task_controller.handle_complete(
        task_id=task_id, notes=request.form.get("completion_notes")
    )

    if not result.is_success:
        error = task_presenter.present_error(result.error.message)
        flash(error.message, "error")
    else:
        task = result.success
        flash(f'"{task.title}"이(가) 완료로 표시되었습니다', "success")

    return redirect(
        url_for("todo.index", show_completed=request.args.get("show_completed", "false"))
    )
