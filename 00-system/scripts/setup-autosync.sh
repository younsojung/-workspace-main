#!/usr/bin/env bash
# 자동 sync 설정: launchd LaunchAgent 등록
# 머신마다 한 번씩만 실행하면 됨 (데스크탑/노트북 각각)

set -euo pipefail

LABEL="com.sojung.workspace-sync"
WORKSPACE="$HOME/Desktop/claude/workspace-main"
TEMPLATE="$WORKSPACE/00-system/scripts/com.sojung.workspace-sync.plist.template"
PLIST_DEST="$HOME/Library/LaunchAgents/${LABEL}.plist"

if [ ! -d "$WORKSPACE" ]; then
  echo "❌ 워크스페이스 없음: $WORKSPACE"
  echo "   먼저 git clone 으로 받아주세요."
  exit 1
fi

if [ ! -f "$TEMPLATE" ]; then
  echo "❌ plist 템플릿 없음: $TEMPLATE"
  exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"
mkdir -p "$HOME/Library/Logs"

# 기존 job 있으면 unload
if launchctl list | grep -q "$LABEL"; then
  echo "→ 기존 LaunchAgent unload..."
  launchctl unload "$PLIST_DEST" 2>/dev/null || true
fi

# 템플릿에서 경로 치환
echo "→ plist 생성: $PLIST_DEST"
sed -e "s|__WORKSPACE__|$WORKSPACE|g" \
    -e "s|__HOME__|$HOME|g" \
    "$TEMPLATE" > "$PLIST_DEST"

# 로드
echo "→ launchd 등록..."
launchctl load -w "$PLIST_DEST"

echo ""
echo "✅ 자동 sync 활성화"
echo "   - 30분마다 백그라운드 sync"
echo "   - 로그: $HOME/Library/Logs/workspace-sync.log"
echo "   - 비활성화: launchctl unload $PLIST_DEST"
echo ""
echo "→ 첫 sync 실행 (RunAtLoad)..."
sleep 2
echo ""
tail -20 "$HOME/Library/Logs/workspace-sync.log" 2>/dev/null || echo "(로그 아직 없음 — 잠시 후 확인)"
