#!/usr/bin/env bash
# designer/ 멀티 머신 동기화 (workspace-main과 동일 패턴)
# 주의: 미디어 파일은 .gitignore로 제외됨. 미디어는 별도 백업 필요.

set -euo pipefail

REPO_ROOT="/Users/sojungyoun/Desktop/claude/designer"
cd "$REPO_ROOT"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
HOSTNAME=$(hostname -s)

echo "📍 머신: $HOSTNAME"
echo "📍 브랜치: $BRANCH"
echo ""

git add .
TS=$(date +"%Y-%m-%d %H:%M")
MSG="${1:-sync from $HOSTNAME: $TS}"
LOCAL_HAD_CHANGES=0
if ! git diff --cached --quiet; then
  git commit -m "$MSG"
  LOCAL_HAD_CHANGES=1
  echo ""
fi

echo "→ origin/$BRANCH 에서 pull (rebase)..."
if ! git pull --rebase origin "$BRANCH" 2>&1; then
  echo "❌ Pull/rebase 실패 — 충돌. 수동 해결 필요."
  exit 1
fi
echo ""

if [ "$LOCAL_HAD_CHANGES" -eq 1 ] || [ "$(git rev-list @{u}..HEAD --count 2>/dev/null)" -gt 0 ]; then
  echo "→ origin/$BRANCH 으로 push..."
  git push origin "$BRANCH"
  echo ""
  echo "✅ 동기화 완료: $MSG"
else
  echo "✅ 변경사항 없음. Pull만 완료."
fi
