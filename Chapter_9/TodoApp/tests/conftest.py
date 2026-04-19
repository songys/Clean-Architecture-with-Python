import sys
import os
from uuid import UUID
import pytest

# 테스트 실행 시 todo_app 패키지를 import할 수 있도록 경로 설정
# 프로젝트의 루트 디렉터리를 가져옴 (todo_app 패키지가 있는 곳)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
print(f"{root_dir}을(를) sys.path에 추가")
sys.path.insert(0, root_dir)

# 이제 todo_app을 패키지로 임포트할 수 있음
