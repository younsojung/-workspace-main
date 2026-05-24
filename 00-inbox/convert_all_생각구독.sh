#!/usr/bin/env bash
# 생각구독 전체호 PDF → MD 일괄 변환
set -u
cd /Users/sojungyoun/Desktop/claude/workspace-main
source .venv/bin/activate

SRC="/Users/sojungyoun/Desktop/claude/writer/전체호"
OUT="/Users/sojungyoun/Desktop/claude/writer/전체호-md"
SCRIPT=".claude/skills/pdf-to-md/scripts/pdf_to_md.py"
LOG="$OUT/_convert.log"
mkdir -p "$OUT"
: > "$LOG"

count=0
ok=0
fail=0
for f in "$SRC"/*.pdf; do
  base="$(basename "$f" .pdf)"
  out_md="$OUT/${base}.md"
  count=$((count+1))
  if [[ -s "$out_md" ]]; then
    echo "[skip $count] $base (exists)" | tee -a "$LOG"
    ok=$((ok+1))
    continue
  fi
  echo "[run  $count] $base" | tee -a "$LOG"
  if python "$SCRIPT" "$f" --output "$out_md" >>"$LOG" 2>&1; then
    ok=$((ok+1))
  else
    fail=$((fail+1))
    echo "  FAILED" | tee -a "$LOG"
  fi
done
echo "===== DONE total=$count ok=$ok fail=$fail =====" | tee -a "$LOG"
