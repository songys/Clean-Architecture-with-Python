# 테스트 루트 설정 파일
# - pytest가 테스트 실행 시 todo_app 패키지를 import할 수 있도록 경로 설정
# - TodoApp 디렉토리를 sys.path에 추가하여 패키지 경로 해결

import sys
import os

# 프로젝트 루트 디렉터리를 가져온다 (todo_app 패키지가 있는 곳)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
print(f"sys.path에 {root_dir} 추가")
sys.path.insert(0, root_dir)

# 이제 todo_app을 패키지로 임포트할 수 있다