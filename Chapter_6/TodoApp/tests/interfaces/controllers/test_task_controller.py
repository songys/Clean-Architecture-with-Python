# 컨트롤러 테스트 - 모의 객체(Mock)를 사용한 단위 테스트
# - 유스케이스와 프레젠터를 모의 객체로 대체하여 컨트롤러의 데이터 변환 로직만 독립적으로 검증
# - 의존성 주입 덕분에 실제 유스케이스나 프레젠터 없이도 컨트롤러 테스트 가능
from datetime import datetime, timezone
import pytest
from uuid import uuid4
from todo_app.interfaces.view_models.base import ErrorViewModel
from todo_app.domain.value_objects import TaskStatus, Priority
from todo_app.application.dtos.task_dtos import TaskResponse
from todo_app.application.common.result import Result, Error, ErrorCode
from todo_app.interfaces.controllers.task_controller import TaskController
from todo_app.interfaces.view_models.task_vm import TaskViewModel


# 유스케이스의 모의 객체 - 실제 비즈니스 로직 대신 미리 정해진 결과를 반환
@pytest.fixture
def mock_create_use_case():
    class MockCreateUseCase:
        def execute(self, request):
            if request.title == "error":
                return Result.failure(
                    Error(code=ErrorCode.VALIDATION_ERROR, message="Invalid title")
                )
            return Result.success(
                TaskResponse(
                    id=str(uuid4()),
                    title=request.title,
                    description=request.description,
                    status=TaskStatus.TODO,
                    priority=Priority.MEDIUM,
                )
            )

    return MockCreateUseCase()


# 작업 완료 유스케이스의 모의 객체
@pytest.fixture
def mock_complete_use_case():
    class MockCompleteUseCase:
        def execute(self, request):
            # "찾을 수 없음" 시나리오를 테스트하기 위해 사용할 특정 UUID
            not_found_id = "550e8400-e29b-41d4-a716-446655440000"

            if request.task_id == not_found_id:
                return Result.failure(Error(code=ErrorCode.NOT_FOUND, message="Task not found"))
            return Result.success(
                TaskResponse(
                    id=request.task_id,
                    title="Test Task",
                    description="Description",
                    status=TaskStatus.DONE,
                    priority=Priority.MEDIUM,
                    completion_date=datetime.now(timezone.utc),
                    completion_notes=request.completion_notes,
                )
            )

    return MockCompleteUseCase()


# 프레젠터의 모의 객체 - 실제 형식화 대신 단순 변환만 수행
@pytest.fixture
def mock_presenter():
    class MockPresenter:
        def present_task(self, task_response):
            return TaskViewModel(
                id=task_response.id,
                title=task_response.title,
                description=task_response.description,
                status_display=f"[{task_response.status.name}]",
                priority_display=str(task_response.priority.value),
                due_date_display="",
                project_display="",
                completion_info="",
            )

        def present_error(self, message, code):
            return ErrorViewModel(message=message, code=code)

    return MockPresenter()


# 의존성 주입으로 모의 객체를 조립한 컨트롤러 픽스처
@pytest.fixture
def task_controller(mock_create_use_case, mock_complete_use_case, mock_presenter):
    return TaskController(
        create_use_case=mock_create_use_case,
        complete_use_case=mock_complete_use_case,  # 모의 객체를 사용하는지 확인
        presenter=mock_presenter,
    )


def test_handle_create_success(task_controller):
    """성공적인 작업 생성 테스트"""
    result = task_controller.handle_create(title="Test Task", description="Test Description")

    assert result.is_success
    assert isinstance(result.success, TaskViewModel)
    assert result.success.title == "Test Task"
    assert result.success.status_display == "[TODO]"


def test_handle_create_failure(task_controller):
    """실패한 작업 생성 테스트"""
    result = task_controller.handle_create(title="error", description="Test Description")

    assert not result.is_success
    assert result.error.message == "Invalid title"
    assert result.error.code == "VALIDATION_ERROR"


def test_handle_create_validation_error(task_controller):
    """검증 오류 처리 테스트"""
    result = task_controller.handle_create(
        title="", description="Test Description"  # 빈 제목은 ValueError를 발생시켜야 함
    )

    assert not result.is_success
    assert "Title is required" in result.error.message
    assert result.error.code == "VALIDATION_ERROR"


def test_handle_complete_success(task_controller):
    """성공적인 작업 완료 테스트"""
    task_id = str(uuid4())
    result = task_controller.handle_complete(task_id=task_id, notes="Completed successfully")

    assert result.is_success
    assert result.success.id == task_id
    assert isinstance(result.success, TaskViewModel)
    assert result.success.status_display == "[DONE]"


def test_handle_complete_invalid_id_format(task_controller):
    """유효하지 않은 작업 ID 형식으로 완료 테스트"""
    result = task_controller.handle_complete(
        task_id="not-a-uuid", notes="Will fail"  # 유효하지 않은 UUID 형식
    )

    assert not result.is_success
    assert "Invalid task ID format" in result.error.message
    assert result.error.code == "VALIDATION_ERROR"


def test_handle_complete_task_not_found(task_controller):
    """존재하지 않는 작업 완료 테스트"""
    result = task_controller.handle_complete(
        task_id="550e8400-e29b-41d4-a716-446655440000",  # 이 UUID는 찾을 수 없음 케이스를 트리거함
        notes="Will fail",
    )

    assert not result.is_success
    assert "Task not found" in result.error.message
    assert result.error.code == "NOT_FOUND"
