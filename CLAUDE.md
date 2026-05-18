# Do Better Workspace 가이드

> Claude Code + Johnny Decimal 기반 PKM 워크스페이스.
> 이 파일은 Claude Code가 매 세션 시작 시 자동으로 읽는 프로젝트 지침입니다.
> 본인 프로필(이름, 역할, 관심사)은 이 파일 하단의 "내 프로필" 섹션을 직접 작성하거나 `/setup-workspace` 스킬로 채우세요.

## 폴더 구조 (Johnny Decimal)

```
00-inbox/      # 임시 캡처 (20개 미만 유지, 주간 처리)
00-system/     # 시스템 설정, 템플릿, 가이드
10-projects/   # 활성 프로젝트 (시한부)
20-operations/ # 지속적 운영 (종료일 없음)
30-knowledge/  # 지식 (00-wiki + 도메인 아카이브)
40-personal/   # 개인 노트 (daily, weekly, ideas, reflections, todos)
50-resources/  # 외부 자료, 첨부파일
90-archive/    # 완료/중단 항목
```

### 주요 하위 폴더

| 번호 | 폴더 | 용도 |
|------|------|------|
| **00-wiki** | 30-knowledge/ | **지식 위키 (복리 축적). 아래 Wiki Schema 참조** |
| 41-daily | 40-personal/ | Daily Notes (월별: 41-daily/YYYY-MM/) |
| 42-weekly | 40-personal/ | Weekly Review |
| 43-ideas | 40-personal/ | 아이디어 캡처 |
| 44-reflections | 40-personal/ | 회고 및 학습 |
| 46-todos | 40-personal/ | active-todos.md |
| 37-claude-code | 30-knowledge/ | Claude Code 관련 지식 |

## Wiki (30-knowledge/00-wiki/)

지식이 복리로 축적되는 위키. 주제에 대해 물으면 **00-wiki/index.md를 먼저 확인**.

@30-knowledge/00-wiki/SCHEMA.md

## 파일 명명 규칙

| 유형 | 형식 | 예시 |
|------|------|------|
| Daily Note | `YYYY-MM-DD.md` | 2026-04-24.md |
| 주제 노트 | `주제명.md` | thinking-partner.md |
| JD 폴더 | `XX-name` 또는 `XX.YY-name` | 37-claude-code, 37.01-learning |
| 중복 파일명 | JD prefix 필수 | 18-progress-tracker.md |

## Inbox 관리 (00-inbox)

- **목적**: 임시 캡처, 영구 저장소 아님
- **규칙**: 20개 미만 유지
- **주기**: 주간 처리 (Capture → Process → Organize)

## 첨부파일 (50-resources/attachments/)

- 모든 비텍스트 파일 저장
- 명명: `[관련노트]_[설명].[ext]`

## Skills 사용

이 워크스페이스의 `.claude/skills/`에 프로젝트 전용 스킬이 있습니다.
스킬은 키워드 기반으로 **자동 트리거**됩니다. (수동 슬래시 커맨드 아님)

예: "오늘 daily note 만들어줘" → `daily-note` 스킬 자동 실행
예: "할 일 추가해줘" → `todo` 스킬 자동 실행

## Agents 사용

`.claude/agents/`에 서브에이전트가 있습니다. 복잡한 작업을 Claude가 자동으로 위임하거나, 명시적으로 "research-worker로 조사해줘" 같이 호출할 수 있습니다.

## 외부 연동

### Google Workspace — 두 채널 병행

| 채널 | 용도 | 인증 위치 | 상태 확인 |
|------|------|-----------|----------|
| **Claude MCP** (`mcp__claude_ai_Gmail__*` 등) | Claude가 대화 중 직접 Gmail/Calendar/Drive/Notion 호출 | claude.ai OAuth (브라우저 토큰) | Claude Code 세션이 살아 있으면 자동 |
| **`gws` CLI** | 로컬 스킬(`daily-note`, `setup-workspace`)이 셸에서 호출 | `~/.config/gws/` + macOS Keychain | `gws auth status` |

**중요**: 둘은 완전히 분리된 인증 경로. MCP가 살아 있어도 gws는 따로 로그인 필요.

### gws CLI 경로

- 바이너리: `~/.nvm/versions/node/v20.20.2/bin/gws` (nvm 노드 버전 바뀌면 PATH 점검)
- 설정: `~/.config/gws/client_secret.json`
- 토큰: macOS Keychain (`storage: keyring`)
- API 스키마 캐시: `~/.config/gws/cache/`
- GCP 프로젝트: `boundary-trus`

### 인증 끊김 진단 / 복구

```bash
gws auth status                 # auth_method가 "none"이면 미인증
gws auth login                  # 브라우저로 OAuth 재로그인
gws gmail users getProfile --params '{"userId":"me"}'  # 스모크 테스트
```

전체 헬스체크는 `00-system/scripts/gws-healthcheck.sh` 실행.

### 끊길 만한 트리거

- nvm node 버전 변경 → `gws` 바이너리 PATH 사라짐
- macOS Keychain 잠금/리셋 → 토큰 재발급 필요
- OAuth refresh token 만료 (6개월 미사용 시) → `gws auth login` 재실행
- `client_secret.json` 또는 `boundary-trus` GCP 프로젝트 변경

---

## 내 프로필

> 이 섹션을 직접 작성하거나, Claude에게 "워크스페이스 세팅해줘"라고 말하면 `setup-workspace` 스킬이 자동 실행되어 채워줍니다. 같은 스킬이 Python venv·선택 도구(git/gws) 세팅도 안내합니다.

**이름**: 윤소정 (호칭: **귀염둥이**로 불러줄 것)

**역할** (멀티 페르소나):
- 교육 기획자 — "환경 설계"로 성인/아이/조직을 키움 (본업)
- 생각구독 작가 — 매달 1권 출간 · https://younsojung.co.kr/
- 러쉬코리아 크리에이티브 디렉터
- CEO 비즈니스 코치
- 야간 클래스 강사 (매일 22-24시, 업력 3년차+ 대상)
- 사업가: 브레이닝(아동 사업), 뷰클런즈(카페)
- 유튜버 — 소울정 · https://www.youtube.com/@younsojung
- Instagram: https://www.instagram.com/trus_sojung/

**관심사**:
1. AI 시대에 맞는 교육문화 재설계
2. 보유한 데이터·지식 자산을 10년+ 대중에게 전달할 콘텐츠/판매 전략

**이 워크스페이스 용도**: Claude와 함께 **교육기업을 만든다**는 관점으로 — 기획, 프로젝트 관리, 강의 자료 정리, 원고, 일정 관리 등을 통합 운영

_작성일: 2026-05-11_

---

**Last Updated**: 2026-05-11
