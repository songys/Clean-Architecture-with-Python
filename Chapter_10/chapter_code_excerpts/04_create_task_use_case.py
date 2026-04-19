# 유스 케이스의 구조화된 로깅 패턴 상세 예시
# - 작업 시작과 완료 시점에 각각 로그를 남겨 비즈니스 운영 추적 가능
@dataclass
class CreateTaskUseCase:
    task_repository: TaskRepository
    project_repository: ProjectRepository

    def execute(self, request: CreateTaskRequest) -> Result:
        try:
            # 작업 시작 시점 로깅 (입력 데이터를 컨텍스트로 기록)
            logger.info(
                "Creating new task",
                extra={"title": request.title, "project_id": request.project_id},
            )

            # ... 작업 생성 로직 ...

            # 작업 완료 시점 로깅 (결과 데이터를 "context" 네임스페이스로 기록)
            # - "context" 키 사용으로 LogRecord 내장 속성과의 이름 충돌 방지
            logger.info(
                "Task created successfully",
                extra={"context":{
                    "task_id": str(task.id),
                    "project_id": str(project_id),
                    "priority": task.priority.name,
                }},
            )
            # ... 메서드의 나머지 부분