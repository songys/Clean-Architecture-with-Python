# 9장: 웹 UI 추가: 클린 아키텍처의 인터페이스 유연성

## 장 코드 발췌
이 장에서 발췌한 코드 조각은 `chapter_code_excerpts` 폴더에 등장 순서대로 정리되어 있다. 예시: `00_error_class.py`
이 코드들은 참고용이며 직접 실행할 수 있도록 만들어진 것은 아니다.

## 동반 작업 관리 애플리케이션

저장소의 [README](../README.md)에 있는 환경 설정 지침을 따라 환경을 구성했는지 확인하자.

pytest를 사용하여 모든 테스트를 실행한다:
```bash
cd Chapter_9/TodoApp
pytest
```

### 구성
애플리케이션은 환경 변수를 통한 구성을 지원한다:

```bash
# 리포지토리 구성
export TODO_REPOSITORY_TYPE="memory"  # 또는 "file"
export TODO_DATA_DIR="repo_data"      # 파일 리포지토리와 함께 사용

# 선택사항: 이메일 알림 구성
# 설정하지 않으면 (오프라인) NotificationRecorder가 기본값으로 사용됨
export TODO_SENDGRID_API_KEY="your_api_key"
export TODO_NOTIFICATION_EMAIL="recipient@example.com"
```

### 애플리케이션 실행
```bash
cd Chapter_9/TodoApp
pytest

python web_main.py
```

## 역자 추가 코드 예제 노트북

이 장의 코드 예제는 Jupyter 노트북(`Chapter_9_코드예제.ipynb`)으로도 제공된다. [루트 README](../README.md)의 Colab 배지를 클릭하면 바로 실행할 수 있다. 셀을 위에서 아래로 순서대로 실행한다.

- 노트북 코드는 책의 코드 발췌와 동일하되, 노트북 환경에서 실행 가능하도록 일부 수정되었다.
- 수정된 부분은 `[추가]`, `[수정]`, `[보완]` 주석으로 표시되어 있다.
- 첫 번째 코드 셀에서 `TodoApp/` 소스 코드의 경로를 설정한다.