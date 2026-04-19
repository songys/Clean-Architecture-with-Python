# todo_app/application/use_cases/task_use_cases.py
# 유스 케이스 계층에서의 프레임워크 독립적 로깅 예시
# - 파이썬 표준 logging 모듈만 사용하여 Flask 등 특정 프레임워크에 의존하지 않음
import logging

# 모듈 단위 로거 생성 (로거 이름은 모듈 경로를 자동 반영)
logger = logging.getLogger(__name__)

@dataclass
class CreateTaskUseCase:
    # 리포지토리 의존성 (의존성 주입을 통해 외부에서 제공)
    task_repository: TaskRepository
    project_repository: ProjectRepository

    def execute(self, request: CreateTaskRequest) -> Result:
        try:
            # 구조화된 로깅: extra의 "context" 키에 비즈니스 컨텍스트 정보 포함
            # - 로그 메시지와 별도로 검색/필터링 가능한 메타데이터 제공
            logger.info(
                "Creating new task",
                extra={"context": {
                  "title": request.title, "project_id": request.project_id
                }},
            )
            # ... 구현 계속 ...