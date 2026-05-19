#!/usr/bin/env bash
# workspace-main 멀티 머신 동기화 스크립트
# 컴퓨터·노트북 둘 다에서 같은 GitHub repo를 공유하므로:
#   1. 항상 PULL부터 (다른 머신 변경 가져오기)
#   2. 충돌 시 rebase로 정리
#   3. 변경있으면 commit + push
#
# 사용:
#   bash 00-system/scripts/sync.sh                # 자동 메시지
#   bash 00-system/scripts/sync.sh "내 커밋 메시지"

set -euo pipefail

REPO_ROOT="/Users/sojungyoun/Desktop/claude/workspace-main"
cd "$REPO_ROOT"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
HOSTNAME=$(hostname -s)

echo "📍 머신: $HOSTNAME"
echo "📍 브랜치: $BRANCH"
echo ""

# --- 1. 로컬 변경 먼저 commit (rebase 충돌 회피) ---
git add .
TS=$(date +"%Y-%m-%d %H:%M")
MSG="${1:-sync from $HOSTNAME: $TS}"
LOCAL_HAD_CHANGES=0
if ! git diff --cached --quiet; then
  git commit -m "$MSG"
  LOCAL_HAD_CHANGES=1
  echo ""
fi

# --- 2. PULL (다른 머신 변경 가져오기) ---
echo "→ origin/$BRANCH 에서 pull (rebase)..."
if ! git pull --rebase origin "$BRANCH" 2>&1; then
  echo ""
  echo "❌ Pull/rebase 실패 — 충돌 가능성. 수동 해결 필요."
  echo "   git status 로 확인 후 git rebase --continue / --abort"
  exit 1
fi
echo ""

# --- 3. PUSH (로컬 변경 또는 rebase 결과 송신) ---
if [ "$LOCAL_HAD_CHANGES" -eq 1 ] || [ "$(git rev-list @{u}..HEAD --count 2>/dev/null)" -gt 0 ]; then
  echo "→ origin/$BRANCH 으로 push..."
  git push origin "$BRANCH"
  echo ""
  echo "✅ 동기화 완료: $MSG"
else
  echo "✅ 변경사항 없음. Pull만 완료."
fi
