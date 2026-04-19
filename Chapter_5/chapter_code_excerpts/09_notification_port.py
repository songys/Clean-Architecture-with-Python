# 포트(Port) 인터페이스 정의
# - 포트: 애플리케이션 계층이 외부 서비스에 필요로 하는 기능을 추상적으로 정의한 인터페이스
# - 리포지토리가 데이터 저장 기능을 추상화하듯, 포트는 외부 서비스 기능을 추상화
# - 구체적인 알림 방식(이메일, SMS 등)은 인프라 계층의 어댑터가 구현
from abc import abstractmethod, ABC
from uuid import UUID


# 알림 기능을 위한 포트(Port) - 애플리케이션 계층이 필요로 하는 기능 정의
# - 유스케이스는 이 추상 인터페이스에만 의존하여 구체적 구현과 분리
class NotificationPort(ABC):

    @abstractmethod
    def notify_task_completed(self, task: Task) -> None:
        """작업이 완료되었을 때 알림"""
        pass

    # 필요에 따라 추가 기능 확장
