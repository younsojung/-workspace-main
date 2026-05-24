#!/usr/bin/env python3
"""
younsojung.co.kr 메뉴 페이지 전수 크롤러
- 풀페이지 스크린샷 + 섹션 스크린샷
- DOM 텍스트(태그별) 추출
- 이미지 src/alt 수집
- 모든 a 태그 텍스트 (CTA 후보) 수집
"""
import os
import sys
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_ROOT = Path("/Users/sojungyoun/Desktop/claude/workspace-main/10-projects/younsojung-site-renewal/data/copy-raw")

PAGES = [
    ("00", "home",                 "https://younsojung.co.kr/home"),
    ("01", "About-처음이라면",       "https://younsojung.co.kr/About"),
    ("02", "firstthought-생각이처음이라면", "https://younsojung.co.kr/firstthought"),
    ("03", "102030-연대기",         "https://younsojung.co.kr/102030"),
    ("04", "ebook-생각80편",        "https://younsojung.co.kr/ebook"),
    ("05", "etimeline-Ebook",       "https://younsojung.co.kr/etimeline"),
    ("06", "btopic-한정판실물도서",   "https://younsojung.co.kr/btopic"),
    ("07", "subscribe-생각구독신청", "https://younsojung.co.kr/subscribe"),
    ("08", "subscribeopen-오픈알림", "https://younsojung.co.kr/subscribeopen"),
    ("09", "insideroom-오프라인",    "https://younsojung.co.kr/insideroom"),
    ("10", "95-생각마라톤",          "https://younsojung.co.kr/95"),
    ("11", "community-커뮤니티",     "https://younsojung.co.kr/community"),
]


def sanitize(text, maxlen=300):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > maxlen:
        text = text[:maxlen] + "..."
    return text


def crawl_page(page, url, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"  - goto {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    try:
        page.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    page.wait_for_timeout(2500)

    # Scroll to bottom to trigger lazy-load
    height = page.evaluate("document.body.scrollHeight")
    step = 800
    pos = 0
    while pos < height:
        page.evaluate(f"window.scrollTo(0, {pos})")
        page.wait_for_timeout(350)
        pos += step
        new_h = page.evaluate("document.body.scrollHeight")
        if new_h > height:
            height = new_h
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(800)

    # Full-page screenshot
    full_shot = out_dir / "fullpage.png"
    page.screenshot(path=str(full_shot), full_page=True)
    print(f"    screenshot -> {full_shot.name} ({full_shot.stat().st_size//1024} KB)")

    # Sectional screenshots: scroll viewport-by-viewport
    viewport_h = page.viewport_size["height"]
    page_h = page.evaluate("document.body.scrollHeight")
    section_files = []
    i = 0
    y = 0
    while y < page_h:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(400)
        section_path = out_dir / f"section_{i:02d}.png"
        page.screenshot(path=str(section_path), full_page=False)
        section_files.append(section_path.name)
        i += 1
        y += viewport_h
        if i > 30:
            break
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)

    # Extract DOM data
    data = page.evaluate(r"""() => {
        const out = {title: document.title, url: location.href, headings: [], paragraphs: [], buttons: [], links: [], images: [], visible_text_blocks: []};

        // Headings
        document.querySelectorAll('h1,h2,h3,h4,h5,h6').forEach(h => {
            const t = (h.innerText || '').trim();
            if (t) out.headings.push({tag: h.tagName.toLowerCase(), text: t});
        });

        // Paragraphs / spans / divs with direct text
        const TEXT_TAGS = ['p', 'li', 'blockquote', 'figcaption'];
        TEXT_TAGS.forEach(tag => {
            document.querySelectorAll(tag).forEach(el => {
                const t = (el.innerText || '').trim();
                if (t && t.length > 1 && t.length < 800) {
                    out.paragraphs.push({tag, text: t});
                }
            });
        });

        // Buttons & CTA-like elements
        document.querySelectorAll('button, [role="button"], .btn, [class*="btn"], [class*="cta"], [class*="Button"]').forEach(b => {
            const t = (b.innerText || b.getAttribute('aria-label') || '').trim();
            if (t && t.length < 100) out.buttons.push(t);
        });

        // All anchors with text
        document.querySelectorAll('a').forEach(a => {
            const t = (a.innerText || '').trim();
            const href = a.getAttribute('href') || '';
            if (t && t.length < 200) out.links.push({text: t, href});
        });

        // Images
        document.querySelectorAll('img').forEach(img => {
            const src = img.currentSrc || img.src || '';
            const alt = img.alt || '';
            const title = img.title || '';
            // Position
            const r = img.getBoundingClientRect();
            const top = r.top + window.scrollY;
            out.images.push({src, alt, title, top: Math.round(top), w: Math.round(r.width), h: Math.round(r.height)});
        });

        // Visible text blocks (for "carved-in" copy that's actually text)
        // Walk body, collect non-trivial text nodes
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
        let n;
        while ((n = walker.nextNode())) {
            const t = (n.nodeValue || '').trim();
            if (t.length > 3 && t.length < 600) {
                const el = n.parentElement;
                if (!el) continue;
                const tag = el.tagName.toLowerCase();
                if (['script','style','noscript'].includes(tag)) continue;
                const r = el.getBoundingClientRect();
                if (r.width === 0 && r.height === 0) continue;
                out.visible_text_blocks.push({text: t, tag, top: Math.round(r.top + window.scrollY)});
            }
        }

        return out;
    }""")

    # Save raw DOM data
    with open(out_dir / "dom.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Dedupe & sort visible text blocks by top
    seen = set()
    sorted_blocks = []
    for b in sorted(data["visible_text_blocks"], key=lambda x: x["top"]):
        key = b["text"].strip()
        if key in seen:
            continue
        seen.add(key)
        sorted_blocks.append(b)

    # Save markdown (DOM-side copy)
    md = []
    md.append(f"# DOM 텍스트: {data['title']}\n")
    md.append(f"- URL: {url}\n")
    md.append(f"- 풀페이지: ./fullpage.png\n")
    md.append(f"- 섹션 캡처: {len(section_files)}장 (section_00 ~ section_{len(section_files)-1:02d})\n")
    md.append("")
    md.append("## Headings\n")
    for h in data["headings"]:
        md.append(f"- ({h['tag']}) {h['text']}")
    md.append("")
    md.append("## Paragraphs / List Items\n")
    for p in data["paragraphs"][:200]:
        md.append(f"- ({p['tag']}) {sanitize(p['text'], 500)}")
    md.append("")
    md.append("## Buttons / CTA 후보\n")
    seen_b = set()
    for b in data["buttons"]:
        if b in seen_b:
            continue
        seen_b.add(b)
        md.append(f"- {b}")
    md.append("")
    md.append("## Links (anchor text + href)\n")
    seen_l = set()
    for l in data["links"]:
        key = (l['text'], l['href'])
        if key in seen_l or not l['text']:
            continue
        seen_l.add(key)
        md.append(f"- [{sanitize(l['text'],120)}]({l['href']})")
    md.append("")
    md.append("## Images (위에서 아래로)\n")
    for img in sorted(data["images"], key=lambda x: x["top"]):
        md.append(f"- top={img['top']}  {img['w']}x{img['h']}  alt=\"{img['alt']}\"  src={img['src']}")
    md.append("")
    md.append("## Visible Text Blocks (위→아래 순서, 중복 제거)\n")
    md.append("> 이 항목은 DOM 상의 *진짜* 텍스트. 이미지 위에 박힌 카피는 OCR이 필요함 (스크린샷 참고).\n")
    for b in sorted_blocks:
        md.append(f"- top={b['top']:>5} ({b['tag']}) {sanitize(b['text'], 500)}")

    (out_dir / "dom.md").write_text("\n".join(md), encoding="utf-8")
    return data, section_files


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None  # e.g. "00,01,02"
    only_set = set(only.split(",")) if only else None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900},
                                      user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()

        for num, name, url in PAGES:
            if only_set and num not in only_set:
                continue
            slug = f"{num}_{name}"
            print(f"[{num}] {name}")
            out_dir = OUT_ROOT / slug
            try:
                crawl_page(page, url, out_dir)
            except Exception as e:
                print(f"  ! error: {e}")
                (out_dir / "ERROR.txt").write_text(str(e), encoding="utf-8")

        browser.close()
    print("DONE")


if __name__ == "__main__":
    main()
