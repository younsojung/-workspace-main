#!/usr/bin/env bash
# Google Drive Reorganization — 최근 1년 루트 파일을 페르소나 폴더로 이동
#
# 사용법:
#   bash execute-moves.sh --dry-run    # 미리보기 (실제 이동 없음)
#   bash execute-moves.sh              # 실제 이동
#
# 전제: gws CLI 설치 + 'gws auth login' 완료

set -u

DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

# === 폴더 ID (folder-ids.md 와 동기화) ===
ROOT_ID="0AN3yxw6Kl-6VUk9PVA"
SINCE="2025-05-11T00:00:00Z"

F_생각마라톤="1nuKriuHiKVvcaIF0HqEOmcF_wTN2k1WP"
F_앤드엔="1PGt7NVKa-EzFLO81lpEMCDoySF-D6Xlg"
F_뛰어노는논술="1uRsgJvH3LayB62u8AJHqg5njq1PgTlzk"
F_단행본="1OJYevblsEK_rynZ4IVRsmo4OsfOz-ASl"
F_채산표="1HgS2wrsAYtSqxbAhnfPNBkYPbVk0fn5A"
F_러쉬="12FwNOcnrrDBg3F3w-kav7xpmy0L5VWwt"
F_코치="10ghq3GpBKq4B1_ahSE_wmWKRXLpxM9Di"
F_뷰클런즈="1fneWWEWwVkV5989SV_KFvWTaXoqxlPMn"
F_개인="1KFfEYBs6nfgsepSDPHnZWR9wKk4A1JsJ"
F_inbox="1Vj4dNYRKariU0AKR_bsbV103tgfK9eEe"

# === 사전 체크 ===
if ! command -v gws >/dev/null 2>&1; then
  echo "Error: gws CLI 없음. 'npm i -g @googleworkspace/gws-cli' 또는 nvm 버전 확인."
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: jq 없음. 'brew install jq' 필요."
  exit 1
fi

AUTH_METHOD=$(gws auth status 2>/dev/null | jq -r '.auth_method // "none"')
if [ "$AUTH_METHOD" = "none" ] || [ -z "$AUTH_METHOD" ]; then
  echo "Error: gws 인증 안 됨. 'gws auth login' 먼저 실행."
  exit 1
fi

echo "=== Drive Reorganization $([ "$DRY_RUN" = "1" ] && echo "(DRY-RUN)" || echo "(LIVE)") ==="
echo "Auth: $AUTH_METHOD"
echo "Cutoff: $SINCE"
echo

# === 분류 함수 ===
classify() {
  local title="$1"
  case "$title" in
    *생각마라톤*|*"생각 마라톤"*|"DAY7_"*|"DAY8_"*|*학습자본*|*"깨끗한 학습력"*) echo "$F_생각마라톤"; return ;;
    *앤드엔*) echo "$F_앤드엔"; return ;;
    *"뛰어노는 논술"*|*뛰어노는논술*|*"트루스 에듀케이트"*|*트루에듀컬처*|*"Trus educulture"*) echo "$F_뛰어노는논술"; return ;;
    *러쉬*|*LUSH*|*무명배우*|*러쉬씨어터*|*"RETAIL STRATEGY"*|*"WORK AFTER PARTY"*) echo "$F_러쉬"; return ;;
    *트루스데이*|*"트루스 전략"*|*"26년 트루스"*|*"트루스의 비전"*|*"트루스 _학습"*|*"트루스 그룹"*|*"트루스 설날"*|*"트루스 스토리"*|*리브랜딩_단가_인터뷰_TRUS*|*"진정한 성과"*|*기업의\ 체질개선*|*"고객에 대하여"*) echo "$F_코치"; return ;;
    *"2033_book"*|*"2033_one_pager"*|*"2033_presentation"*|*"ASTRA BOOK"*|*"Astra book"*|*일의_교과서*|*"일의 교과서"*|*"시스템 1장"*|*"직관의 시대"*|*"날것의 감각"*|*"생각 교과서"*|*"5월. 알고리즘"*|*"6월. 브랜드"*|*"7월. 떠나고"*|*"7월. 잘사는"*|*"11월의 생각구독"*|*"1월. 30대"*|*"생각구독 Pt"*|*"생각구독 라이브"*|*"생각구독의 끝점"*|*사람공부*|*김득신*|*맹상군*|*"욕망에 대한 스터디"*|*"회의록 4단계 슬라이드"*|*회의록_4단계_슬라이드*|*소울정*|*유투브*|*유학법*|*"라이브 방송"*|*"오프닝 영상"*) echo "$F_단행본"; return ;;
    *브레빌*|*보헤미안*) echo "$F_뷰클런즈"; return ;;
    *"결혼식 사회"*|*축사*|*"절기 체크"*|*추석*|*펜타포트*|*생일잔치*|*명절*|"IMG_"*|*송도동*|*destiny_dates*|*"VIF 신청"*|*"영혼의 친구"*) echo "$F_개인"; return ;;
    *.mp3|*.m4a|*Playlist*|*𝐏𝐥𝐚𝐲𝐥𝐢𝐬𝐭*|*Laufey*|*"Mo' Better"*|*"Keep Me Warm"*|*"Love, Love"*|*"Let us walk"*|*"You are in low voice"*|*"사클 샘플"*) echo "$F_생각마라톤"; return ;;
    *학습자본.ai*|*"시간을 자유로"*|*"숫자를 언어로"*|*"나의 자리"*) echo "$F_단행본"; return ;;
  esac
  echo "$F_inbox"
}

# === 이동 함수 ===
move_file() {
  local fid="$1"; local target="$2"; local title="$3"
  if [ "$DRY_RUN" = "1" ]; then
    printf "[DRY] %-44s → %s\n" "$title" "$(folder_name "$target")"
  else
    if gws drive files update --params "{\"fileId\":\"$fid\",\"addParents\":\"$target\",\"removeParents\":\"$ROOT_ID\"}" >/dev/null 2>&1; then
      printf "[OK]  %-44s → %s\n" "$title" "$(folder_name "$target")"
    else
      printf "[ERR] %s — gws update 실패 (권한? 공동소유?)\n" "$title"
    fi
  fi
}

folder_name() {
  case "$1" in
    $F_생각마라톤) echo "교육기획/생각마라톤" ;;
    $F_앤드엔) echo "교육기획/앤드엔클럽" ;;
    $F_뛰어노는논술) echo "교육기획/뛰어노는논술" ;;
    $F_단행본) echo "작가-생각구독/단행본-원고" ;;
    $F_채산표) echo "작가-생각구독/채산표" ;;
    $F_러쉬) echo "러쉬코리아-CD" ;;
    $F_코치) echo "코치-CEO비즈니스" ;;
    $F_뷰클런즈) echo "사업체/뷰클런즈" ;;
    $F_개인) echo "개인" ;;
    $F_inbox) echo "_inbox" ;;
    *) echo "$1" ;;
  esac
}

# === 메인 루프 ===
TOTAL=0
declare -A COUNTS

# Drive API: q 파라미터로 필터
QUERY="'$ROOT_ID' in parents and mimeType != 'application/vnd.google-apps.folder' and modifiedTime > '$SINCE' and trashed = false"
PARAMS=$(jq -n --arg q "$QUERY" '{q: $q, pageSize: 100, fields: "nextPageToken, files(id,name)"}')

gws drive files list --page-all --params "$PARAMS" 2>/dev/null \
  | jq -r '.files[]? | "\(.id)\t\(.name)"' \
  | while IFS=$'\t' read -r fid name; do
      [ -z "$fid" ] && continue
      target=$(classify "$name")
      move_file "$fid" "$target" "$name"
      TOTAL=$((TOTAL+1))
    done

echo
echo "=== 끝 ==="
[ "$DRY_RUN" = "1" ] && echo "이상 이동 대상. 실제로 옮기려면: bash $0 (옵션 없이)"
