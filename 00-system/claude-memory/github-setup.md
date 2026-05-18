---
name: github-setup
description: "GitHub 리포 URL, SSH 키 정보, 일일 sync 스크립트 위치"
metadata: 
  node_type: memory
  type: reference
  originSessionId: a984fe46-d00f-46cb-a5d7-871b1bfd6910
---

## GitHub 계정

- 사용자명: **younsojung**
- 이메일: insung.inq@gmail.com

## SSH 인증

- 키 종류: ed25519 (passphrase 없음)
- 위치: `~/.ssh/id_ed25519` / `~/.ssh/id_ed25519.pub`
- Fingerprint: `SHA256:Cy8GAx+HgwNnmwP/1unnDNLurlXzFKRWqehiVeF+uT0`
- 생성일: 2026-05-19
- GitHub 등록일: 2026-05-19

## 리포

| 로컬 폴더 | GitHub Remote | 비고 |
|----------|---------------|------|
| `~/Desktop/claude/workspace-main` | `git@github.com:younsojung/-workspace-main.git` | PKM. 첫 커밋 162e860 (2026-05-19) |
| `~/Desktop/claude/designer` | 미정 | 코드만 (미디어 제외). 사용자가 repo 생성 예정 |

## 자동 백업

- 스크립트: `~/Desktop/claude/workspace-main/00-system/scripts/sync.sh`
- 사용: `bash 00-system/scripts/sync.sh [커밋메시지]`
- 변경사항 없으면 무동작. 메시지 생략 시 `sync: YYYY-MM-DD HH:MM`

## 도구 상태

- `gh` CLI: **미설치** (brew도 없음). repo 생성은 수동(github.com/new) 필요
- `git`: 2.39.2

## Related

[[workspace-layout]] · [[integrations]]
