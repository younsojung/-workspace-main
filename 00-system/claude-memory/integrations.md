---
name: integrations
description: Notion/Gmail/Calendar/Drive MCP 채널 상태 + gws CLI 부재
metadata: 
  node_type: memory
  type: reference
  originSessionId: a984fe46-d00f-46cb-a5d7-871b1bfd6910
---

## 2026-05-19 시점 점검 결과

### ✅ Claude MCP 채널 (전부 연결됨)

| 도구 | 상태 | 비고 |
|------|------|------|
| Notion | ✅ | `sojung youn` / insung.inq@gmail.com |
| Gmail | ✅ | 라벨: Notes (1개) |
| Google Calendar | ✅ | 6개 캘린더: 대한민국 휴일, 💚앤드엔, 운이 좋은날(주캘린더), 트루스, 소정&황호, 🖤TRUS GROUP |
| Google Drive | ✅ | 최근 파일: 앤드엔 글 통합본, THINK MARATHON (응답) 등 |

### ❌ 로컬 CLI

- `gws` CLI: **미설치** (CLAUDE.md에 언급된 `~/.nvm/versions/node/...` 경로 존재하지 않음, nvm도 없음)
- `gh` CLI: **미설치**
- `brew`: **미설치**

### 대응 원칙

- Gmail/Calendar/Drive/Notion 작업은 **MCP로 직접 호출** (gws 우회)
- `daily-note` 스킬 등이 gws를 호출하면 실패할 수 있음 → MCP로 대체 가능한지 확인 필요

## 주요 캘린더 ID (Calendar MCP 호출용)

- `insung.inq@gmail.com` — 운이 좋은날 (주캘린더)
- `b5b55b...` — 트루스
- `7735f6...` — 🖤TRUS GROUP
- `84e745...` — 💚앤드엔
- `5616e4...` — 소정&황호
- `ko.south_korea#holiday@group.v.calendar.google.com` — 대한민국 휴일

## Related

[[github-setup]] · [[workspace-layout]]
