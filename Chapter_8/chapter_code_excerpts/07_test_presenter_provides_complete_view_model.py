from uuid import UUID


# 프레젠터의 뷰 모델 생성 기능 테스트
# 뷰 모델(ViewModel): UI에 표시할 데이터만 담은 읽기 전용 객체
def test_presenter_provides_complete_view_model():
    """프레젠터가 모든 표시 필드를 갖춘 올바른 형식의 뷰 모델을 생성하는지 테스트"""
    # 준비 - HIGH 우선순위, 완료 상태의 작업 생성
    task = Task(
        title="Important Task",
        description="Testing view model creation",
        project_id=UUID('12345678-1234-5678-1234-567812345678'),
        priority=Priority.HIGH
    )
    task.complete()  # 상태를 DONE으로 설정
    task_response = TaskResponse.from_entity(task)  # 엔티티 -> DTO 변환
    presenter = CliTaskPresenter()

    # 실행 - DTO -> 뷰 모델 변환
    view_model = presenter.present_task(task_response)

    # 검증 - 뷰 모델의 각 표시 필드가 올바른 형식인지 확인
    assert view_model.title == "Important Task"
    assert view_model.status_display == "[DONE]"  # 상태의 사람이 읽기 좋은 표현
    assert view_model.priority_display == "High"  # 우선순위의 사람이 읽기 좋은 표현
    assert isinstance(view_model.completion_info, str)  # 완료 정보 존재 여부 확인