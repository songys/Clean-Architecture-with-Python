# ============================================================
# SRP 적용 후의 유닛 테스트
# 단일 책임을 가진 PostManager를 독립적으로 테스트하는 예제
# SRP 덕분에 복잡한 모의 객체 없이 간결한 테스트 작성 가능
# ============================================================

import unittest

from post_manager import PostManager
from user import User


# PostManager의 게시물 생성 기능을 검증하는 테스트 클래스
class TestPostManager(unittest.TestCase):
    # 게시물 생성 시 사용자 ID, 내용, 좋아요 수, 게시물 ID의 정확성 검증
    def test_create_post(self):
        user = User("123", "testuser", "test@example.com")
        post_manager = PostManager()
        post = post_manager.create_post(user, "Hello, world!")

        self.assertEqual(post["user_id"], "123")      # 사용자 ID 일치 여부
        self.assertEqual(post["content"], "Hello, world!")  # 게시물 내용 일치 여부
        self.assertEqual(post["likes"], 0)             # 초기 좋아요 수 (0)
        self.assertIn("id", post)                      # 게시물 ID 존재 여부
