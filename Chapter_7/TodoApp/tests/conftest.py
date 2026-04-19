import sys
import os

# 프로젝트의 루트 디렉터리를 가져온다 (todo_app 패키지가 있는 곳)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
print(f"Adding {root_dir} to sys.path")
sys.path.insert(0, root_dir)

# 이제 todo_app을 패키지로 임포트할 수 있다