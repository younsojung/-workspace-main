# 노트북 셋업 가이드

> 두 번째 머신(노트북 또는 다른 데스크탑)에서 이 워크스페이스를 활성화하는 절차.
> 작성일: 2026-05-19

## 사전 조건

- macOS (다른 OS는 경로 조정 필요)
- 노트북 사용자 이름이 **`sojungyoun`** 이어야 경로가 일치함
  - 다르면 메모리 symlink 경로 수정 필요 (아래 4번 주의)
- 인터넷 + GitHub younsojung 계정 접근

## 1. SSH 키 설정

데스크탑에서 만든 키를 그대로 옮기거나, 노트북에서 새 키를 만들어 GitHub에 추가 등록.

**방법 A — 데스크탑 키 복사** (가장 빠름):

데스크탑에서:
```bash
cat ~/.ssh/id_ed25519
cat ~/.ssh/id_ed25519.pub
```

두 내용을 노트북의 같은 경로에 동일하게 저장 후:
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
ssh -T git@github.com   # "Hi younsojung!" 나오면 성공
```

**방법 B — 노트북에서 새 키 생성**:

```bash
ssh-keygen -t ed25519 -C "insung.inq@gmail.com" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub
```

출력된 공개키를 https://github.com/settings/ssh/new 에 등록 (Title: `Mac - laptop` 등).

## 2. 워크스페이스 clone

```bash
mkdir -p ~/Desktop/claude
cd ~/Desktop/claude
git clone git@github.com:younsojung/-workspace-main.git workspace-main
```

> 폴더 이름을 `workspace-main` 으로 유지하는 게 중요. 메모리 경로 자동 매칭됨.

## 3. designer/ clone (선택, 코드만)

```bash
cd ~/Desktop/claude
git clone git@github.com:younsojung/[designer-repo-이름].git designer
```

> ⚠️ 미디어 파일(영상·이미지, 5GB)은 git에 없음. 별도 동기화 필요:
> - 옵션 1: iCloud Drive / Dropbox / Google Drive로 `designer/` 통째 sync
> - 옵션 2: 미디어는 노트북에 안 가져가고 데스크탑 전용으로 유지

## 4. Claude 메모리 symlink 연결

`~/.claude/projects/...` 경로는 워크스페이스 절대경로에서 자동 계산됨.
사용자명이 `sojungyoun`이고 워크스페이스가 `~/Desktop/claude/workspace-main`이면 같은 경로:

```bash
MEM_PATH="/Users/sojungyoun/.claude/projects/-Users-sojungyoun-Desktop-claude-workspace-main"
mkdir -p "$MEM_PATH"
# 기존 memory 디렉토리 있으면 백업 후 제거
[ -d "$MEM_PATH/memory" ] && [ ! -L "$MEM_PATH/memory" ] && mv "$MEM_PATH/memory" "$MEM_PATH/memory.backup-$(date +%Y%m%d)"
ln -s ~/Desktop/claude/workspace-main/00-system/claude-memory "$MEM_PATH/memory"

# 검증
ls -la "$MEM_PATH/memory/"
```

## 5. 자동 sync 활성화 (권장)

### 5-1. Full Disk Access 권한 부여 (필수 1회)

macOS는 기본적으로 백그라운드 프로세스(launchd)의 Desktop 폴더 접근을 막음. `bash`에 권한 줘야 자동 sync 작동.

1. **System Settings** 열기 (사과 메뉴 → System Settings)
2. **Privacy & Security** → **Full Disk Access**
3. 좌하단 **`+`** 버튼 → 파일 선택 창 열림
4. **`Cmd + Shift + G`** → 경로 입력: `/bin/bash`
5. `bash` 선택 → **Open** → 토글 켜기 (파란색)
6. 비밀번호 입력 (있으면)

### 5-2. LaunchAgent 등록

```bash
bash ~/Desktop/claude/workspace-main/00-system/scripts/setup-autosync.sh
```

→ 30분마다 자동 sync. 로그: `~/Library/Logs/workspace-sync.log`

### 5-3. Claude Code Stop 훅 (자동 적용됨)

`.claude/settings.json`이 git에 있어서 노트북에서도 Claude Code 세션 끝날 때마다 자동 sync 됨. 별도 설정 불필요.

## 6. 수동 sync (자동이 안 될 때)

작업 시작 / 끝:
```bash
cd ~/Desktop/claude/workspace-main
bash 00-system/scripts/sync.sh "메시지"
```

designer/ 도 동일:
```bash
bash ~/Desktop/claude/workspace-main/00-system/scripts/sync-designer.sh
```

## 7. 충돌 발생 시

`sync.sh` 에서 pull 단계가 실패하면 충돌 가능성:
```bash
cd ~/Desktop/claude/workspace-main
git status                     # 충돌 파일 확인
# 충돌 파일 직접 편집하거나, 어느 쪽 채택할지 결정
git rebase --continue          # 또는 git rebase --abort
```

확실하지 않으면 Claude에게 "git 충돌 났어"라고 말하기.

## 8. 멀티 머신 사용 원칙

1. **한 번에 한 머신만** 작업 — 동시에 같은 파일 편집하면 충돌
2. 작업 전 `sync.sh` 먼저
3. 작업 후 `sync.sh` 즉시 (다른 머신이 가져갈 수 있도록)
4. 미디어(designer 영상·이미지)는 git 아닌 별도 동기화 (Dropbox/iCloud Drive 등)

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `Permission denied (publickey)` | SSH 키 미등록/다른 계정 | https://github.com/settings/keys 에서 fingerprint 확인 |
| `pull` 충돌 | 양 머신에서 같은 파일 편집 | 수동으로 충돌 해결 후 `git rebase --continue` |
| 메모리가 안 보임 | symlink 안 됨 | 위 4번 재실행. `ls -la ~/.claude/projects/.../memory` 로 화살표 확인 |
| Notion/Drive/Gmail 안 됨 | Claude MCP 인증 만료 | claude.ai 에서 재로그인 |
