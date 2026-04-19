# ============================================================
# SRP(단일 책임 원칙) 적용 후 - 리팩토링 완료
# 기존 User 클래스의 여러 책임을 각각 독립된 클래스로 분리한 구조
# 각 클래스가 하나의 변경 이유만 가지도록 설계
# ============================================================


# User 클래스: 사용자 데이터만 보관하는 순수 엔티티
# 게시물, 타임라인, 프로필 수정 로직은 모두 별도 클래스로 분리
class User:
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email


# 게시물 관리 전담 클래스 - 게시물 생성/관리 책임만 보유
class PostManager:
    # User 객체를 매개변수로 받아 게시물 생성 (User와의 느슨한 결합)
    def create_post(self, user: User, content: str):
        post = {
            "id": self.generate_post_id(),
            "user_id": user.user_id,
            "content": content,
            "likes": 0,
        }
        # 게시물 저장 로직
        return post

    # 게시물 고유 ID 생성 담당 메서드
    def generate_post_id(self):
        # 고유한 게시물 ID 생성 로직
        pass


# 타임라인 서비스 전담 클래스 - 타임라인 조회 책임만 보유
class TimelineService:
    def get_timeline(self, user: User) -> list:
        # 사용자의 타임라인을 가져와 반환
        # 팔로우 중인 사용자들의 게시물을 가져오고 정렬하는 복잡한 로직이 필요할 수 있음
        pass


# 프로필 관리 전담 클래스 - 프로필 수정 책임만 보유
class ProfileManager:
    def update_profile(
        self, user: User, new_username: str = None, new_email: str = None
    ):
        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email
        # 프로필 업데이트를 위한 추가 로직, 이메일 인증 트리거 등
