# 채산 대시보드 — 운영 가이드

> 매월 통장·카드 데이터를 넣으면 자동으로 분류·집계되는 시스템.

## 📁 구조

```
10-projects/채산-대시보드/
├── 00-설계.md                  # 전체 설계 문서
├── README.md                  # 이 파일 (운영 가이드)
├── config/                    # 분류 규칙 (사람이 읽고 수정)
│   ├── taxonomy.yaml          # 지출 항목 + 자동 분류 규칙
│   ├── revenue.yaml           # 매출 분류
│   └── exclusions.yaml        # 영업외/제외 항목
├── data/
│   ├── raw/                   # 원본 (월별로 누적)
│   ├── processed/
│   │   └── transactions.csv   # 분류된 거래 단위
│   └── unclassified.csv       # 자동 분류 실패 (사용자 검토용)
├── src/
│   └── classify.py            # 분류 엔진
└── outputs/                   # (다음 단계: 월별 집계, 대시보드)
```

## 🔁 매월 운영 절차

### 1. 원본 데이터 받기
- 통장 입출금: 은행에서 CSV 다운로드 → `data/raw/bank_YYYYMM.csv`로 저장
- 카드 사용내역: 카드사에서 XLS 다운로드 → `data/raw/card_YYYYMM.xls`로 저장

### 2. 분류 실행
```bash
cd 10-projects/채산-대시보드
source ../../.venv/bin/activate
python3 src/classify.py [bank_csv_path] [card_xls_path]
```

### 3. 미분류 검토
- `data/unclassified.csv`에 50만 이상 미분류 거래만 모임
- 1만 이상 자잘한 거래는 자동으로 `OPEX-MISC-AUTO`로 fallback
- 검토 후 분류가 명확해지면 `config/*.yaml`에 키워드 추가

### 4. 결과 확인
- `data/processed/transactions.csv` — 거래 단위 분류 결과
- 콘솔 출력에 카테고리별 합계 표시

## ✏️ 새 거래처가 생겼을 때

`config/taxonomy.yaml`을 열고 해당 카테고리의 `rules`에 키워드 추가:

```yaml
OPEX-DINE:
  rules:
    - source: card
      ujong_contains: [...]
    - source: card
      merchant_contains: [우아한형제들, 컬리페이, 새거래처]  # ← 여기 추가
```

## 🏗 분류 체계 (대분류 9개)

| 코드 | 대분류 | 6개월 합계 |
|------|--------|-----------:|
| REV  | 매출 | 1,114,316,732 |
| -    | 매출차감 (환불) | -15,700,090 |
| COGS | 매출원가 | 25,369,000 |
| RENT | 임대료 | 69,631,400 |
| LABOR | 인건비 (정규+외주+4대보험+퇴직금) | 359,214,255 |
| MGMT | 관리비 | 1,828,969 |
| OPEX | 운영비 | 83,242,927 |
| TAX  | 세금 | 10,945,110 |
| NONOP | 영업외 (트루스·본인이체·이자·환급) | (제외) |

**6개월 영업이익**: 약 5.49억 (이익률 49.9%)

## ⚙️ 시스템 특징

1. **YAML 기반 규칙** — 코드 안 건드리고 분류 추가 가능
2. **명시적 매칭만** — 모호한 광범위 룰 없음 (예: "법인은 다 매출원가" 같은 위험한 규칙 제거)
3. **소액 자동 fallback** — 50만 미만 미분류는 운영비 기타로 자동 처리
4. **매월 검토 항목** — 네이버파이낸셜처럼 가맹점 정보 없는 결제는 `OPEX-REVIEW`로 별도 표시
5. **영업외 분리** — 트루스 투자·본인 이체·카드 출금은 채산표에서 빠짐 (중복 계산 방지)

## 📋 다음 단계

1. `aggregate.py` — 월별 채산표 생성 (`outputs/monthly_pnl.csv`)
2. `dashboard.py` — Streamlit 대시보드 또는 정적 HTML
3. `ingest.py` — 신규 raw 파일 자동 추가 처리

---
_작성일: 2026-05-19_
