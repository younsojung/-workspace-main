"""
1,455개 답변을 카테고리·동사·페인 패턴으로 분류
"""
import csv, re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

CSV_PATH = "/Users/sojungyoun/Desktop/claude/workspace-main/10-projects/younsojung-site-renewal/data/raw/form-responses-full.csv"
OUT = Path("/Users/sojungyoun/Desktop/claude/workspace-main/10-projects/younsojung-site-renewal/data/wish-clusters.md")

with open(CSV_PATH, encoding="utf-8") as f:
    rows = list(csv.reader(f))
header = rows[0]
data = rows[1:]
WISH_IDX = 7  # confirmed
DATE_IDX = 0
PLAN_IDX = 2

wishes = []
for r in data:
    if len(r) <= WISH_IDX: continue
    w = r[WISH_IDX].strip()
    if w and len(w) >= 4:
        wishes.append({
            "date": r[DATE_IDX],
            "plan": r[PLAN_IDX],
            "text": w
        })
print(f"[load] {len(wishes)} wish entries")

# ===== 카테고리 사전 =====
CATEGORIES = {
    "AI/도구": ["AI", "ai", "인공지능", "챗gpt", "ChatGPT", "chatGPT", "GPT", "claude", "클로드", "프롬프트", "자동화", "툴", "도구"],
    "일/커리어/사업": ["일", "커리어", "직장", "직업", "이직", "퇴사", "회사", "비즈니스", "비지니스", "사업", "창업", "프리랜서", "1인기업", "워라밸", "성과"],
    "돈/투자/재테크": ["돈", "수익", "재테크", "투자", "자산", "부동산", "경제", "재무", "수익화", "수익구조", "현금흐름", "월급", "연봉", "파이프라인", "패시브"],
    "관계/부모/자녀": ["관계", "인간관계", "사람", "부모", "엄마", "아빠", "자녀", "아이", "딸", "아들", "남편", "아내", "배우자", "가족", "친구", "동료"],
    "성장/마인드": ["성장", "마인드", "마인드셋", "태도", "용기", "자존감", "자신감", "감정", "스트레스", "불안", "두려움", "무기력", "번아웃"],
    "습관/시간/루틴": ["습관", "루틴", "시간", "아침", "새벽", "미라클", "계획", "실행", "꾸준", "지속", "리추얼"],
    "글쓰기/콘텐츠": ["글", "글쓰기", "라이팅", "콘텐츠", "퍼스널브랜드", "퍼스널 브랜드", "브랜딩", "유튜브", "인스타", "sns", "SNS", "블로그"],
    "공부/학습/독서": ["공부", "학습", "독서", "책", "강의", "배움", "배우"],
    "진로/미래/방향": ["진로", "미래", "방향", "방향성", "꿈", "비전", "목표", "정체성", "정체성", "본질", "what to do", "뭘 해야"],
    "마케팅/판매": ["마케팅", "세일즈", "판매", "고객", "고객언어", "타겟", "포지셔닝", "전환"],
    "건강/운동": ["건강", "운동", "다이어트", "체력", "수면", "잠"],
    "영성/명상": ["명상", "영성", "기도", "감사", "내면", "영혼", "에너지"],
    "육아/교육": ["육아", "교육", "양육", "엄마로", "워킹맘", "초등", "유아", "사춘기"],
    "협상/소통": ["협상", "대화", "소통", "표현", "말하기", "발표", "거절"],
    "윤소정 본인/생각": ["소정님", "소정 님", "선생님", "소정쌤", "작가님", "윤소정", "생각구독", "생각 구독", "이야기", "관점", "통찰", "지혜"],
    "결단/선택": ["결단", "결정", "선택", "기준", "판단"],
    "환경설계": ["환경", "환경설계", "환경 설계", "시스템", "구조"],
}

cat_counter = Counter()
cat_examples = defaultdict(list)
for w in wishes:
    t = w["text"]
    matched = set()
    for cat, kws in CATEGORIES.items():
        for kw in kws:
            if kw in t:
                matched.add(cat)
                break
    for cat in matched:
        cat_counter[cat] += 1
        if len(cat_examples[cat]) < 8:
            cat_examples[cat].append(t)

# 미분류
unclassified = []
for w in wishes:
    t = w["text"]
    matched = False
    for cat, kws in CATEGORIES.items():
        if any(kw in t for kw in kws):
            matched = True; break
    if not matched:
        unclassified.append(t)

# ===== 동사 패턴 =====
VERB_PATTERNS = {
    "알고 싶다": r"알고\s*싶[어다]|궁금[하해]",
    "배우고 싶다": r"배우(고|러|기|어)\s*싶|배워(보|볼)?\s*싶|익히[고기]\s*싶",
    "하고 싶다": r"하고\s*싶[어다]",
    "되고 싶다": r"되고\s*싶[어다]|되었으면|되기를",
    "찾고 싶다": r"찾[고기]\s*싶|찾아[보볼]?\s*싶",
    "듣고 싶다": r"듣(고|기)\s*싶|들어\s*보고\s*싶",
    "성장하고 싶다": r"성장하[고기]\s*싶|커지[고기]\s*싶|발전하[고기]\s*싶",
    "변하고 싶다": r"바꾸[고기]\s*싶|변하[고기]\s*싶|달라지[고기]\s*싶",
    "도움 받고 싶다": r"도움(을|이)?\s*받[고기]\s*싶|도와\s*주[셨었]|힘이\s*되어",
    "공부하고 싶다": r"공부하[고기]\s*싶|공부해\s*보고",
}
verb_counter = Counter()
for w in wishes:
    for label, pat in VERB_PATTERNS.items():
        if re.search(pat, w["text"]):
            verb_counter[label] += 1

# ===== 페인 패턴 =====
PAIN_PATTERNS = {
    "막막/모르겠다": r"막막|모르겠|잘\s*모르|어디서부터|어떻게\s*해야|어디로",
    "힘들다/어렵다": r"힘들|어렵|버겁|버거",
    "놓쳤다/뒤늦게": r"놓쳤|놓치|뒤늦게|이제야|뒤늦",
    "처음/초보": r"처음|초보|시작하[는려기]|새로\s*시작",
    "고민/방황": r"고민|방황|헤매|길을\s*잃|혼란|혼돈",
    "이탈/번아웃": r"번아웃|지친|지쳐|무기력|소진|에너지\s*없",
    "변하지 않는다": r"변하지\s*않|그대로|제자리|반복|뱅뱅",
    "두렵다/불안": r"두렵|두려|무서|불안|걱정",
    "혼자 한다": r"혼자|외로|곁에\s*없|함께할",
    "시간 부족": r"시간이\s*없|바쁘|틈이\s*없|여유가\s*없",
}
pain_counter = Counter()
pain_examples = defaultdict(list)
for w in wishes:
    for label, pat in PAIN_PATTERNS.items():
        if re.search(pat, w["text"]):
            pain_counter[label] += 1
            if len(pain_examples[label]) < 5:
                pain_examples[label].append(w["text"])

# ===== 답변 길이 분포 =====
short = sum(1 for w in wishes if len(w["text"]) < 20)
mid = sum(1 for w in wishes if 20 <= len(w["text"]) < 60)
long_ = sum(1 for w in wishes if len(w["text"]) >= 60)

# 슈퍼팬 (긴 답변 = 정성적 슈퍼팬 후보)
long_entries = [w for w in wishes if len(w["text"]) >= 100]

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# 신청 답변 클러스터 분석\n\n")
    f.write(f"- 데이터 범위: 2026-02-28 ~ 2026-05-04 (약 2개월)\n")
    f.write(f"- 전체 신청: 3,399건\n")
    f.write(f"- 답변 작성: {len(wishes):,}건 (42.8%)\n\n")
    f.write(f"## 답변 길이 분포\n")
    f.write(f"- 짧음 (<20자): {short} ({short/len(wishes)*100:.1f}%)\n")
    f.write(f"- 중간 (20-60자): {mid} ({mid/len(wishes)*100:.1f}%)\n")
    f.write(f"- 깊음 (60자+): {long_} ({long_/len(wishes)*100:.1f}%) ← *진짜 신호*\n")
    f.write(f"- 매우 깊음 (100자+): {len(long_entries)}건\n\n")

    f.write("---\n\n## 🎯 주제 카테고리 (중복 카운트)\n\n")
    f.write("| 카테고리 | 답변 수 | 비중 (전체 1,455 기준) |\n|---|---:|---:|\n")
    for cat, cnt in cat_counter.most_common():
        f.write(f"| {cat} | {cnt} | {cnt/len(wishes)*100:.1f}% |\n")
    f.write(f"\n- 미분류: {len(unclassified)} ({len(unclassified)/len(wishes)*100:.1f}%)\n")

    f.write("\n---\n\n## 🗣 동사 패턴 (무엇을 하고 싶다고 적었나)\n\n")
    f.write("| 동사 패턴 | 빈도 |\n|---|---:|\n")
    for v, c in verb_counter.most_common():
        f.write(f"| {v} | {c} |\n")

    f.write("\n---\n\n## 🩹 페인 패턴 (어떤 고통에서 왔나)\n\n")
    f.write("| 페인 | 빈도 |\n|---|---:|\n")
    for p, c in pain_counter.most_common():
        f.write(f"| {p} | {c} |\n")

    f.write("\n---\n\n## 📋 카테고리별 대표 답변\n\n")
    for cat, cnt in cat_counter.most_common():
        f.write(f"\n### {cat} ({cnt}건)\n")
        for ex in cat_examples[cat]:
            f.write(f"- {ex}\n")

    f.write("\n---\n\n## 🩹 페인별 대표 답변\n\n")
    for p, cnt in pain_counter.most_common():
        f.write(f"\n### {p} ({cnt}건)\n")
        for ex in pain_examples[p]:
            f.write(f"- {ex}\n")

    f.write("\n---\n\n## 💎 100자+ 깊은 답변 (TOP 30)\n\n")
    for w in sorted(long_entries, key=lambda x: -len(x["text"]))[:30]:
        f.write(f"- **[{w['date'][:10]}]** _{w['plan']}_ — {w['text']}\n")

    f.write("\n---\n\n## 🌀 미분류 답변 샘플 (20)\n\n")
    for t in unclassified[:20]:
        f.write(f"- {t}\n")

print(f"[save] {OUT}")
print(f"[stats] categories: {len(cat_counter)}, verbs: {len(verb_counter)}, pains: {len(pain_counter)}")
print(f"[stats] long (100+): {len(long_entries)}, unclassified: {len(unclassified)}")
print("\nTOP CATEGORIES:")
for cat, cnt in cat_counter.most_common(10):
    print(f"  {cat}: {cnt} ({cnt/len(wishes)*100:.1f}%)")
print("\nTOP PAINS:")
for p, cnt in pain_counter.most_common(8):
    print(f"  {p}: {cnt}")
print("\nTOP VERBS:")
for v, cnt in verb_counter.most_common(8):
    print(f"  {v}: {cnt}")
