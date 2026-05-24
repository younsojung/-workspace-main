#!/usr/bin/env bash
# 생각구독 전체호 병렬 변환 (6 workers)
set -u
cd /Users/sojungyoun/Desktop/claude/workspace-main
source .venv/bin/activate

SRC="/Users/sojungyoun/Desktop/claude/writer/전체호"
OUT="/Users/sojungyoun/Desktop/claude/writer/전체호-md"
SCRIPT=".claude/skills/pdf-to-md/scripts/pdf_to_md.py"
LOG="$OUT/_convert.log"
mkdir -p "$OUT"
# preserve previous successes; append to log
: >> "$LOG"

convert_one() {
  local f="$1"
  local base="$(basename "$f" .pdf)"
  local out_md="$OUT/${base}.md"
  if [[ -s "$out_md" ]]; then
    echo "[skip] $base" >> "$LOG"
    return 0
  fi
  echo "[run ] $base (start $(date +%H:%M:%S))" >> "$LOG"
  if python "$SCRIPT" "$f" --output "$out_md" >>"$LOG" 2>&1; then
    echo "[ok  ] $base ($(date +%H:%M:%S))" >> "$LOG"
  else
    echo "[FAIL] $base" >> "$LOG"
  fi
}
export -f convert_one
export OUT SCRIPT LOG SRC

# 6 parallel workers
find "$SRC" -maxdepth 1 -name "*.pdf" -print0 \
  | xargs -0 -P 6 -I {} bash -c 'convert_one "$@"' _ {}

echo "===== ALL DONE $(date +%H:%M:%S) =====" >> "$LOG"
