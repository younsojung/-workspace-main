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

# --- 1. PULL 먼저 (다른 머신 변경 가져오기) ---
echo "→ origin/$BRANCH 에서 pull (rebase)..."
if ! git pull --rebase origin "$BRANCH" 2>&1; then
  echo ""
  echo "❌ Pull 실패 — 충돌 가능성. 수동 해결 필요."
  echo "   git status 로 확인 후 git rebase --continue / --abort"
  exit 1
fi
echo ""

# --- 2. 로컬 변경 스테이징 ---
git add .

if git diff --cached --quiet; then
  echo "✅ 변경사항 없음. Pull만 완료."
  exit 0
fi

# --- 3. 커밋 메시지 ---
TS=$(date +"%Y-%m-%d %H:%M")
MSG="${1:-sync from $HOSTNAME: $TS}"

# --- 4. 커밋 + PUSH ---
git commit -m "$MSG"
echo ""
echo "→ origin/$BRANCH 으로 push..."
git push origin "$BRANCH"
echo ""
echo "✅ 동기화 완료: $MSG"
