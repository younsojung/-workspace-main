#!/usr/bin/env bash
# gws-healthcheck.sh — Google Workspace CLI 연동 상태 진단
# 사용법: bash 00-system/scripts/gws-healthcheck.sh

set -u

OK="✅"
NG="❌"
WARN="⚠️ "

echo "=== gws CLI 헬스체크 ==="
echo

# 1. 바이너리
if command -v gws >/dev/null 2>&1; then
  GWS_BIN=$(command -v gws)
  GWS_VER=$(gws --version 2>/dev/null | head -1)
  echo "$OK 바이너리: $GWS_BIN ($GWS_VER)"
else
  echo "$NG gws 명령을 찾을 수 없음. nvm node 버전이 바뀌었는지 확인 → 'nvm use' 또는 'npm i -g @googleworkspace/gws-cli'"
  exit 1
fi

# 2. 설정 디렉터리
CFG_DIR="$HOME/.config/gws"
if [ -d "$CFG_DIR" ]; then
  echo "$OK 설정 디렉터리: $CFG_DIR"
else
  echo "$NG 설정 디렉터리 없음: $CFG_DIR"
fi

# 3. client_secret.json
if [ -f "$CFG_DIR/client_secret.json" ]; then
  echo "$OK client_secret.json 존재"
else
  echo "$NG client_secret.json 없음 → 'gws auth setup' 재실행 필요"
fi

# 4. 인증 상태
echo
echo "--- gws auth status ---"
STATUS_JSON=$(gws auth status 2>/dev/null)
echo "$STATUS_JSON"
echo

AUTH_METHOD=$(echo "$STATUS_JSON" | grep -o '"auth_method": *"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')
if [ "$AUTH_METHOD" = "none" ] || [ -z "$AUTH_METHOD" ]; then
  echo "$NG auth_method=none → 'gws auth login' 실행해서 OAuth 로그인 필요"
  AUTH_OK=0
else
  echo "$OK auth_method=$AUTH_METHOD"
  AUTH_OK=1
fi

# 5. 스모크 테스트 (인증이 있을 때만)
if [ "$AUTH_OK" = "1" ]; then
  echo
  echo "--- Gmail 스모크 테스트 ---"
  RESP=$(gws gmail users getProfile --params '{"userId":"me"}' --format json 2>&1)
  if echo "$RESP" | grep -q '"emailAddress"'; then
    EMAIL=$(echo "$RESP" | grep -o '"emailAddress": *"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')
    echo "$OK Gmail API 호출 성공 ($EMAIL)"
  else
    echo "$NG Gmail API 호출 실패:"
    echo "$RESP" | head -10
  fi

  echo
  echo "--- Calendar 스모크 테스트 ---"
  RESP=$(gws calendar users me calendarList list --format json 2>&1 | head -20)
  if echo "$RESP" | grep -q '"items"\|"summary"'; then
    echo "$OK Calendar API 호출 성공"
  else
    echo "$WARN Calendar 응답 확인 필요:"
    echo "$RESP" | head -5
  fi
fi

echo
echo "=== 끝 ==="
