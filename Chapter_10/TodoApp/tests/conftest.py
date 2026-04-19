# pytest 설정 파일 - 테스트 실행 전 경로 설정
# - TodoApp 디렉토리를 sys.path에 추가하여 todo_app 패키지를 import 가능하게 설정
import sys
import os
from uuid import UUID
import pytest

# 프로젝트 루트 디렉터리 가져오기 (todo_app 패키지가 있는 위치)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
print(f"Adding {root_dir} to sys.path")
sys.path.insert(0, root_dir)

# 이제 todo_app을 패키지로 임포트할 수 있다
