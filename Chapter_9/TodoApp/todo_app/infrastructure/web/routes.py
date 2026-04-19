"""
할일 앱을 위한 플라스크 라우트.
HTTP 요청과 클린 아키텍처의 컨트롤러 사이를 연결하는 웹 어댑터 계층
"""

# [수정] flask 미설치 시에도 동작하도록 보호
try:
    from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
except ImportError:
    Blueprint = type('Blueprint', (), {'__init__': lambda *a, **kw: None, 'route': lambda *a, **kw: (lambda f: f)})  # type: ignore
from todo_app.domain.value_objects import Priority
from todo_app.interfaces.presenters.web import WebProjectPresenter, WebTaskPresenter

# Flask 블루프린트 - URL 라우팅 규칙의 모듈화
bp = Blueprint("todo", __name__)
# 라우트에서 직접 오류 포맷팅에 사용하는 웹 프레젠터 인스턴스
project_presenter = WebProjectPresenter()
task_presenter = WebTaskPresenter()


# 메인 페이지 라우트 - 모든 프로젝트와 작업 목록 표시
@bp.route("/")
def index():
    """모든 프로젝트와 작업을 나열한다."""
    # Flask config에서 Application 컨테이너 가져오기
    app = current_app.config["APP_CONTAINER"]
    # 웹 전용 상태 처리 - URL 쿼리 파라미터에서 완료 작업 표시 여부 추출
    show_completed = request.args.get("show_completed", "false").lower() == "true"

    # 인터페이스 독립적 컨트롤러를 통해 비즈니스 로직 실행
    result = app.project_controller.handle_list()
    if not result.is_success:
        # 웹 전용 오류 처리 - 플래시 메시지로 사용자에게 알림
        error = project_presenter.present_error(result.error.message)
        flash(error.message, "error")
        return redirect(url_for("todo.index"))

    # 프레젠터가 생성한 뷰 모델을 HTML 템플릿에 전달
    return render_template("index.html", projects=result.success, show_completed=show_completed)


# 프로젝트 생성 라우트 - GET: 폼 표시, POST: 폼 제출 처리
@bp.route("/projects/new", methods=["GET", "POST"])
def new_project():
    """새 프로젝트를 생성한다."""
    if request.method == "POST":
        # HTML 폼 필드에서 데이터 추출
        name = request.form["name"]
        app = current_app.config["APP_CONTAINER"]
        # 컨트롤러에 기본 타입만 전달 - CLI의 click.prompt와 대칭 구조
        result = app.project_controller.handle_create(name)

        if not result.is_success:
            error = project_presenter.present_error(result.error.message)
            flash(error.message, "error")
            return redirect(url_for("todo.index"))

        # 컨트롤러 응답에서 뷰 모델을 직접 사용
        project = result.success
        flash(f'프로젝트 "{project.name}" 생성 성공', "success")
        return redirect(url_for("todo.index"))

    return render_template("project_form.html")


# 작업 생성 라우트 - URL 경로에서 project_id, 폼에서 작업 상세 추출
@bp.route("/projects/<project_id>/tasks/new", methods=["GET", "POST"])
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

        # 컨트롤러 응답에서 뷰 모델을 직접 사용
        task = result.success
        flash(f'작업 "{task.title}" 생성 성공', "success")
        return redirect(url_for("todo.index"))

    return render_template("task_form.html", project_id=project_id)


# 작업 편집 라우트 - GET: 편집 폼 표시, POST: 편집 결과 반영
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


# 작업 완료 라우트 - POST 전용 (상태 변경 작업이므로 GET 미허용)
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
        flash(f'"{task.title}" 완료로 표시됨', "success")

    return redirect(
        url_for("todo.index", show_completed=request.args.get("show_completed", "false"))
    )
