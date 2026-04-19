# 안티패턴 예시: 도메인 엔티티가 인프라(DB, 알림)에 직접 의존하는 구조
# 이런 구조에서는 단순한 비즈니스 규칙 테스트에도 외부 서비스가 필요
class Task(Entity):
    """안티패턴: 인프라에 직접 의존하는 도메인 엔터티"""

    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description
        self.db = Database()  # 데이터베이스에 직접 의존
        self.notifier = NotificationService()  # 알림 서비스에 직접 의존
        self.priority = Priority.MEDIUM
        # 생성 시 데이터베이스에 저장하고 알림 전송
        self.id = self.db.save_task(self.as_dict())
        self.notifier(f"Task {self.id} created")


# 안티패턴: "기본 우선순위가 MEDIUM인지" 확인하는 단순 테스트에
# DB 연결과 알림 서비스 설정이 모두 필요한 상황
def test_new_task_priority_antipattern():
    """단순한 도메인 로직과 인프라 관심사를 혼합하는 안티패턴"""
    # 기본값 테스트를 위한 복잡한 설정
    db_connection = create_database_connection()
    notification_service = create_notification_service()
    # 작업 생성만으로도 데이터베이스와 알림 서비스에 접근함
    task = Task(title="Test task", description="Test description")
    # 단순한 속성 확인조차 데이터베이스 쿼리가 필요함
    saved_task = task.db.get_task(task.id)
    assert saved_task["priority"] == Priority.MEDIUM
