"""
download_file_content 결과 (base64 CSV) 디코딩 + 최근 12개월 분석
"""
import json, csv, re, base64
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

INPUT = "/Users/sojungyoun/.claude/projects/-Users-sojungyoun-Desktop-claude-workspace-main/6eafa475-1140-44ac-aeb5-1fc6b22ce00f/tool-results/mcp-claude_ai_Google_Drive-download_file_content-1779508010627.txt"
OUT_DIR = Path("/Users/sojungyoun/Desktop/claude/workspace-main/10-projects/younsojung-site-renewal/data")
RAW_DIR = OUT_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

with open(INPUT, encoding="utf-8") as f:
    payload = json.load(f)

print(f"[meta] title={payload.get('title')!r} mimeType={payload.get('mimeType')!r}")
print(f"[meta] content length (base64) = {len(payload['content']):,}")

# base64 디코딩
raw_bytes = base64.b64decode(payload["content"])
print(f"[meta] decoded bytes = {len(raw_bytes):,}")

csv_text = raw_bytes.decode("utf-8", errors="replace")
print(f"[meta] csv text len = {len(csv_text):,}")

# CSV 저장
csv_path = RAW_DIR / "form-responses-full.csv"
with open(csv_path, "w", encoding="utf-8") as f:
    f.write(csv_text)
print(f"[save] {csv_path}")

# 파싱
rows = list(csv.reader(csv_text.splitlines()))
header = rows[0]
data = rows[1:]
print(f"[parse] header cols = {len(header)}")
print(f"[parse] data rows = {len(data):,}")
print(f"[parse] header:")
for i, h in enumerate(header):
    print(f"  [{i}] {h!r}")

# 컬럼 인덱스 식별
def find_col(keywords):
    for i, h in enumerate(header):
        if any(k in h for k in keywords):
            return i
    return None

date_idx = find_col(["타임스탬프", "Timestamp"])
plan_idx = find_col(["성장하고 싶은 기간", "구독 기간"])
wish_idx = find_col(["나누고 싶은 주제", "기대하는 점"])
name_idx = find_col(["성함"])
email_idx = find_col(["이메일"])

print(f"\n[idx] date={date_idx}, plan={plan_idx}, wish={wish_idx}, name={name_idx}, email={email_idx}")

def parse_kr_date(s):
    s = s.strip()
    if not s:
        return None
    m = re.match(r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\s*(오전|오후)?\s*(\d{1,2}):(\d{2}):(\d{2})", s)
    if not m:
        try:
            return datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None
    y, mo, d, ampm, hh, mi, ss = m.groups()
    hh = int(hh)
    if ampm == "오후" and hh < 12: hh += 12
    elif ampm == "오전" and hh == 12: hh = 0
    return datetime(int(y), int(mo), int(d), hh, int(mi), int(ss))

today = datetime(2026, 5, 23)
cutoff = today - timedelta(days=365)

# 전체 통계
total_all = len(data)
all_dates = [parse_kr_date(r[date_idx]) if date_idx is not None and len(r)>date_idx else None for r in data]
valid_dates = [d for d in all_dates if d]
date_min = min(valid_dates) if valid_dates else None
date_max = max(valid_dates) if valid_dates else None
print(f"\n[range] total={total_all}, valid dates={len(valid_dates)}, range={date_min} ~ {date_max}")

# 최근 12개월 필터링
recent = []
for r, d in zip(data, all_dates):
    if d is None or d < cutoff:
        continue
    while len(r) < len(header):
        r.append("")
    recent.append((d, r))
print(f"[filter] last 12mo rows = {len(recent):,}")

# 자유서술 답변
wish_entries = []
for d, r in recent:
    wish = r[wish_idx].strip() if wish_idx is not None and wish_idx < len(r) else ""
    plan = r[plan_idx].strip() if plan_idx is not None and plan_idx < len(r) else ""
    name = r[name_idx].strip() if name_idx is not None and name_idx < len(r) else ""
    email = r[email_idx].strip() if email_idx is not None and email_idx < len(r) else ""
    if wish and len(wish) >= 4:
        wish_entries.append({
            "date": d.strftime("%Y-%m-%d"),
            "plan": plan, "name": name, "email": email, "wish": wish
        })

print(f"[filter] non-empty wish answers (last 12mo) = {len(wish_entries):,}")

# 결제 플랜 분포
plan_counter = Counter(r[plan_idx].strip() for d, r in recent if plan_idx is not None and plan_idx < len(r) and r[plan_idx].strip())

# 월별
month_counter = Counter(d.strftime("%Y-%m") for d, _ in recent)
wish_month_counter = Counter(e["date"][:7] for e in wish_entries)

# 슈퍼팬: 같은 email 다회 신청
all_emails = [r[email_idx].strip().lower() for d, r in recent if email_idx is not None and email_idx < len(r) and r[email_idx].strip()]
email_counter = Counter(all_emails)
superfans_12mo = [(e, c) for e, c in email_counter.most_common(50) if c >= 3]

# 저장: wishes
out_wishes = OUT_DIR / "last-12mo-wishes.md"
with open(out_wishes, "w", encoding="utf-8") as f:
    f.write("# 최근 12개월 신청자가 원하는 것 (raw)\n\n")
    f.write(f"- 기간: {cutoff.date()} ~ {today.date()}\n")
    f.write(f"- 전체 신청 (1년): {len(recent):,}건\n")
    f.write(f"- 자유서술 답변 작성: {len(wish_entries):,}건 ({len(wish_entries)/max(len(recent),1)*100:.1f}%)\n\n")
    f.write("## 월별\n\n")
    f.write("| 월 | 전체 신청 | 답변 작성 |\n|---|---:|---:|\n")
    for m in sorted(month_counter):
        f.write(f"| {m} | {month_counter[m]} | {wish_month_counter.get(m,0)} |\n")
    f.write("\n---\n\n## 답변 전체 (최신순)\n\n")
    for e in sorted(wish_entries, key=lambda x: x["date"], reverse=True):
        f.write(f"- **[{e['date']}]** _{e['plan']}_ — {e['wish']}\n")

# 저장: summary
out_sum = OUT_DIR / "summary-12mo.md"
with open(out_sum, "w", encoding="utf-8") as f:
    f.write("# 최근 12개월 신청 요약 (2025-05-23 ~ 2026-05-23)\n\n")
    f.write(f"- 전체 신청: **{len(recent):,}건**\n")
    f.write(f"- 자유서술 답변률: **{len(wish_entries)/max(len(recent),1)*100:.1f}%**\n")
    f.write(f"- 고유 이메일: {len(set(all_emails)):,}명\n")
    f.write(f"- 1년 내 3회+ 재신청: {len(superfans_12mo):,}명\n\n")
    f.write("## 결제 플랜 분포\n\n")
    for plan, cnt in plan_counter.most_common():
        if plan:
            f.write(f"- {plan}: {cnt}건 ({cnt/max(len(recent),1)*100:.1f}%)\n")
    f.write("\n## 1년 내 슈퍼팬 (3회+ 재신청)\n\n")
    for e, c in superfans_12mo[:20]:
        f.write(f"- {e}: {c}회\n")

print(f"\n[save] {out_wishes}")
print(f"[save] {out_sum}")
print("\n[done]")
