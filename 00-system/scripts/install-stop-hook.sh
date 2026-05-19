#!/usr/bin/env bash
# Claude Code Stop 훅 설치 — 세션 끝날 때마다 sync.sh 자동 실행
# 한 번만 실행. 양 머신에서 각각 실행해도 같은 결과.
# (settings.json이 git에 포함되니 한쪽에서 한 번이면 다른 쪽에도 적용되긴 함)

set -euo pipefail

SETTINGS="$HOME/Desktop/claude/workspace-main/.claude/settings.json"
TMPL="$HOME/Desktop/claude/workspace-main/00-system/scripts/.settings-stop-hook.json"

# 템플릿 생성
cat > "$TMPL" <<'EOF'
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash /Users/sojungyoun/Desktop/claude/workspace-main/00-system/scripts/sync.sh 'auto-sync (Claude session end)' 2>&1 | tail -5"
          }
        ]
      }
    ]
  }
}
EOF

if [ -f "$SETTINGS" ]; then
  echo "⚠️  $SETTINGS 이미 존재. 백업 후 덮어씁니다."
  cp "$SETTINGS" "$SETTINGS.backup-$(date +%Y%m%d-%H%M%S)"
fi

cp "$TMPL" "$SETTINGS"
rm "$TMPL"

echo "✅ Stop 훅 설치 완료: $SETTINGS"
echo ""
cat "$SETTINGS"
