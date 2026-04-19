from datetime import datetime, timedelta
from uuid import UUID


# AAA(Arrange-Act-Assert) 패턴을 적용한 엔티티 단위 테스트
# 준비(Arrange) -> 실행(Act) -> 검증(Assert) 구조로 테스트 가독성 향상
def test_task_completion_captures_completion_time():
    """작업 완료 시 완료 타임스탬프가 기록되는지 테스트"""
    # 준비 - 순수 도메인 객체만으로 테스트 데이터 구성
    task = Task(
        title="Test task",
        description="Test description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )

    # 실행 - 테스트 대상 메서드 호출
    task.complete()

    # 검증 - 완료 시각이 현재 시각과 1초 이내 차이인지 확인
    assert task.completed_at is not None
    assert (datetime.now() - task.completed_at) < timedelta(seconds=1)
