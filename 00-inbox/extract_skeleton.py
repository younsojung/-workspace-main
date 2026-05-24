#!/usr/bin/env python3
"""Extract structural skeleton from each cleaned 생각구독 MD.

For each file produce a compact skeleton showing:
- Opening (first ~80 non-empty lines)
- Closing (last ~80 non-empty lines)
- Chapter-pattern hits (01. / 02. / ... or 챕터/PART)
- Lines containing key markers (안녕, 영혼의 친구, BGM, Playlist, 라이브, bit.ly)

Output: one skeleton file per source.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

SRC = Path('/Users/sojungyoun/Desktop/claude/writer/전체호-md/_clean')
OUT = Path('/Users/sojungyoun/Desktop/claude/workspace-main/30-knowledge/생각구독-corpus/_skeletons')
OUT.mkdir(parents=True, exist_ok=True)

CHAPTER_RE = re.compile(r'^\s*0?\d{1,2}[.,]\s+\S')        # 01. / 02 . / 1.
PART_RE    = re.compile(r'(PART|CHAPTER|챕터|파트)\s*[\dIVX]+', re.I)
MARKER_RE  = re.compile(r'(안녕|영혼의\s*친구|BGM|Playlist|플리|라이브|bit\.?ly|naver\.me|선곡|네이버\s*카페)', re.I)
URL_RE     = re.compile(r'https?://\S+')

def is_meaningful(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if len(s) < 2:
        return False
    return True

def extract(md_path: Path) -> str:
    raw = md_path.read_text(encoding='utf-8')
    lines = raw.splitlines()
    meaningful = [(i, l) for i, l in enumerate(lines) if is_meaningful(l)]
    total_lines = len(lines)
    total_mean = len(meaningful)

    head = meaningful[:100]
    tail = meaningful[-80:] if len(meaningful) > 100 else []

    chapters = []
    markers = []
    for i, l in meaningful:
        s = l.strip()
        if CHAPTER_RE.match(s) or PART_RE.search(s):
            chapters.append((i, s))
        if MARKER_RE.search(s):
            markers.append((i, s))

    parts: list[str] = []
    parts.append(f'# Skeleton: {md_path.stem}')
    parts.append(f'(total lines: {total_lines}, non-empty: {total_mean})')
    parts.append('')
    parts.append('## OPENING (first 100 non-empty lines)')
    for i, l in head:
        parts.append(f'L{i+1:05d}: {l.strip()}')
    parts.append('')
    parts.append('## CLOSING (last 80 non-empty lines)')
    for i, l in tail:
        parts.append(f'L{i+1:05d}: {l.strip()}')
    parts.append('')
    parts.append(f'## CHAPTER-LIKE LINES ({len(chapters)} hits)')
    for i, l in chapters[:80]:
        parts.append(f'L{i+1:05d}: {l[:120]}')
    parts.append('')
    parts.append(f'## MARKER LINES ({len(markers)} hits — 영혼의 친구/BGM/Playlist/라이브 등)')
    for i, l in markers[:60]:
        parts.append(f'L{i+1:05d}: {l[:160]}')
    parts.append('')
    return '\n'.join(parts) + '\n'

def main():
    cnt = 0
    for f in sorted(SRC.glob('*.md')):
        if f.name.startswith('_'):
            continue
        skel = extract(f)
        out = OUT / f.name
        out.write_text(skel, encoding='utf-8')
        print(f'{f.name}: {len(skel):,} chars')
        cnt += 1
    print(f'=== {cnt} skeletons written → {OUT} ===')

if __name__ == '__main__':
    main()
