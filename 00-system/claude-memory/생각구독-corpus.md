---
name: corpus
description: 윤소정 작가의 <생각구독> 80호 전수 분석 코퍼스 위치와 활용 가이드
metadata: 
  node_type: memory
  type: reference
  originSessionId: 50bf834f-0237-420d-ae6c-e1d753941833
---

윤소정 작가 <생각구독> 1호~80호(2019.10~2026.4) 전수 분석 코퍼스가 구축되어 있다.

## 자산 위치

| 자료 | 경로 |
|---|---|
| 원본 PDF 80개 | `/Users/sojungyoun/Desktop/claude/writer/전체호/` |
| 정제 마크다운 | `/Users/sojungyoun/Desktop/claude/writer/전체호-md/_clean/` |
| 호별 카드 80개 | `/Users/sojungyoun/Desktop/claude/workspace-main/30-knowledge/생각구독-corpus/_cards/호NN.md` |
| 통합 분석 5종 | `/Users/sojungyoun/Desktop/claude/workspace-main/30-knowledge/생각구독-corpus/_aggregations/` |

## 통합 분석 산출물

- `concepts-dataset.md` — 80호 메인+부제 전수 + 12 메인 / 9 부제 패턴
- `signature-expressions.md` — 어투·표현 카탈로그 (13 섹션)
- `people-catalog.md` — 반복 인물 (가족·동료·멘토·외부 인용)
- `openings-closings.md` — 5 오프닝 / 6 단계 클로징 / 4단 호명 리듬
- `themes-frames.md` — 8 대 테마 + 비유·메타퍼 풀

## 봇 연동

`yoonsojung-bot` 스킬의 `voice_reference.md`가 80호 베이스로 전면 개정됨 (2026-05-19). 봇이 본문 쓸 때 이 코퍼스를 grep·인용한다.

## 활용 패턴

- 새 호 컨셉 잡을 때 → `concepts-dataset.md` 12 유형에서 선택
- 본문 쓸 때 어휘 풀 → `signature-expressions.md`
- 일화 인용할 때 → `people-catalog.md`에서 인물 픽
- 비슷한 주제의 과거 호 → `_cards/`에서 grep
- 비유 선택 → `themes-frames.md`의 시그니처 메타퍼 풀

## 변환·구축 비화

- pdf-to-md 스킬이 Python 3.10+ 타입힌트를 써서 3.9에서 실패 → `from __future__ import annotations` 한 줄로 패치 (다른 사용자도 같은 문제 겪을 가능성)
- 47호("가치를 생각하며")가 폰트 임베딩 오류로 pymupdf4llm 실패 → pymupdf 직접 호출로 복구
- 분석-워커 8개씩 디스패치하면 600s watchdog에 stall — **워커당 3호 이하 + 즉시-Write 지시**가 안정적

Related: [[user-profile]] · [[workspace-layout]]
