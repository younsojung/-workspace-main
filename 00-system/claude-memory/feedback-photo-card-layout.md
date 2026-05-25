---
name: feedback-photo-card-layout
description: 윤소정 정지사진 인스타 카드 정렬법(레이아웃 시스템) — 다음에도 이 방식으로 작업
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ed35d941-99bc-4f0f-9470-a9b3d7c9e675
---

윤소정의 **정지 사진** 인스타 카드(캐러셀) 제작 시 확정된 정렬법. (2026-05 리코 카메라 카드 12장에서 정립, "잘했어, 다음에도 이 정렬법 기억해서 작업하자")

**기본 스펙**: 1080×1350(4:5) · 하단/상단 그라데이션 dim · 흰색 글씨 + 부드러운 그림자(GaussianBlur 6) · EXIF 회전 자동 보정.

**정렬 패턴**
- **기본(가장 선호)**: 가운데 정렬 · 하단 · 작은 균일 명조(~34px). (사용자가 "08번 스타일 제일 예쁘다"고 확정)
- 대사("…") 상단 + 고백 하단으로 분리 (위/아래 호흡)
- 상단·하단 수직 분리(여백 살리기) / B형: 상단좌 메인 + 하단우 에코
- 강조는 크기 아님 — 굵기·여백·위치로. [[feedback-typography-vignelli]]
- 줄바꿈은 소리내 읽어 숨 쉬는 자리에서. [[feedback-typography-linebreak]]

**폰트 (designer/ricoh/fonts/ 에 설치됨)**
- 흐르는 본문/고백 = **부크크 명조**(BookkMyungjo Light/Bold)
- 포인트/모던 = **Pretendard**
- 반전·손글씨 포인트 = **제주돌담체**(JejuDoldam, 얼리폰트 무료)

**기법**
- 가로 사진은 잘라내지 말고 **레터박스(fit_contain)**로 전체 보존 (손글씨·문서 컷 필수)
- 상단 **아치(곡선) 텍스트** 옵션 있음 (글자 한 자씩 원호 회전)
- 정지 사진은 영상화하지 않고 정지 카드로 (cardnews 스킬은 영상용, 이건 정지 변형)

**재사용 자산**: `~/Desktop/claude/designer/ricoh/make_cards.py` (카드 정의 dict 배열 + render 파이프라인). 새 카드 작업 시 이 스크립트 복제/수정.

**작업 방식**: 카피는 사용자가 카드별 1줄씩 빠르게 던짐 → 즉시 반영 → 620px 썸네일로 미리보기 확인 → `open` 자동 → `원고.md` 동기화. 묻기보다 만들어 보여주고 피드백 받기. [[feedback-definition-consent]] · [[younsojung-photo-identity]] · [[trus-design-palette]]
