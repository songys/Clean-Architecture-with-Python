# 리포지토리 인터페이스와 서비스 인터페이스 정의
# - 애플리케이션 계층에서 인터페이스를 정의하고, 인프라 계층에서 구현하는 의존성 역전 원칙(DIP) 적용
# - ABC(추상 기본 클래스)를 사용하여 구현체가 반드시 메서드를 제공하도록 강제하는 계약(Contract)

from abc import abstractmethod, ABC
from uuid import UUID

from todo_app.domain.entities.task import Task


# 작업(Task) 영속성을 위한 리포지토리 인터페이스
# - 애플리케이션 계층이 "어떤 기능이 필요한지"만 정의하고, "어떻게 구현하는지"는 인프라 계층에 위임
class TaskRepository(ABC):
    """애플리케이션 계층에서 정의한 리포지토리 인터페이스"""

    @abstractmethod
    def get(self, task_id: UUID) -> Task:
        """ID로 작업을 조회함"""
        pass

    @abstractmethod
    def save(self, task: Task) -> None:
        """작업을 리포지토리에 저장함"""
        pass

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        """리포지토리에서 작업을 삭제함"""
        pass


# 알림 전송을 위한 서비스 인터페이스
# - 이메일, SMS 등 구체적인 알림 방식을 몰라도 되는, 애플리케이션 계층의 추상 계약
class NotificationService(ABC):
    """알림 전송을 위한 서비스 인터페이스"""

    @abstractmethod
    def notify_task_assigned(self, task_id: UUID) -> None:
        """작업이 할당되었을 때 알림"""
        pass

    @abstractmethod
    def notify_task_completed(self, task_id: UUID) -> None:
        """작업이 완료되었을 때 알림"""
        pass
