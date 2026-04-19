# 10장

## 장별 코드 발췌
이 장에 등장하는 코드 스니펫은 `chapter_code_excerpts` 폴더에 등장 순서대로 있습니다. 예시: `00_error_class.py`
이 파일들은 참조용으로 제공되며, 직접 실행할 수 있는 코드는 아닙니다.

## 작업 관리 웹 애플리케이션 실행

리포지토리의 [README](../README.md)에 있는 환경 설정 지침을 따랐는지 확인하세요.

### 설정
애플리케이션은 환경 변수를 통한 설정을 지원합니다:

```bash
# 리포지토리 설정 옵션
export TODO_REPOSITORY_TYPE="memory"  # 또는 "file"
export TODO_DATA_DIR="repo_data"      # TODO_REPOSITORY_TYPE에 `file`을 선택한 경우 사용

# 선택 사항: 이메일 알림 설정
# 설정하지 않으면 기본적으로 (오프라인) NotificationRecorder를 사용합니다
# SendGrid 알림을 설정하려면 [SendGrid 계정](https://sendgrid.com/en-us/solutions/email-api)을 만들어야 합니다 (무료 티어 사용 가능)
export TODO_SENDGRID_API_KEY="your_api_key"
export TODO_NOTIFICATION_EMAIL="recipient@example.com"
```

### 애플리케이션 실행
```bash
cd Chapter_10/TodoApp
pytest
```
#### CLI 실행
```bash
python cli_main.py
```
#### 웹 실행
```bash
python web_main.py

# http://127.0.0.1:5000 으로 이동
```

## 역자 추가 코드 예제 노트북

이 장의 코드 예제는 Jupyter 노트북(`Chapter_10_코드예제.ipynb`)으로도 제공된다. [루트 README](../README.md)의 Colab 배지를 클릭하면 바로 실행할 수 있다. 셀을 위에서 아래로 순서대로 실행한다.

- 노트북 코드는 책의 코드 발췌와 동일하되, 노트북 환경에서 실행 가능하도록 일부 수정되었다.
- 수정된 부분은 `[추가]`, `[수정]`, `[보완]` 주석으로 표시되어 있다.
- 첫 번째 코드 셀에서 `TodoApp/` 소스 코드의 경로를 설정한다.