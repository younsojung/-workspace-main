---
name: trus-design-palette
description: "\"트루스 디자인\"으로 해달라고 하면 반드시 이 3색 사용 — TRUS BLACK #121212 / TRUE WHITE #FFFFFF / EDUCATE PINK #D84D8D"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c0fff2e4-4df1-4e0d-b0a3-fffc16de1dde
---

**"트루스 디자인으로 해줘"라고 하면 반드시 TRUS 공식 3색을 쓴다:**

- **TRUS BLACK** `#121212` — 텍스트·잉크·1차 버튼
- **TRUE WHITE** `#FFFFFF` — 기본 배경
- **TRUE EDUCATE PINK** `#D84D8D` — 시그니처 액센트 (로즈핑크)

**핑크는 절제 — 화면의 5% 미만, 액센트 전용.** 핵심 강조 1개·활성 상태·링크·작은 하이라이트에만. 넓은 면적·배경·본문 다수에 ❌.

브랜드 서사: **틀에박힌(BOUND) → 깨어나는(AWAKENING) → 확장되는(EXPANDING)** — 핑크 = 각성·변화.

**Why:** 사용자가 "내가 트루스 디자인으로 해줘 하면 이 컬러를 꼭 사용해줘야 해"라고 명시 (2026-05-24). 무드보드로 HEX 직접 제공.

**How to apply:** 사이트·카드뉴스·핸드아웃·대시보드 등 "트루스/TRUS 디자인" 요청 시 이 팔레트를 CSS 변수로 깐다. 타이포는 [[feedback-typography-vignelli]](비넬리 비율) + [[feedback-typography-linebreak]](호흡 줄바꿈) + 제목 Pretendard·본문 명조. 풀 가이드: 10-projects/younsojung-site-renewal/design/design-guide.md.

**웹·인터랙션 레이어 (2026-05-25, Stripe Press 학습):** 버튼·웹·모션은 `press.stripe.com`을 레퍼런스로 이식(폰트·컬러는 TRUS 유지). 실행본은 `trus-design.css` 하단 "웹·인터랙션 레이어" — 이징 2개(`--ease-out`/`--ease-hover`), `.btn` 포커스 링·pointer 분기, `.card-interactive`(잉크 반전), `.hover-label`, `.framed`, `.rise`. 데모: `design/web-components.html`. 위키 [[트루스-디자인-시스템]] 참조.
