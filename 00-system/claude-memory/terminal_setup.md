---
name: terminal-setup
description: 사용자의 Claude Code 실행 환경은 iTerm2 + D2Coding 폰트. Terminal.app은 쓰지 않음 (한글 깨짐)
metadata: 
  node_type: memory
  type: project
  originSessionId: f31b94d1-8c9d-48fa-89a9-6b13d6351c07
---

사용자는 Claude Code를 **iTerm2**에서 실행한다. macOS 기본 Terminal.app은 쓰지 않는다.

**Why:** Terminal.app은 한글 자모(NFD) 합성 렌더링이 약해서 한글이 깨져 보였음 (2026-05-19 셋업). iTerm2로 옮기고 D2Coding 16pt 폰트로 해결.

**How to apply:**
- 사용자가 "터미널" 언급하면 iTerm2를 기본 가정
- iTerm2 기본 프로필: "Korean (D2Coding)" (GUID: A1B2C3D4-E5F6-7890-ABCD-D2CODING0001)
- Dynamic Profile 위치: `~/Library/Application Support/iTerm2/DynamicProfiles/Korean.json`
- 폰트: `~/Library/Fonts/D2Coding*.ttf` (Regular/Bold/Ligature 4종 설치됨)
- 한글 렌더링 이슈 재발 시 이 프로필이 살아있는지 먼저 확인

브루(Homebrew)는 설치 안 됨 — 도구 설치는 직접 다운로드 방식으로 진행.
