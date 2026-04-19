# 안티패턴: 도메인 엔터티가 웹 상태에 접근함
# 도메인 계층이 외부 인프라(웹 세션)에 의존하는 의존성 규칙 위반 사례
from datetime import datetime


class Task:
    def complete(self, web_app_contatiner):
        # 잘못됨: Task는 웹 세션에 대해 알면 안 됨
        # 도메인 엔터티가 웹 컨테이너에 직접 접근하면:
        #   - 단위 테스트 시 웹 세션 모의 객체가 필요
        #   - CLI 환경에서는 사용 불가
        #   - 도메인 로직과 인프라의 강한 결합 발생
        self.completed_by = web_app_contatiner.user.id
        self.completed_at = datetime.now()
