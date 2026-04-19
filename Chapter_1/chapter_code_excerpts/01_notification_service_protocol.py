# Protocol을 활용한 구조적 타이핑(Structural Typing) 기반 알림 서비스 예제
# ABC 대신 Protocol을 사용하여 명시적 상속 없이 클린 아키텍처 구현
# 파이썬의 덕 타이핑(duck typing) 철학과 자연스럽게 어우러지는 방식
from typing import Protocol


# Protocol 기반 알림 인터페이스 정의
# ABC와 달리 이 클래스를 상속받을 필요 없음 - 같은 메서드 시그니처만 있으면 호환
# "오리처럼 걷고 오리처럼 꽥꽥거리면, 그것은 오리다" (덕 타이핑의 핵심 원리)
class Notifier(Protocol):
    def send_notification(self, message: str) -> None:
        # ... (Ellipsis)은 "구현 없음"을 나타내는 파이썬 관례
        ...


# 이메일 알림 구현체 - Notifier를 상속받지 않음에 주목
# send_notification 메서드만 올바른 시그니처로 구현하면 Notifier로 인정
class EmailNotifier:  # 참고: 명시적 상속 없음
    def send_notification(self, message: str) -> None:

        print(f"이메일 발송 중: {message}")


# SMS 알림 구현체 - 역시 명시적 상속 없이 Protocol 호환
class SMSNotifier:  # 참고: 명시적 상속 없음
    def send_notification(self, message: str) -> None:

        print(f"SMS 발송 중: {message}")


# 알림 서비스 - Protocol 타입 힌트를 통한 의존성 역전
# Notifier Protocol에 맞는 어떤 객체든 주입 가능 (구조적 타이핑의 유연성)
class NotificationService:
    def __init__(self, notifier: Notifier):  # 여전히 타입 힌팅 사용 가능
        self.notifier = notifier

    def notify(self, message: str) -> None:
        self.notifier.send_notification(message)


# 사용법
# SMSNotifier는 Notifier를 상속하지 않았지만, 동일한 메서드를 가지므로 사용 가능
sms_notifier = SMSNotifier()
sms_service = NotificationService(sms_notifier)
sms_service.notify("Hello")
