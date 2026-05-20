# 생각구독 Corpus — 윤소정 작가 80호 분석 자산

> 80호 (2019.10 ~ 2026.4) 전수 분석 결과. `yoonsojung-bot` 스킬이 본문 쓸 때 레퍼런스로 사용.

## 폴더 구조

```
생각구독-corpus/
├── README.md            ← 이 파일
├── _cards/              ← 호별 추출 카드 (80개)
│   ├── 호01.md ~ 호80.md
└── _aggregations/       ← 통합 분석 산출물
    ├── _all_cards.md           (80호 카드 통합 원문)
    ├── concepts-dataset.md     (메인+부제 80호 전수 + 12 유형 메인·9 유형 부제 패턴)
    ├── signature-expressions.md (어투·표현 카탈로그)
    ├── people-catalog.md       (반복 등장 인물 카탈로그)
    ├── openings-closings.md    (오프닝·클로징 패턴)
    └── themes-frames.md        (8 대 테마·비유·프레임)
```

## 원본 소스

| 종류 | 위치 |
|---|---|
| PDF 원본 80개 | `/Users/sojungyoun/Desktop/claude/writer/전체호/` |
| 변환 마크다운 (raw) | `/Users/sojungyoun/Desktop/claude/writer/전체호-md/` |
| 정제 마크다운 | `/Users/sojungyoun/Desktop/claude/writer/전체호-md/_clean/` |
| 스켈레톤 (오프닝/클로징/마커) | 상동 `_skeletons/` |

## 카드 스키마

각 카드는 다음 필드를 포함:

```yaml
---
호: NN
title: "메인 제목"
subtitle: "부제 (있을 시)"
estimated_year_month: "YYYY-MM"
tags: [태그1, 태그2, 태그3]
---

## 메인 컨셉 (한 줄)
## 부제
## 오프닝 발췌 (원문 그대로)
## 클로징 발췌 (원문 그대로)
## 챕터 목록
## 핵심 일화 (3-5개)
## 인용 인물 (실명/관계)
## 시그니처 표현 (5-10개)
## 비유/프레임
## 라이브/플레이리스트
## 한 줄 요약
```

## 사용처

1. **봇 본문 작성 시 어투 참조**: `signature-expressions.md`
2. **컨셉 잡기 시 패턴 선택**: `concepts-dataset.md` (12 메인 + 9 부제 유형)
3. **인물 인용 시**: `people-catalog.md`
4. **오프닝/클로징 작성 시**: `openings-closings.md`
5. **비유 선택 시**: `themes-frames.md`

## 작성 이력

- 2026-05-19: 초판 구축 (80호 전수 변환·카드·통합 분석)
- Phase 1: PDF→MD 변환 (병렬 6 워커, 1 PDF 폰트 임베딩 문제 → pymupdf 직접 추출로 복구)
- Phase 2: 호별 추출 카드 80개 생성 (스켈레톤 기반 + 직접 작성 혼합)
- Phase 3: 통합 분석 파일 5개 (concepts / signature / people / openings-closings / themes-frames)
- Phase 4: yoonsojung-bot 스킬의 voice_reference.md 전면 개정 (다음 단계)
