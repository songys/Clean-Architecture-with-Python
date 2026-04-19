from dataclasses import dataclass
from uuid import UUID


# 클린 아키텍처: 외부 의존성이 전혀 없는 순수 도메인 엔티티
# DB, 알림 등 인프라 관심사를 완전히 분리하여 테스트가 간단해지는 구조
@dataclass
class Task:
    """클린 아키텍처: 순수 도메인 엔터티"""

    title: str
    description: str
    project_id: UUID
    priority: Priority = Priority.MEDIUM  # 기본 우선순위: MEDIUM


# 클린 테스트: 외부 설정 없이 도메인 객체만으로 비즈니스 규칙 검증 가능
# 안티패턴(00번)과 비교하면 설정 코드가 크게 줄어들고, 실패 원인이 명확한 구조
def test_new_task_priority():
    """도메인 로직에만 집중하는 클린 테스트"""
    task = Task(
        title="Test task",
        description="Test description",
        project_id=UUID("12345678-1234-5678-1234-567812345678"),
    )
    assert task.priority == Priority.MEDIUM
