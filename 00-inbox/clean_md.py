#!/usr/bin/env python3
"""Clean PDF-converted markdown: strip zero-width spaces, empty bold markers, normalize whitespace."""
from __future__ import annotations
import re
import sys
from pathlib import Path

ZERO_WIDTH = ['​', '‌', '‍', '﻿']

def clean_text(txt: str) -> str:
    for z in ZERO_WIDTH:
        txt = txt.replace(z, '')
    # Empty bold patterns: ** **, **,**, **.**, **?**
    txt = re.sub(r'\*\*\s*\*\*', '', txt)
    txt = re.sub(r'\*\*([,.\?!\s])\*\*', r'\1', txt)
    # Empty heading-only lines (####, ## 등 단독)
    txt = re.sub(r'(?m)^\s*#{1,6}\s*$', '', txt)
    # Collapse runs of spaces (keep newlines)
    txt = re.sub(r'[ \t]+', ' ', txt)
    # Collapse 3+ consecutive newlines → 2
    txt = re.sub(r'\n{3,}', '\n\n', txt)
    # Drop lines that are now whitespace-only
    lines = [l.rstrip() for l in txt.split('\n')]
    out = []
    prev_blank = False
    for l in lines:
        if not l.strip():
            if not prev_blank:
                out.append('')
            prev_blank = True
        else:
            out.append(l)
            prev_blank = False
    return '\n'.join(out).strip() + '\n'

def main():
    src_dir = Path(sys.argv[1] if len(sys.argv) > 1 else '/Users/sojungyoun/Desktop/claude/writer/전체호-md')
    out_dir = src_dir / '_clean'
    out_dir.mkdir(exist_ok=True)
    cnt = 0
    for f in sorted(src_dir.glob('*.md')):
        if f.name.startswith('_'):
            continue
        raw = f.read_text(encoding='utf-8')
        clean = clean_text(raw)
        out = out_dir / f.name
        out.write_text(clean, encoding='utf-8')
        print(f'{f.name}: {len(raw):,} → {len(clean):,} chars')
        cnt += 1
    print(f'=== cleaned {cnt} files → {out_dir} ===')

if __name__ == '__main__':
    main()
