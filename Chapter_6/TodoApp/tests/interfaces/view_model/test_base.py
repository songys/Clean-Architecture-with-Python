# tests/interfaces/view_models/test_base.py
# OperationResult와 ErrorViewModel의 동작 검증 테스트
# - Either 패턴의 정확한 구현(성공/실패 배타적 보장)을 확인
import dataclasses
import pytest
from todo_app.interfaces.view_models.base import ErrorViewModel, OperationResult


def test_error_view_model_creation():
    """오류 뷰 모델 생성 테스트"""
    error = ErrorViewModel(message="Test error", code="TEST_ERROR")
    assert error.message == "Test error"
    assert error.code == "TEST_ERROR"


def test_error_view_model_immutability():
    """오류 뷰 모델의 불변성 테스트"""
    error = ErrorViewModel(message="Test error", code="TEST_ERROR")
    with pytest.raises(dataclasses.FrozenInstanceError):
        error.message = "New message"


def test_operation_result_success():
    """성공적인 작업 결과 생성 테스트"""
    data = {"key": "value"}
    result = OperationResult.succeed(data)

    assert result.is_success
    assert result.success == data
    with pytest.raises(ValueError):
        _ = result.error


def test_operation_result_failure():
    """실패한 작업 결과 생성 테스트"""
    error = ErrorViewModel(message="Failed", code="ERROR")
    result = OperationResult.fail(error.message, error.code)

    assert not result.is_success
    assert result.error.message == "Failed"
    assert result.error.code == "ERROR"
    with pytest.raises(ValueError):
        _ = result.success


def test_operation_result_invalid_creation():
    """OperationResult가 성공과 오류를 동시에 가질 수 없는지 테스트"""
    with pytest.raises(ValueError):
        OperationResult(
            success={"key": "value"}, error=ErrorViewModel(message="Failed", code="ERROR")
        )


def test_operation_result_invalid_empty_creation():
    """OperationResult가 성공이나 오류 없이 생성될 수 없는지 테스트"""
    with pytest.raises(ValueError):
        OperationResult()
