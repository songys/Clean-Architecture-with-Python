# === 안티패턴: 도메인 엔터티 내부의 인프라 의존성 ===
# 도메인 엔터티가 Kafka 같은 외부 메시징 시스템에 직접 의존하는 잘못된 설계
# 클린 아키텍처의 의존성 규칙(Dependency Rule) 위반 사례

# 안티패턴: 도메인 엔터티가 직접 이벤트를 발행
class Task:
    # complete() 메서드가 비즈니스 로직과 인프라 관심사를 혼합하고 있는 상태
    def complete(self, user_id: UUID):
        # --- 비즈니스 로직 영역 ---
        self.status = TaskStatus.DONE
        self.completed_at = datetime.now()
        self.completed_by = user_id

        # --- 인프라 관심사 영역 (여기서부터 문제) ---
        # 메시징 시스템에 대한 직접 의존성 – 클린 아키텍처 위반
        # 문제점 1: 도메인 엔터티가 Kafka라는 특정 기술에 직접 결합
        # 문제점 2: 단위 테스트 시 Kafka 서버가 필요하여 테스트 어려움
        # 문제점 3: 메시징 시스템 교체(예: RabbitMQ, SQS) 시 도메인 코드 수정 필요
        kafka_producer = KafkaProducer(bootstrap_servers='kafka:9092')
        event_data = {
            "task_id": str(self.id),
            "completed_by": str(user_id),
            "completed_at": self.completed_at.isoformat()
        }
        # 도메인 계층에서 인프라 계층으로의 직접 호출 — 의존성 방향 역전
        kafka_producer.send('task_events', json.dumps(event_data).encode())