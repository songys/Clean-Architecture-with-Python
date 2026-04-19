import sys
import os
from uuid import UUID
import pytest

# conftest.py: pytest의 공유 픽스처(fixture) 설정 파일
# 테스트 디렉토리 계층별로 conftest.py를 두어 해당 계층의 테스트에서 공통으로 사용

# 프로젝트의 루트 디렉토리를 가져온다 (todo_app 패키지가 있는 곳)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
print(f"{root_dir}을(를) sys.path에 추가합니다")
sys.path.insert(0, root_dir)

# 이제 todo_app을 패키지로 임포트할 수 있다
