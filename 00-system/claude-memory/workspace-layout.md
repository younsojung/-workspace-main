---
name: workspace-layout
description: "~/Desktop/claude/ 4개 폴더 매핑 — workspace-main, designer, cardnews-dashboard, boundary-trus-main"
metadata: 
  node_type: memory
  type: reference
  originSessionId: a984fe46-d00f-46cb-a5d7-871b1bfd6910
---

## ~/Desktop/claude/ 디렉토리 매핑

```
/Users/sojungyoun/Desktop/claude/
├── workspace-main/         # PKM (Johnny Decimal). Claude Code 기본 작업 디렉토리
├── designer/               # 🎬 영상·카드뉴스 작업 본진 (5.2GB)
├── cardnews-dashboard/     # Flask 대시보드 앱
└── boundary-trus-main/     # 노정석 과외노트 (HTML/PDF). 트루스/boundary 강의자료
```

## 각 폴더 핵심 자산

### workspace-main/ (PKM)
- 00-system, 10-projects (dryrun-ai, google-drive-reorg, 숫자언어-기획)
- 30-knowledge/00-wiki, 37-claude-code
- 40-personal (41-daily, 43-ideas, 46-todos)
- .claude/agents + skills (23개 스킬)
- GitHub: [[github-setup]] 참조

### designer/ (영상 작업)
- 스크립트: `make_card_captions.py`, `make_card_videos.sh`, `make_reel.sh`, `make_slides.py`, `make_video_captions.py`
- PRD: `CARDNEWS_PRD.md`
- 미디어 폴더: `ai/` (1.9GB), `instagram_sojung'style/` (1.4GB), `maraton/` (809MB), `image/` (653MB), `output/` (255MB)
- **미디어는 git에 안 들어감** — 코드/스크립트/자막(.srt/.ass)만 GitHub 백업
- 카드뉴스 = 한 카드 → 한 영상 → 하나의 메시지 (cardnews skill 원칙)

### cardnews-dashboard/ (Flask)
- app.py, data/, modules/, static/, requirements.txt
- 카드뉴스.command (실행 단축)

### boundary-trus-main/
- index.html, 노정석_과외노트.html/pdf, 앤드엔 폴더

## 사용자가 "영상 작업" 언급 시

→ `designer/` 폴더 확인. workspace-main에는 영상 작업 결과물이 없음. 검색하려면 절대경로로.

## Related

[[user-profile]] · [[github-setup]]
