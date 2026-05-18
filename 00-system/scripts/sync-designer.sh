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

echo "→ origin/$BRANCH 에서 pull (rebase)..."
if ! git pull --rebase origin "$BRANCH" 2>&1; then
  echo "❌ Pull 실패 — 충돌. 수동 해결 필요."
  exit 1
fi
echo ""

git add .

if git diff --cached --quiet; then
  echo "✅ 변경사항 없음. Pull만 완료."
  exit 0
fi

TS=$(date +"%Y-%m-%d %H:%M")
MSG="${1:-sync from $HOSTNAME: $TS}"

git commit -m "$MSG"
echo ""
echo "→ origin/$BRANCH 으로 push..."
git push origin "$BRANCH"
echo ""
echo "✅ 동기화 완료: $MSG"
