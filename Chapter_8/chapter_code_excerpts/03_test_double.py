from unittest.mock import Mock

# 테스트 더블(Test Double): 실제 객체 대신 사용하는 대역 객체
# Mock은 호출 기록 추적과 반환값 사전 설정이 가능한 테스트 더블
mock_repo = Mock()
# 원하는 응답 구성 - get() 호출 시 some_task를 반환하도록 설정
mock_repo.get.return_value = some_task
# 호출 시 some_task 반환
mock_repo.get(123)
# assert_called_once()로 메서드가 정확히 1회 호출되었는지 검증
mock_repo.get.assert_called_once()

# Mock의 상호작용 추적 기능 시연
# call_args: 마지막 호출 시 전달된 인수 확인
print(mock_repo.get.call_args)
# call_count: 총 호출 횟수 확인
print(mock_repo.get.call_count)
