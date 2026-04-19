# === SendGrid 외부 서비스 통합 ===
# 애플리케이션 계층의 포트(인터페이스)와 인프라스트럭처 계층의 어댑터(구현체) 관계 시연

from abc import ABC, abstractmethod
from dataclasses import dataclass
import os

# --- 애플리케이션 계층: 알림 포트(인터페이스) 정의 ---
# 외부 알림 서비스와의 계약 — 구현 세부사항은 노출하지 않음
class NotificationPort(ABC):
    """작업 이벤트에 대한 알림 전송 인터페이스 — 외부 서비스와의 경계"""

    @abstractmethod
    def notify_task_completed(self, task: Task) -> None:
        """작업이 완료되었을 때 알린다."""
        pass

    @abstractmethod
    def notify_task_high_priority(self, task: Task) -> None:
        """작업이 높은 우선순위로 설정되었을 때 알림"""
        pass

# --- 구성 클래스: 외부 서비스 인증 정보 관리 ---
class Config:
    """애플리케이션 구성 — 환경 변수를 통한 외부 서비스 설정 관리"""
    # 이전 리포지토리 설정 생략...

    @classmethod
    def get_sendgrid_api_key(cls) -> str:
        """SendGrid API 키 반환 — 환경 변수에서 조회"""
        return os.getenv("TODO_SENDGRID_API_KEY", "")

    @classmethod
    def get_notification_email(cls) -> str:
        """알림 수신자 이메일 반환 — 환경 변수에서 조회"""
        return os.getenv("TODO_NOTIFICATION_EMAIL", "")
    # ... 나머지 구현

# --- 인프라스트럭처 계층: SendGrid 어댑터(구현체) ---
# NotificationPort 인터페이스의 실제 이메일 서비스 구현
class SendGridNotifier(NotificationPort):
    """알림 포트의 SendGrid 구현 — 외부 이메일 서비스 어댑터"""

    def __init__(self) -> None:
        # 구성 클래스에서 인증 정보 조회
        self.api_key = Config.get_sendgrid_api_key()
        self.notification_email = Config.get_notification_email()
        self._init_sg_client()

    def notify_task_completed(self, task: Task) -> None:
        """설정된 경우 완료된 작업에 대한 이메일 알림을 전송"""
        # 클라이언트나 이메일이 미설정이면 조용히 건너뜀
        if not (self.client and self.notification_email):
            return
        try:
            # SendGrid SDK를 사용한 이메일 전송
            message = Mail(
                from_email=self.notification_email,
                to_emails=self.notification_email,
                subject=f"작업 완료: {task.title}",
                plain_text_content=f"작업 '{task.title}' 완료"
            )
            self.client.send(message)
        except Exception as e:
            # 알림 실패가 비즈니스 작업을 방해하지 않도록 오류만 기록
            # ...

# === 유스 케이스에서의 알림 통합 ===
# 작업 완료 워크플로우에 어떻게 적용되는지 살펴보자.
# 5장에서 알림과 함께 작업 완료를 조율하는 CompleteTaskUseCase를 다룬 적이 있다:
@dataclass
class CompleteTaskUseCase:
    task_repository: TaskRepository
    notification_service: NotificationPort  # 포트를 통한 의존성 주입

    def execute(self, request: CompleteTaskRequest) -> Result:
        try:
            task = self.task_repository.get(request.task_id)
            task.complete(notes=request.completion_notes)
            self.task_repository.save(task)
            # 알림 전송 — 어떤 구현체가 주입되었든 동일한 인터페이스로 호출
            self.notification_service.notify_task_completed(task)
            # ... 나머지 구현

        except :
            ...