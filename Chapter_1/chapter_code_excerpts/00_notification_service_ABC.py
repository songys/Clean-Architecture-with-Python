# ABC(추상 기본 클래스)를 활용한 알림 서비스 예제
# 클린 아키텍처의 핵심 원칙인 "추상화에 의존하라"를 보여주는 코드
from abc import ABC, abstractmethod


# 알림 발송의 추상 인터페이스 (클린 아키텍처의 내부 원에 해당)
# 모든 알림 클래스가 반드시 구현해야 할 계약(contract) 정의
class Notifier(ABC):
    @abstractmethod
    def send_notification(self, message: str) -> None:
        # 하위 클래스에서 반드시 구현해야 하는 추상 메서드
        pass


# 이메일 방식의 구체적 알림 구현체 (외부 원에 해당)
# Notifier 추상 클래스를 상속받아 실제 이메일 발송 로직 구현
class EmailNotifier(Notifier):
    def send_notification(self, message: str) -> None:

        print(f"이메일 발송: {message}")


# SMS 방식의 구체적 알림 구현체 (외부 원에 해당)
# Notifier 추상 클래스를 상속받아 실제 SMS 발송 로직 구현
class SMSNotifier(Notifier):
    def send_notification(self, message: str) -> None:

        print(f"SMS 발송: {message}")


# 알림 서비스 클래스 - 의존성 역전 원칙(DIP)의 적용
# 구체 클래스(EmailNotifier, SMSNotifier)가 아닌 추상 클래스(Notifier)에 의존
# → 새로운 알림 방식 추가 시 이 클래스를 수정할 필요 없음 (개방-폐쇄 원칙)
class NotificationService:
    def __init__(self, notifier: Notifier):
        # 생성자를 통한 의존성 주입 - 외부에서 구체적 알림 구현체를 전달
        self.notifier = notifier

    def notify(self, message: str) -> None:
        # 추상 인터페이스의 메서드 호출 - 실제 구현체가 무엇인지 알 필요 없음
        self.notifier.send_notification(message)


# 사용 예시
# EmailNotifier 구체 클래스 생성 후 NotificationService에 주입
email_notifier = EmailNotifier()
email_service = NotificationService(email_notifier)
email_service.notify("이메일을 통한 인사")
