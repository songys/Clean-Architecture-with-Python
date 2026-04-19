# ============================================================
# SRP(단일 책임 원칙) 위반 사례 - 리팩토링 전
# User 클래스가 사용자 데이터 관리, 게시물 생성, 타임라인 조회,
# 프로필 수정 등 여러 책임을 동시에 담당하는 구조
# ============================================================


# SRP 위반: 하나의 클래스가 4가지 책임(사용자 정보, 게시물, 타임라인, 프로필)을 모두 보유
class User:
    def __init__(self, user_id: str, username: str, email: str):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.posts = []  # 게시물 목록 - 사용자 데이터와 무관한 별도 책임

    # 책임 #1: 게시물 생성 기능 (별도 클래스로 분리해야 할 대상)
    def create_post(self, content: str) -> dict:
        post = {"id": len(self.posts) + 1, "content": content, "likes": 0}
        self.posts.append(post)
        return post

    # 책임 #2: 타임라인 조회 기능 (별도 서비스로 분리해야 할 대상)
    def get_timeline(self) -> list:
        # 사용자의 타임라인을 가져와 반환
        # 팔로우 중인 사용자의 게시물을 가져오고
        # 정렬하는 복잡한 로직이 필요할 수 있음
        pass

    # 책임 #3: 프로필 수정 기능 (별도 매니저로 분리해야 할 대상)
    def update_profile(self, new_username: str = None, new_email: str = None):
        if new_username:
            self.username = new_username
        if new_email:
            self.email = new_email
