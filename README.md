# 학습 도구 대여·구매 키오스크 시뮬레이터

Python Flask, SQLite, Jinja2를 사용한 학교 1층 학습 도구 키오스크 시뮬레이터입니다. 실제 하드웨어 없이 웹 브라우저에서 대여 물품과 구매 물품 선택, 장바구니, 카드 결제, 현금 결제, 잔돈 계산, 재고 차감, 품절 표시, 반납 시뮬레이션, 관리자 확인을 실행할 수 있습니다.

## 사용 기술

- Python
- Flask
- SQLite
- HTML, CSS, Jinja2
- 최소한의 JavaScript
- pytest

## 언어별 사용 점유율

| 언어 | 사용 점유율 | 사용 위치 |
| --- | ---: | --- |
| Python | 58.5% | `app.py`의 Flask 라우팅, `database.py`의 SQLite 초기화, `services/`의 결제·잔돈·재고·주문 처리, `tests/`의 pytest 테스트에 사용 |
| HTML | 22.9% | `templates/`의 Jinja2 템플릿에서 메인 화면, 물품 선택, 장바구니, 결제, 학생증 태그, 반납, 관리자 화면 구성에 사용 |
| CSS | 18.0% | `static/css/style.css`에서 파란색 키오스크 테마, 터치형 버튼, 카드형 물품 목록, 관리자 표와 그래프 스타일에 사용 |
| JavaScript | 0.6% | `static/js/script.js`에서 수량 입력값이 최소·최대 범위를 벗어나지 않도록 보정하는 간단한 동작에 사용 사용자가 현재 재고보다 많은 수량을 입력했을때 즉시 수량을 줄여주는 동작을 브라우저에서 구현하기 위해 사용|

## 주요 기능

- 학습 도구 목록 조회
- 대여 물품과 구매 물품 구분 표시
- 품절 물품 비활성화
- 장바구니 담기, 수량 수정, 삭제
- 총 결제 금액 계산
- 대여 물품 선택 시 학생증 태그 안내 화면 표시
- 대여 물품은 결제 금액을 보증금으로 표시하고 반납 시 반환되는 흐름 시뮬레이션
- 메인 화면에서 물품 반납 시작
- 반납 시 학생증 태그 후 반납 완료 화면 표시
- 카드 결제 시뮬레이션
- 현금 결제 시뮬레이션
- 키오스크 내부 현금 보유량을 고려한 잔돈 계산
- 결제 성공 시 물품 재고 차감
- 주문 결과 영수증 화면
- 관리자 페이지에서 물품 정보, 재고, 주문 내역, 현금 보유량 확인
- 관리자 페이지에서 시간대별 주문 수, 물품별 이용량 그래프 확인
- 관리자 페이지에서 인기 물품 지정
- 인기 물품으로 지정된 물품은 선택 화면에 인기 배너 표시

## 샘플 물품

| 구분 | 물품 | 결제 성격 |
| --- | --- | --- |
| 대여 | 무선 마우스 | 보증금 |
| 대여 | 무선 키보드 | 보증금 |
| 대여 | 독서대 | 보증금 |
| 대여 | 담요 | 보증금 |
| 대여 | c타입 충전기 | 보증금 |
| 구매 | 일회용 칫솔 세트 | 구매 가격 |
| 구매 | 필기구 세트 | 구매 가격 |
| 구매 | 인공눈물 | 구매 가격 |
| 구매 | 졸음껌 | 구매 가격 |
| 구매 | 머리끈 | 구매 가격 |
| 구매 | 에너지 드링크 | 구매 가격 |
| 구매 | 포스트잇 | 구매 가격 |

## 관리자 비밀번호

- 관리자 페이지 주소: `http://127.0.0.1:5000/admin`
- 비밀번호: `0000`

## 실행 방법

```bash
cd kiosk_project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

브라우저에서 다음 주소를 엽니다.

```text
http://127.0.0.1:5000
```

만약 macOS에서 5000번 포트가 이미 사용 중이면 다음처럼 5001번 포트로 실행할 수 있습니다.

```bash
flask --app app run --debug --port 5001
```

처음 실행하면 `kiosk.db` 파일이 자동으로 생성되고 샘플 물품과 현금 보유량이 저장됩니다.

## 테스트 실행

```bash
cd kiosk_project
pytest
```

테스트 대상은 다음 핵심 Python 로직과 화면 흐름입니다.

- `services/change_service.py`: 잔돈 계산
- `services/product_service.py`: 재고 확인과 차감
- `services/payment_service.py`: 카드/현금 결제 검증
- `app.py`: 관리자 비밀번호, 대여 학생증 태그, 반납 흐름

## 프로젝트 구조

```text
kiosk_project/
├─ app.py
├─ database.py
├─ models.py
├─ requirements.txt
├─ README.md
├─ kiosk.db
├─ services/
│  ├─ product_service.py
│  ├─ order_service.py
│  ├─ payment_service.py
│  └─ change_service.py
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  ├─ menu.html
│  ├─ cart.html
│  ├─ payment.html
│  ├─ result.html
│  ├─ student_tag.html
│  ├─ return.html
│  ├─ return_result.html
│  └─ admin.html
├─ static/
│  ├─ css/
│  │  └─ style.css
│  ├─ js/
│  │  └─ script.js
│  └─ images/
└─ tests/
   ├─ test_change_service.py
   ├─ test_stock_service.py
   ├─ test_payment_service.py
   ├─ test_admin_auth.py
   ├─ test_result_route.py
   ├─ test_sales_stats.py
   └─ test_rental_flow.py
```

## 핵심 알고리즘

현금 결제 시 `calculate_change(change_amount, cash_box)` 함수가 큰 화폐 단위부터 사용 가능한 수량만큼 선택합니다. 끝까지 계산했을 때 남은 거스름돈이 0이면 성공이고, 남으면 키오스크 내부 잔돈 부족으로 결제 실패 처리합니다.

예시:

```python
calculate_change(3700, {1000: 5, 500: 2, 100: 10})
# 결과: {1000: 3, 500: 1, 100: 2}
```

## 팀원 역할 예시

- Flask 라우트 및 화면 연결
- SQLite 테이블 설계 및 초기 데이터 구성
- 잔돈 계산, 결제 처리, 재고 차감 서비스 구현
- 대여 학생증 태그와 반납 흐름 구현
- HTML/CSS 화면 구성
- pytest 테스트 작성 및 발표 자료 정리
