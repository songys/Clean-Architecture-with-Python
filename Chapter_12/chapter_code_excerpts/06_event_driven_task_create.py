# === 올바른 이벤트 드리븐 클린 아키텍처 패턴 ===
# 도메인 엔터티는 순수 비즈니스 로직만 담당하고,
# 이벤트 발행은 애플리케이션 계층(유스 케이스)이 추상 인터페이스를 통해 처리하는 구조

# 클린 도메인 엔터티 - 메시징 의존성 없음
# 이전 안티패턴과 달리 Kafka 등 외부 시스템에 대한 의존이 전혀 없는 순수한 도메인 객체
# 비즈니스 규칙(상태 변경, 검증)만 포함하므로 독립적으로 단위 테스트가 가능
class Task:
    def complete(self, user_id: UUID) -> None:
        # 비즈니스 규칙: 이미 완료된 작업은 다시 완료할 수 없는 불변 조건(invariant)
        if self.status == TaskStatus.DONE:
            raise ValueError("이미 완료된 작업")
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.completed_by = user_id


# 애플리케이션 계층이 이벤트 생성을 처리함
# 유스 케이스가 도메인 작업과 이벤트 발행을 조율(orchestration)하는 역할
@dataclass
class CompleteTaskUseCase:
    task_repository: TaskRepository
    # 구현이 아닌 추상 인터페이스에 의존 (의존성 역전 원칙, DIP)
    # 실제 구현체(Kafka, RabbitMQ 등)는 인프라 계층에서 주입
    event_publisher: EventPublisher

    def execute(self, task_id: UUID, user_id: UUID) -> Result:
        try:
            # 1단계: 리포지토리에서 작업 엔터티 조회
            task = self.task_repository.get_by_id(task_id)
            # 2단계: 도메인 엔터티의 비즈니스 로직 실행
            task.complete(user_id)
            # 3단계: 변경된 엔터티를 리포지토리에 저장
            self.task_repository.save(task)

            # 4단계: 도메인 이벤트를 생성하고 추상 인터페이스를 통해 발행
            # 이벤트 발행이 도메인이 아닌 애플리케이션 계층에 위치하는 것이 핵심
            event = TaskCompletedEvent.from_task(task, user_id)
            self.event_publisher.publish(event)

            return Result.success(task)
        except ValueError as e:
            # 도메인 예외를 Result 패턴으로 변환하여 상위 계층에 전달
            return Result.failure(Error(str(e)))
