"""
생각구독 신청 폼 응답 시트에서 최근 1년치 자유서술형 답변 추출
입력: read_file_content 결과 JSON (fileContent: string)
출력:
  - all-rows.csv (전체 파싱된 행)
  - last-12mo-wishes.md (2025-05-23 ~ 2026-05-23 자유서술형 답변)
  - summary.md (통계)
"""
import json
import csv
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

INPUT = "/Users/sojungyoun/.claude/projects/-Users-sojungyoun-Desktop-claude-workspace-main/6eafa475-1140-44ac-aeb5-1fc6b22ce00f/tool-results/mcp-claude_ai_Google_Drive-read_file_content-1779507884209.txt"
OUT_DIR = Path("/Users/sojungyoun/Desktop/claude/workspace-main/10-projects/younsojung-site-renewal/data")
RAW_DIR = OUT_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

with open(INPUT, encoding="utf-8") as f:
    payload = json.load(f)

content = payload["fileContent"]
print(f"[load] fileContent length = {len(content):,} chars")

# read_file_content 결과는 마크다운 형태: "# 시트탭이름\n\n``` \n...CSV...\n```"
# 시트 탭별로 분리
tabs = re.split(r"\n#\s+", content)
print(f"[parse] found {len(tabs)} sections")

# 첫 섹션은 보통 "# 설문지 응답 시트1" 헤더로 시작
all_rows = []
tab_info = []
for i, t in enumerate(tabs):
    t = t.strip()
    if not t:
        continue
    # 탭 이름 추출
    first_line = t.split("\n", 1)[0]
    tab_name = first_line.replace("#", "").strip()
    # 코드블록 안의 CSV 추출
    m = re.search(r"```\s*\n(.*?)\n```", t, re.DOTALL)
    if not m:
        tab_info.append((tab_name, 0, "no code block"))
        continue
    csv_text = m.group(1)
    # CSV 파싱
    reader = csv.reader(csv_text.splitlines())
    rows = list(reader)
    tab_info.append((tab_name, len(rows), "ok"))
    if not rows:
        continue
    header = rows[0]
    data = rows[1:]
    for r in data:
        all_rows.append({"_tab": tab_name, "_row": r, "_header": header})

print(f"[parse] total rows (all tabs) = {len(all_rows):,}")
for ti in tab_info:
    print(f"  - {ti[0]!r}: {ti[1]} rows ({ti[2]})")

# 모든 행을 통합 CSV로 저장 (탭별 header가 다를 수 있어서 탭마다 분리 저장)
by_tab = {}
for row in all_rows:
    tname = row["_tab"]
    by_tab.setdefault(tname, []).append(row)

for tname, rows in by_tab.items():
    safe = re.sub(r"[^\w가-힣]+", "_", tname).strip("_") or "unnamed"
    out = RAW_DIR / f"tab_{safe}.csv"
    header = rows[0]["_header"]
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            # 행 길이 맞춤
            row_padded = r["_row"] + [""] * (len(header) - len(r["_row"]))
            w.writerow(row_padded[:len(header)])
    print(f"[save] {out.name}: {len(rows)} rows, {len(header)} cols")
    print(f"        header={header}")

# 날짜 컬럼과 자유서술형 컬럼 자동 식별
def parse_kr_date(s):
    # "2026. 2. 28 오후 8:52:55" → datetime
    s = s.strip()
    if not s:
        return None
    m = re.match(r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\s*(오전|오후)?\s*(\d{1,2}):(\d{2}):(\d{2})", s)
    if not m:
        # alt: "2026-02-28 20:52:55"
        try:
            return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None
    y, mo, d, ampm, hh, mi, ss = m.groups()
    hh = int(hh)
    if ampm == "오후" and hh < 12:
        hh += 12
    elif ampm == "오전" and hh == 12:
        hh = 0
    return datetime(int(y), int(mo), int(d), hh, int(mi), int(ss))

# 자유서술형 컬럼 키워드
WISH_KEYWORDS = ["나누고 싶은", "기대하는", "주제", "원하는"]

today = datetime(2026, 5, 23)
cutoff = today - timedelta(days=365)
print(f"\n[filter] cutoff = {cutoff.date()}, today = {today.date()}")

# 모든 탭에서 자유서술형 답변 추출 (최근 1년치만)
wish_entries = []
total_in_range = 0
total_all = 0

for tname, rows in by_tab.items():
    header = rows[0]["_header"]
    # 날짜 컬럼 찾기
    date_idx = None
    for i, h in enumerate(header):
        if "타임스탬프" in h or "Timestamp" in h or "응답일시" in h:
            date_idx = i
            break
    # 자유서술형 컬럼 찾기
    wish_idx = None
    for i, h in enumerate(header):
        if any(k in h for k in WISH_KEYWORDS):
            wish_idx = i
            break
    # 결제 플랜 컬럼 찾기
    plan_idx = None
    for i, h in enumerate(header):
        if "기간" in h or "결제" in h and "방법" not in h:
            plan_idx = i
            break

    print(f"\n[{tname}] date_idx={date_idx}, wish_idx={wish_idx}, plan_idx={plan_idx}")
    if wish_idx is None:
        print(f"  (skip: no wish column)")
        continue

    for r in rows:
        total_all += 1
        row = r["_row"]
        if len(row) <= max(filter(None, [date_idx, wish_idx, plan_idx])):
            row = row + [""] * (max(filter(None, [date_idx, wish_idx, plan_idx])) + 1 - len(row))
        dt = parse_kr_date(row[date_idx]) if date_idx is not None else None
        wish = row[wish_idx].strip() if wish_idx is not None else ""
        plan = row[plan_idx].strip() if plan_idx is not None else ""

        if dt is None or dt < cutoff:
            continue
        total_in_range += 1
        if not wish or len(wish) < 4:
            continue  # 빈 답변 제외
        wish_entries.append({
            "tab": tname,
            "date": dt.strftime("%Y-%m-%d"),
            "plan": plan,
            "wish": wish,
        })

print(f"\n[filter] total rows across tabs = {total_all:,}")
print(f"[filter] rows in last 12 months = {total_in_range:,}")
print(f"[filter] non-empty wish answers in last 12mo = {len(wish_entries):,}")

# 저장
out_wishes = OUT_DIR / "last-12mo-wishes.md"
with open(out_wishes, "w", encoding="utf-8") as f:
    f.write(f"# 최근 12개월 신청자가 원하는 것 (raw)\n\n")
    f.write(f"- 기간: {cutoff.date()} ~ {today.date()}\n")
    f.write(f"- 전체 신청 (1년): {total_in_range:,}건\n")
    f.write(f"- 자유서술 답변 작성: {len(wish_entries):,}건 ({len(wish_entries)/max(total_in_range,1)*100:.1f}%)\n\n")
    # 월별
    by_month = Counter(e["date"][:7] for e in wish_entries)
    f.write("## 월별 답변 작성 수\n\n")
    for m in sorted(by_month):
        f.write(f"- {m}: {by_month[m]}건\n")
    f.write("\n---\n\n## 답변 전체 (최신순)\n\n")
    for e in sorted(wish_entries, key=lambda x: x["date"], reverse=True):
        f.write(f"- **[{e['date']}]** ({e['plan']}) {e['wish']}\n")

print(f"\n[save] {out_wishes}")

# 통계 요약
out_summary = OUT_DIR / "summary-12mo.md"
plan_counter = Counter()
for tname, rows in by_tab.items():
    header = rows[0]["_header"]
    date_idx = None
    plan_idx = None
    for i, h in enumerate(header):
        if "타임스탬프" in h:
            date_idx = i
        if "기간" in h:
            plan_idx = i
    if date_idx is None or plan_idx is None:
        continue
    for r in rows:
        row = r["_row"]
        if len(row) <= max(date_idx, plan_idx):
            continue
        dt = parse_kr_date(row[date_idx])
        if dt is None or dt < cutoff:
            continue
        plan_counter[row[plan_idx].strip()] += 1

with open(out_summary, "w", encoding="utf-8") as f:
    f.write("# 최근 12개월 신청 요약\n\n")
    f.write(f"- 기간: {cutoff.date()} ~ {today.date()}\n")
    f.write(f"- 전체 신청: {total_in_range:,}건\n")
    f.write(f"- 자유서술 답변률: {len(wish_entries)/max(total_in_range,1)*100:.1f}%\n\n")
    f.write("## 결제 플랜 분포 (최근 12개월)\n\n")
    for plan, cnt in plan_counter.most_common():
        f.write(f"- {plan}: {cnt}건 ({cnt/max(total_in_range,1)*100:.1f}%)\n")

print(f"[save] {out_summary}")
print("\n[done]")
