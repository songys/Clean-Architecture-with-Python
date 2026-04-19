# 안티패턴: 구현체를 직접 생성하여 강한 결합이 발생하는 컨트롤러 예시
# - 의존성 주입 없이 구현체를 내부에서 직접 생성하면 테스트와 교체가 어려움
# - 클린 아키텍처에서는 추상화(인터페이스)에만 의존해야 함
class TightlyCoupledTaskController:

    def __init__(self):

        # 구현체를 직접 생성하여 강한 결합이 발생
        # SqliteTaskRepository라는 구체적인 저장소 구현에 직접 의존 (교체 불가)
        self.use_case = TaskUseCase(SqliteTaskRepository())
        # CliTaskPresenter라는 구체적인 프레젠터 구현에 직접 의존 (다른 출력 형식 지원 불가)
        self.presenter = CliTaskPresenter()

    def handle_create(self, title: str, description: str):

        # 구현 세부 사항 생략

        pass
