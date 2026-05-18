---
name: youtube-to-notion
description: YouTube URL을 받아 메타데이터/자막을 추출하고 Notion 유튜브 영상 아카이브 DB에 자동 정리. "유튜브 URL 저장", "유튜브 영상 정리", "노션에 영상 저장" 등을 언급하거나 youtube.com/youtu.be URL을 제공하면 자동 실행.
context: fork
allowed-tools:
  - Bash
  - Read
  - Write
---

# YouTube → Notion Skill

YouTube URL 한 줄 → Notion DB에 정리된 페이지 생성.

## Prerequisites

- `yt-dlp` (워크스페이스 `.venv`에 설치됨)
- `NOTION_TOKEN` (워크스페이스 `.env` 자동 로드)
- 대상 DB: **유튜브 영상 아카이브** — `35d9073fdb96811bbfcee7d6367df6ec`
- Notion integration이 부모 페이지(클로드코드(소정))에 연결되어 있어야 함

## 워크플로우

### Step 1: 추출 (메타데이터 + 자막)

```bash
.venv/bin/python3 .claude/skills/youtube-to-notion/scripts/youtube_handler.py \
  extract --url "https://youtu.be/VIDEO_ID" --pretty
```

출력 JSON 필드:
- `video_id`, `title`, `channel`, `channel_url`
- `upload_date` (YYYY-MM-DD), `duration`, `duration_seconds`
- `thumbnail_url`, `description`, `view_count`
- `source_url`
- `transcript`, `transcript_lang`, `transcript_source`, `transcript_available`

자막 우선순위:
1. 수동 자막 ko → 2. 수동 자막 en → 3. 자동 자막 ko → 4. 자동 자막 en

자막 없으면 description으로 fallback (요약 품질 저하 가능).

### Step 2: Claude의 분석

`transcript`(없으면 `description`)를 읽고 다음 필드를 생성:

- **`summary`**: 3-5문장 요약 (귀염둥이 톤)
- **`insights`**: 핵심 인사이트 — *학습자본 framework 관점*에서 (어떤 무지를 채울 수 있는지, 어느 구간[노력/성과/시스템]에 도움 되는지)
- **`category`**: 다음 중 1개
  - `AI/기술` · `교육` · `비즈니스` · `자기계발` · `라이프스타일` · `기타`
- **`tags`**: 3-5개 키워드 (배열)

### Step 3: 저장 (Notion 페이지 생성)

추출 결과 JSON에 위 4개 필드를 추가한 후 stdin으로 전달:

```bash
cat <<'EOF' | .venv/bin/python3 .claude/skills/youtube-to-notion/scripts/youtube_handler.py save --stdin
{
  "video_id": "...",
  "title": "...",
  "channel": "...",
  "upload_date": "2025-01-15",
  "duration": "12:34",
  "thumbnail_url": "https://i.ytimg.com/...",
  "source_url": "https://youtu.be/...",
  "summary": "...",
  "insights": "...",
  "category": "AI/기술",
  "tags": ["AI", "교육", "framework"]
}
EOF
```

응답:
```json
{
  "ok": true,
  "page_id": "...",
  "page_url": "https://www.notion.so/..."
}
```

## 필드 매핑 표

| Notion 필드 | 출처 |
|------------|------|
| 제목 (title) | yt-dlp `title` |
| URL | `source_url` |
| 채널 | yt-dlp `uploader` |
| 게시일 | yt-dlp `upload_date` → ISO |
| 썸네일 | yt-dlp `thumbnail` (Notion `files` external URL) |
| 카테고리 | Claude 분석 |
| 태그 | Claude 분석 |
| 요약 | Claude 분석 |
| 핵심 인사이트 | Claude 분석 (학습자본 관점) |
| 시청 상태 | 기본값 "미시청" |
| 추가일 | 오늘 날짜 (자동) |
| 중요도 | 비워둠 (시청 후 본인이 채움) |

## 🧓 톤 가이드 — "옆집 할머니 톤 + 학습자본 framework"

귀염둥이의 모든 영상 정리는 **이 톤**으로 통일.

### 톤 원칙

1. **기술 용어 없이** 또는 *바로 옆에 풀어쓰기* (예: "KV cache" → "메모해뒀다가 다시 쓰는 방식, 'KV cache'라고 불러요")
2. **일상 비유** — 음식점/손님, 책장/메모장 같은 친숙한 그림
3. **짧고 명료한 문장** — 한 문장에 한 아이디어
4. **"왜 너에게 의미 있는가"로 마무리** — 추상에서 본인 일상/사업으로 착륙
5. **본인 톤 흔적 포함** — "~예요", "~거든요", "근데" 같은 말투

### 인사이트는 항상 *학습자본 framework 관점*에서

귀염둥이의 framework 6개 명제를 인사이트의 렌즈로 사용:
1. 숫자는 언어다
2. 돈은 결과가 아니라 학습의 피드백
3. 학습자본이 미래 사회의 핵심 자본
4. 어른의 공부 = 내가 뭘 모르는지 찾는 것
5. 연봉 = 무지 좌표
6. 노력 → 성과 → 시스템 구간별 처방

특히 **이 영상이 귀염둥이의 '시스템 구간 이동(5천 → 100만 명)'에 어떻게 도움이 되는가**를 자주 짚어야 함.

### Claude가 분석할 때 따를 prompt 명세

```
당신은 귀염둥이(윤소정)의 학습 큐레이터입니다. 영상의 transcript(또는 description)를 받아서 다음을 작성하세요:

1. summary (3-5문장):
   - "옆집 할머니가 알아들을 정도로" 쉽게
   - 기술 용어는 비유로 풀거나 바로 옆에 설명
   - 본인 말투: "~예요", "~거든요"

2. insights (3-5문장):
   - 학습자본 framework 관점 (위 6개 명제 중 관련된 것)
   - 본인의 "시스템 구간 이동(5천 → 100만 명)"과의 연결
   - 끝에 "왜 귀염둥이에게 의미 있는가" 한 문장

3. category: AI/기술 · 교육 · 비즈니스 · 자기계발 · 라이프스타일 · 기타 중 1개

4. tags: 3-5개 키워드 (영상의 주제 핵심)
```

---

## 📅 채널 디제스트 워크플로우 (자동)

**대상 채널**: 노정석 — https://www.youtube.com/@chester_roh
**스케줄**: 매주 월요일 09:00 KST

### 자동 실행 단계 (Claude가 schedule로 깨어날 때)

```
1. list-channel로 최근 10개 영상 가져오기
   → .venv/bin/python3 youtube_handler.py list-channel --url "https://www.youtube.com/@chester_roh" --max 10

2. 각 영상마다 check-exists로 중복 확인
   → .venv/bin/python3 youtube_handler.py check-exists --video-id VIDEO_ID

3. exists=false 인 영상만 처리:
   a. extract --url URL --pretty
   b. transcript(또는 description) 읽고 위 톤 가이드대로 분석
   c. cat <<'EOF' | save --stdin

4. 완료 후 요약 보고 (몇 개 새 영상 처리했는지)
```

### 새 채널 추가하려면

SKILL.md의 이 섹션에 채널 추가, schedule 등록.

---

## 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| `yt-dlp not installed` | venv 미활성화 | `.venv/bin/python3` 명시 사용 |
| `NOTION_TOKEN not set` | `.env` 로드 실패 | 워크스페이스 루트 `.env` 확인 |
| `Notion API error 404` | DB ID 또는 integration 연결 문제 | DB 존재 확인, integration이 페이지에 연결됐는지 확인 |
| `transcript_available: false` | 자막 없음 (음악/짧은 영상 등) | description으로 fallback. 본인이 시청 후 수동 보강 권장 |
| Rich text 잘림 | Notion 2000자 제한 | 스크립트가 1900자에서 자동 truncate (`…` 추가) |

## 버전

- v1.0.0 (2026-05-11): 초기 작성 — extract + save 서브커맨드
