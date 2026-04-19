from dataclasses import dataclass


# 프레임워크 독립적 컨트롤러 설계를 보여주는 예시
# - 웹 프레임워크(FastAPI, Flask 등)나 특정 저장소에 의존하지 않는 구조
# - 추상화에만 의존하여 어떤 전달 메커니즘(CLI, 웹, 메시지 큐)에서도 재사용 가능
@dataclass
class TaskController:
    # 애플리케이션 계층 인터페이스 - 유스케이스의 구체적 구현을 몰라도 됨 (덕 타이핑 활용)
    create_use_case: CreateTaskUseCase
    # 인터페이스 계층 추상화 - 프레젠터의 구체적 구현을 몰라도 됨 (ABC 인터페이스)
    presenter: TaskPresenter
