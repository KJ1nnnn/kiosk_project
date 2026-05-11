# 가상환경 명세서

## 프로젝트 정보

- 프로젝트명: 로컬 웹 기반 키오스크 시뮬레이터
- 프로젝트 폴더: `kiosk_project`
- 실행 방식: Flask 로컬 웹 서버
- 데이터베이스: SQLite
- 테스트 도구: pytest

## 개발 환경

| 항목 | 내용 |
| --- | --- |
| 운영체제 | macOS |
| Python 버전 | Python 3.13.9 |
| 웹 프레임워크 | Flask 3.1.2 |
| 템플릿 엔진 | Jinja2 |
| 데이터베이스 | SQLite |
| 테스트 프레임워크 | pytest 8.4.2 |

## 패키지 목록

`requirements.txt` 기준 필수 패키지는 다음과 같습니다.

```text
Flask
pytest
```

현재 개발 환경에서 확인한 주요 패키지 버전은 다음과 같습니다.

```text
Flask==3.1.2
pytest==8.4.2
```

## 가상환경 생성 방법

프로젝트 폴더로 이동합니다.

```bash
cd kiosk_project
```

가상환경을 생성합니다.

```bash
python -m venv .venv
```

가상환경을 활성화합니다.

macOS 또는 Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

필요 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

## 실행 방법

Flask 서버를 실행합니다.

```bash
python app.py
```

브라우저에서 접속합니다.

```text
http://127.0.0.1:5000
```

관리자 페이지는 다음 주소에서 접근합니다.

```text
http://127.0.0.1:5000/admin
```

관리자 비밀번호는 `0000`입니다.

## 테스트 방법

```bash
pytest
```

현재 테스트 범위는 다음과 같습니다.

- 잔돈 계산 알고리즘
- 현금/카드 결제 처리
- 재고 차감과 품절 판정
- 관리자 비밀번호 인증
- 결제 결과 화면 렌더링
- 시간대별 주문 통계
- 메뉴별 판매 통계

## SQLite 데이터베이스

`kiosk.db`는 로컬 실행 시 자동 생성되는 데이터 파일입니다. 실행 중 주문 내역, 상품 재고, 현금 보유량이 저장됩니다.

소스 코드 저장소에는 실행 산출물인 `kiosk.db`, `__pycache__`, `.pytest_cache`, `.venv`를 포함하지 않습니다.
