---
name: trus-design
description: 트루스(TRUS) 공식 디자인 시스템을 적용. 사이트·랜딩·카드뉴스·핸드아웃 등 시각물을 TRUS 브랜드 톤(비넬리 타이포·호흡 줄바꿈·기능별 폰트·TRUS 3색)으로 만든다. "트루스 디자인", "TRUS 디자인", "trus design", "트루스 브랜드로", "트루스 스타일로", "TRUS 톤으로" 등을 언급하면 자동 실행.
allowed-tools:
  - Read
  - Write
  - Edit
---

# TRUS Design — 트루스 공식 디자인 시스템

> **큰 글씨로 외치지 않는다. 절제·호흡·여백으로 *읽히게* 만든다.**
> 위계는 크기가 아니라 굵기·여백·위치로. 강조는 딱 한 곳에만.

HTML/시각물을 만들 때 **아래 핵심 토큰을 `:root`에 깔고** 규칙을 따른다. (자체 완결 — 외부 파일 불필요)

## 핵심 토큰 (복사해서 사용)
폰트 2줄을 `<head>`에:
```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
```
```css
:root{
  --black:#121212; --white:#FFFFFF; --pink:#D84D8D;                 /* TRUS 3색 */
  --display:'Pretendard Variable',Pretendard,system-ui,sans-serif;  /* 제목·라벨·짧은 선언 */
  --serif:'Noto Serif KR',serif;                                    /* 여러 줄 흐르는 본문 */
  --t-s:.8rem; --t-body:.9375rem; --t-m:1.25rem; --t-l:1.563rem; --t-xl:1.953rem; /* 13·15·20·25·31 */
}
body{ font-family:var(--display); color:var(--black); background:var(--white);
  font-size:var(--t-body); line-height:1.7; word-break:keep-all; text-wrap:pretty; }
```

## 규칙 (핵심 4 + 절제)
1. **비넬리 타이포** — 크기는 13·15·20·25·31 다섯뿐, 비율 1.25. **디스플레이도 본문의 2배 이내**(31px 상한). 강조는 크기 ❌ → 굵기(400/500/700)·여백.
2. **기능별 폰트** — 제목·라벨·짧은 선언 = Pretendard / 여러 줄 흐르는 본문 = 명조. 본문 15px, 행간 1.6~1.7, 제목 1.1~1.3, 자간 0.
3. **호흡 줄바꿈** — 소리 내어 읽어 숨 쉬는 자리에서 `<br>`. **짧은 핵심 문장·리드에만**, 긴 본문은 붙여서. 조사·단일 음절이 줄 끝에 외톨이로 떨어지면 ❌(keep-all, 안 되면 크기 조절). 붙인 본문=양쪽정렬+`word-break:normal`, 짧은 문장=왼쪽정렬+keep-all. 데스크탑 `<br>`은 모바일에서 끔.
4. **TRUS 3색** — BLACK #121212(텍스트·버튼) / WHITE #FFFFFF(배경) / **EDUCATE PINK #D84D8D**. 핑크는 **화면 5% 미만** — 핵심 강조 한 곳·링크·활성 상태에만. 넓은 면적 ❌.
5. **여백·컴포넌트** — 8의 배수, 섹션 사이 80px+. 읽는 본문 한 줄 폭 640~720px 중앙. **그림자 ❌ → 1px hairline 보더.** 버튼은 잉크 블랙, hover 시 채움↔외곽선 반전.

## Do / Don't
- **Do**: 굵기·여백으로 위계 / 본문 15px·행간 1.6~1.7 / 붙인 본문 양쪽정렬 / 핑크 한 곳만 / `word-break:keep-all`.
- **Don't**: 글씨 키워 강조 ❌ / 폰트 3종+ ❌ / 한글 음수 자간 ❌ / 조사 외톨이 ❌ / 화려한 컬러·그림자 ❌.

---
출처: 윤소정/트루스 디자인 가이드 (2026-05-24). 카드뉴스·핸드아웃·사이트 공통.
