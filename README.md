# 로컬 웹 기반 키오스크 시뮬레이터

Python Flask, SQLite, Jinja2를 사용한 학교 1층 키오스크 시뮬레이터입니다. 실제 하드웨어 없이 웹 브라우저에서 상품 선택, 장바구니, 카드 결제, 현금 결제, 잔돈 계산, 재고 차감, 품절 표시, 관리자 확인을 실행할 수 있습니다.

## 사용 기술

- Python
- Flask
- SQLite
- HTML, CSS, Jinja2
- 최소한의 JavaScript
- pytest

## 주요 기능

- 상품 목록 조회
- 품절 상품 비활성화
- 장바구니 담기, 수량 수정, 삭제
- 총 결제 금액 계산
- 카드 결제 시뮬레이션
- 현금 결제 시뮬레이션
- 키오스크 내부 현금 보유량을 고려한 잔돈 계산
- 결제 성공 시 상품 재고 차감
- 주문 결과 영수증 화면
- 관리자 페이지에서 상품 정보, 재고, 주문 내역, 현금 보유량 확인
- 관리자 페이지에서 시간대별 주문 수, 메뉴별 판매량 그래프 확인
- 관리자 페이지에서 인기 메뉴 지정
- 인기 메뉴로 지정된 상품은 상품 화면에 인기 배너 표시

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

처음 실행하면 `kiosk.db` 파일이 자동으로 생성되고 샘플 상품과 현금 보유량이 저장됩니다.

## 테스트 실행

```bash
cd kiosk_project
pytest
```

테스트 대상은 다음 핵심 Python 로직입니다.

- `services/change_service.py`: 잔돈 계산
- `services/product_service.py`: 재고 확인과 차감
- `services/payment_service.py`: 카드/현금 결제 검증

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
   └─ test_payment_service.py
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
- HTML/CSS 화면 구성
- pytest 테스트 작성 및 발표 자료 정리
