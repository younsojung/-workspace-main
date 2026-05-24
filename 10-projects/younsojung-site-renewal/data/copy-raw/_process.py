#!/usr/bin/env python3
"""
크롤링 + OCR 결과를 카피라이터 워크북용 markdown으로 정리.
각 페이지 폴더에 copy.md 생성 + INDEX.md 마스터 작성.

입력:
  <dir>/dom.json          - DOM 데이터
  <dir>/ocr_sections.tsv  - Apple Vision OCR (블록별, 위→아래)
  <dir>/fullpage.png      - 풀페이지 스크린샷
  <dir>/section_NN.png    - 섹션 스크린샷

출력:
  <dir>/copy.md           - 페이지별 카피라이터 워크북
  INDEX.md                - 전체 페이지 인덱스 (마스터)
"""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path("/Users/sojungyoun/Desktop/claude/workspace-main/10-projects/younsojung-site-renewal/data/copy-raw")

# 메뉴 메타데이터: (번호, 폴더명, URL, 메뉴라벨, 노트)
PAGES = [
    ("00", "00_home",                   "https://younsojung.co.kr/home",          "홈 (메인 페이지)", "사이트 진입 페이지"),
    ("01", "01_About-처음이라면",        "https://younsojung.co.kr/About",         "처음이라면",        "윤소정 입문/소개"),
    ("02", "02_firstthought-생각이처음이라면", "https://younsojung.co.kr/firstthought", "윤소정의 생각이 처음이라면?", "About과 같은 페이지로 리다이렉트됨 (중복)"),
    ("03", "03_102030-연대기",           "https://younsojung.co.kr/102030",        "윤소정 연대기",     "10/20/30대 연대기"),
    ("04", "04_ebook-생각80편",          "https://younsojung.co.kr/ebook",         "윤소정의 생각 80편", "E-book 카탈로그"),
    ("05", "05_etimeline-Ebook",         "https://younsojung.co.kr/etimeline",     "E-book",            "ebook과 동일 페이지로 리다이렉트됨 (중복)"),
    ("06", "06_btopic-한정판실물도서",    "https://younsojung.co.kr/btopic",        "한정판 (실물도서)", "실물도서 카탈로그"),
    ("07", "07_subscribe-생각구독신청",   "https://younsojung.co.kr/subscribe",     "생각구독 신청",    "메인 상품 - 월간 구독"),
    ("08", "08_subscribeopen-오픈알림",   "https://younsojung.co.kr/subscribeopen", "생각구독 오픈 알림", "매월 말일 24시간 OPEN"),
    ("09", "09_insideroom-오프라인",      "https://younsojung.co.kr/insideroom",    "오프라인 / 인사이드룸", "오프라인 공간"),
    ("10", "10_95-생각마라톤",            "https://younsojung.co.kr/95",            "생각 마라톤",      "챌린지/이벤트"),
    ("11", "11_community-커뮤니티",       "https://younsojung.co.kr/community",     "커뮤니티",         "회원 커뮤니티"),
]

# About == firstthought, ebook == etimeline (확인됨)
DUPES = {"02_firstthought-생각이처음이라면": "01_About-처음이라면",
         "05_etimeline-Ebook":              "04_ebook-생각80편"}


def parse_ocr(tsv_path: Path):
    """Parse OCR TSV -> list of (section_index, y_local, text) sorted globally."""
    if not tsv_path.exists():
        return []
    blocks_by_section = []  # [(section_idx, [(y, text), ...]), ...]
    cur_section = -1
    cur_lines = []
    section_idx_from_path = lambda p: int(re.search(r"section_(\d+)", p).group(1))

    for raw in tsv_path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("===IMAGE:"):
            if cur_lines:
                blocks_by_section.append((cur_section, cur_lines))
            try:
                cur_section = section_idx_from_path(raw)
            except Exception:
                cur_section += 1
            cur_lines = []
        else:
            if "\t" in raw:
                y_s, text = raw.split("\t", 1)
                try:
                    y = int(y_s)
                except ValueError:
                    continue
                text = text.strip()
                if text and text != "ERROR: could not read image":
                    cur_lines.append((y, text))
    if cur_lines:
        blocks_by_section.append((cur_section, cur_lines))

    # Sort each section's lines by y, return flat list
    flat = []
    for sec_idx, lines in blocks_by_section:
        lines.sort()
        for y, t in lines:
            flat.append((sec_idx, y, t))
    return flat


def dedupe_consecutive(lines):
    """Remove consecutive duplicate texts."""
    out = []
    prev = None
    for item in lines:
        text = item[-1] if isinstance(item, tuple) else item
        if text != prev:
            out.append(item)
            prev = text
    return out


HEADER_NOISE = {
    "처음이라면", "윤소정의 생각이 처음이라면?", "윤소정 연대기", "윤소정의 생각 80편",
    "E-book", "한정판 (실물도서)", "생각구독 신청", "오프라인", "인사이드룸 방문하기",
    "생각 마라톤", "커뮤니티", "윤소정의 생각구독", "윤소정의 생각", "MENU", "LOGIN", "MY",
    "장바구니", "Q", "윤소정", "site search", "0",
    "마이페이지", "로그아웃", "로그인", "로그인이 필요합니다.",
    "오프라인 / 인사이드룸",
    "이용약관", "개인정보처리방침",
}

FOOTER_NOISE = {
    "카카오톡 채널 @truspia",
    "고객센터", "사업자 정보", "상호",
}


def is_noise(text):
    t = text.strip()
    if not t:
        return True
    if t in HEADER_NOISE:
        return True
    if t in FOOTER_NOISE:
        return True
    # Single-letter or punctuation only
    if len(t) <= 1 and not t.isdigit():
        return True
    return False


def classify_line(text):
    """Rough heuristic to tag a line as CTA/Heading/Body."""
    t = text.strip()
    # CTA cues
    cta_patterns = ["보러가기", "신청하기", "보기", "더보기", "방문하기", "구매하기", "알림 신청", "OPEN",
                    "구독 신청", "지금 ", "→", ">", "click", "Click", "CLICK", "신청"]
    for p in cta_patterns:
        if p in t and len(t) < 40:
            return "CTA"
    if len(t) < 30 and t.endswith("?"):
        return "질문"
    if len(t) < 30:
        return "타이틀"
    return "본문"


def process_page(num, slug, url, label, note):
    page_dir = ROOT / slug
    out_path = page_dir / "copy.md"

    # Handle duplicates
    if slug in DUPES:
        target = DUPES[slug]
        out_path.write_text(
            f"# {num}. {label}\n\n"
            f"- URL: {url}\n"
            f"- **상태**: 이 페이지는 `{target}` 로 리다이렉트됨 (실제 콘텐츠 동일).\n"
            f"- 따라서 카피는 `{target}/copy.md` 참고.\n"
            f"- 참고 노트: {note}\n",
            encoding="utf-8"
        )
        return {"num": num, "slug": slug, "url": url, "label": label,
                "headlines": [], "cta": [], "body_count": 0, "is_dupe": True, "dupe_of": target}

    # Load DOM
    dom_path = page_dir / "dom.json"
    if not dom_path.exists():
        return None
    dom = json.loads(dom_path.read_text(encoding="utf-8"))

    # Parse OCR
    ocr_lines = parse_ocr(page_dir / "ocr_sections.tsv")

    # Build text blocks for the workbook from OCR (top→bottom), filter noise
    workbook_lines = []
    for sec_idx, y, t in ocr_lines:
        if is_noise(t):
            continue
        workbook_lines.append((sec_idx, y, t))
    workbook_lines = dedupe_consecutive(workbook_lines)

    # Classify
    ctas = []
    headlines = []
    body_count = 0
    classified = []
    for sec_idx, y, t in workbook_lines:
        kind = classify_line(t)
        if kind == "CTA":
            ctas.append(t)
        elif kind == "타이틀" or kind == "질문":
            headlines.append(t)
        else:
            body_count += 1
        classified.append((sec_idx, y, kind, t))

    # Also gather DOM-side visible text for cross-reference
    dom_blocks = sorted({(b["top"], b["text"]) for b in dom.get("visible_text_blocks", [])
                         if not is_noise(b["text"])}, key=lambda x: x[0])

    dom_buttons = []
    for b in dom.get("buttons", []):
        bt = b.strip()
        if bt and not is_noise(bt) and bt not in dom_buttons:
            dom_buttons.append(bt)

    dom_anchors = []
    seen = set()
    for a in dom.get("links", []):
        text = a.get("text", "").strip()
        href = a.get("href", "")
        if not text or is_noise(text):
            continue
        if "javascript:" in href:
            continue
        if href.startswith("https://younsojung.co.kr/") or href.startswith("http"):
            key = (text, href)
            if key in seen:
                continue
            seen.add(key)
            # Skip if it's clearly a navigation header link (already in HEADER_NOISE)
            dom_anchors.append((text, href))

    # Build markdown
    md = []
    md.append(f"# {num}. {label}")
    md.append("")
    md.append(f"- **URL**: {url}")
    md.append(f"- **참고**: {note}")
    md.append(f"- **풀페이지 스크린샷**: ./fullpage.png")
    section_files = sorted(p.name for p in page_dir.glob("section_*.png"))
    md.append(f"- **섹션 스크린샷**: {len(section_files)}장 (`{section_files[0] if section_files else ''}` ~ `{section_files[-1] if section_files else ''}`)")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## A. 카피 (이미지에 박힌 텍스트 = OCR 결과, 위→아래 순서)")
    md.append("")
    md.append("> 메뉴/푸터/공통 UI는 자동 제거됨. 섹션별 구분.")
    md.append("")

    if not classified:
        md.append("_(OCR 결과 없음 — 이 페이지는 이미지 카피가 없거나 OCR이 실패)_")
        md.append("")
    else:
        cur_sec = -1
        for sec_idx, y, kind, t in classified:
            if sec_idx != cur_sec:
                cur_sec = sec_idx
                md.append("")
                md.append(f"### Section {sec_idx:02d}  (`section_{sec_idx:02d}.png`)")
                md.append("")
            tag = {"CTA": "**[CTA]**", "타이틀": "**[타이틀]**", "질문": "**[질문]**", "본문": ""}[kind]
            md.append(f"- {tag} {t}".rstrip())

    md.append("")
    md.append("---")
    md.append("")
    md.append("## B. 버튼 / CTA (DOM 기준)")
    md.append("")
    if dom_buttons:
        for b in dom_buttons:
            md.append(f"- {b}")
    else:
        md.append("_(DOM 상 button 요소 없음)_")
    md.append("")

    md.append("## C. 링크 (앵커 텍스트 + 목적지)")
    md.append("")
    if dom_anchors:
        for text, href in dom_anchors[:80]:
            t = re.sub(r"\s+", " ", text)[:120]
            md.append(f"- [{t}]({href})")
    else:
        md.append("_(외부 링크 없음)_")
    md.append("")

    md.append("## D. DOM 텍스트 (HTML 안의 실제 텍스트 — 이미지 위 텍스트 아님)")
    md.append("")
    md.append("> OCR이 아닌, HTML DOM 상의 텍스트. 이미지 카피와 비교하여 일반 본문 영역을 분리할 때 사용.")
    md.append("")
    if dom_blocks:
        seen_txt = set()
        for top, txt in dom_blocks:
            key = txt.strip()
            if key in seen_txt:
                continue
            seen_txt.add(key)
            txt_oneline = re.sub(r"\s+", " ", txt)[:400]
            md.append(f"- (top≈{top}) {txt_oneline}")
    else:
        md.append("_(DOM 상 의미있는 텍스트 블록 없음 — 카피가 전부 이미지인 페이지)_")
    md.append("")

    md.append("## E. 이미지 인벤토리")
    md.append("")
    imgs = sorted(dom.get("images", []), key=lambda i: i.get("top", 0))
    if imgs:
        md.append("| top | 크기 | alt | src |")
        md.append("|---|---|---|---|")
        for img in imgs[:80]:
            src = img.get("src", "")
            alt = (img.get("alt", "") or "").replace("|", "\\|")[:80]
            w = img.get("w", "?")
            h = img.get("h", "?")
            short_src = src.split("?")[0]
            if len(short_src) > 80:
                short_src = "..." + short_src[-77:]
            md.append(f"| {img.get('top',0)} | {w}x{h} | {alt} | `{short_src}` |")
    else:
        md.append("_(이미지 없음)_")
    md.append("")

    out_path.write_text("\n".join(md), encoding="utf-8")

    return {"num": num, "slug": slug, "url": url, "label": label,
            "headlines": headlines, "ctas": ctas, "body_count": body_count,
            "is_dupe": False, "section_count": len(section_files),
            "image_count": len(imgs), "anchor_count": len(dom_anchors)}


def build_index(results):
    md = []
    md.append("# 윤소정의 생각구독 사이트 — 메뉴별 카피 인덱스")
    md.append("")
    md.append("> Source: https://younsojung.co.kr/ — Crawled: 2026-05-23")
    md.append("> Method: Playwright(렌더링 + 스크롤) + Apple Vision OCR(ko-KR, accurate)")
    md.append("> 목적: 카피라이터 워크북용 — 사이트 전체 메뉴 카피를 한 곳에서 비교")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 페이지 목록")
    md.append("")
    md.append("| # | 메뉴 | URL | 상태 | 카피 노트 |")
    md.append("|---|---|---|---|---|")
    for r in results:
        if r is None:
            continue
        status = "**중복**" if r.get("is_dupe") else "OK"
        link = f"[`copy.md`](./{r['slug']}/copy.md)"
        note = ""
        if r.get("is_dupe"):
            note = f"→ `{r['dupe_of']}` 로 리다이렉트"
        else:
            sec = r.get("section_count", 0)
            img = r.get("image_count", 0)
            hl = len(r.get("headlines", []))
            ct = len(r.get("ctas", []))
            note = f"섹션 {sec} · 이미지 {img} · 타이틀/질문 {hl} · CTA {ct}"
        md.append(f"| {r['num']} | {r['label']} | [{r['url']}]({r['url']}) | {status} {link} | {note} |")
    md.append("")
    md.append("---")
    md.append("")

    # Quick-skim: all headlines, all CTAs, by page
    md.append("## 페이지별 핵심 헤드라인 + CTA (빠른 비교용)")
    md.append("")
    for r in results:
        if r is None or r.get("is_dupe"):
            continue
        md.append(f"### {r['num']}. {r['label']}")
        md.append(f"_{r['url']}_")
        md.append("")
        if r.get("headlines"):
            md.append("**타이틀/질문 (이미지에 박힌 짧은 카피)**:")
            for h in r["headlines"][:30]:
                md.append(f"- {h}")
        else:
            md.append("_(타이틀형 카피 없음)_")
        md.append("")
        if r.get("ctas"):
            md.append("**CTA 후보**:")
            for c in r["ctas"][:20]:
                md.append(f"- {c}")
        else:
            md.append("_(명시적 CTA 텍스트 미검출)_")
        md.append("")
        md.append("---")
        md.append("")

    md.append("## 파일 구조")
    md.append("")
    md.append("```")
    md.append("copy-raw/")
    md.append("├── INDEX.md                  ← 이 파일")
    md.append("├── _crawl.py                 ← Playwright 크롤러")
    md.append("├── _process.py               ← OCR/DOM → markdown 변환기")
    md.append("└── NN_<메뉴명>/")
    md.append("    ├── copy.md               ← 페이지별 카피라이터 워크북")
    md.append("    ├── dom.md                ← DOM 텍스트 덤프 (참고용)")
    md.append("    ├── dom.json              ← DOM 원본 데이터")
    md.append("    ├── ocr_sections.tsv      ← Apple Vision OCR 원본")
    md.append("    ├── fullpage.png          ← 풀페이지 스크린샷")
    md.append("    └── section_NN.png        ← 섹션별 스크린샷 (뷰포트 단위)")
    md.append("```")
    md.append("")

    (ROOT / "INDEX.md").write_text("\n".join(md), encoding="utf-8")


def main():
    results = []
    for num, slug, url, label, note in PAGES:
        if not (ROOT / slug).exists():
            print(f"  ! skip {slug} (dir missing)")
            results.append(None)
            continue
        r = process_page(num, slug, url, label, note)
        results.append(r)
        print(f"  ok {num} {slug}")
    build_index(results)
    print(f"\nINDEX written: {ROOT/'INDEX.md'}")


if __name__ == "__main__":
    main()
