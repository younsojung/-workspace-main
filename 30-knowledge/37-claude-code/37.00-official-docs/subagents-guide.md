# Claude Code Subagents - Source of Truth

> **Source**: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents)
> **Updated**: 2026-04-24 (v2.1.119) - `mcp_tool` 훅, `--print`/`--agent` frontmatter 준수, MCP 병렬 연결, `duration_ms` 필드
> **Purpose**: Subagent 작성 시 유일한 참조 문서

---

## 1. 개요

서브에이전트는 격리된 컨텍스트 윈도우에서 커스텀 시스템 프롬프트, 특정 도구 접근, 독립적 권한으로 작업을 처리하는 특화된 AI 어시스턴트.

### 핵심 특징

- 컨텍스트 보존: 탐색/구현 작업을 메인 대화와 분리
- 제약 강제: 서브에이전트별 도구 접근 제한
- 설정 재사용: 사용자 레벨로 프로젝트 간 공유
- 비용 절감: 빠른/저렴한 모델(Haiku)로 작업 라우팅
- 자동 위임: Description에 따라 Claude가 자동 호출

---

## 2. 기본 제공 서브에이전트

| 에이전트 | 모델 | 도구 | 목적 |
|---------|------|------|------|
| **Explore** | Haiku | 읽기 전용 | 빠른 코드베이스 검색 및 분석 |
| **Plan** | 상속 | 읽기 전용 | 계획 모드 중 리서치 |
| **General-purpose** | 상속 | 모든 도구 | 복잡한 다단계 작업 |
| **Bash** | 상속 | 터미널 | 명령어 별도 실행 |
| **statusline-setup** | Sonnet | 설정 도구 | 상태줄 설정 |
| **Claude Code Guide** | Haiku | 읽기 전용 | Claude Code 사용법 안내 |

---

## 3. 파일 구조

### 저장 위치 (우선순위 순)

| 우선순위 | 위치 | 적용 범위 |
|---------|------|----------|
| 1 | `--agents` CLI 플래그 | 현재 세션만 |
| 2 | `.claude/agents/` | 프로젝트 |
| 3 | `~/.claude/agents/` | 모든 프로젝트 |
| 4 | Plugin의 `agents/` | 플러그인 활성화된 곳 |

동일 이름 시 높은 우선순위 버전 적용.

---

## 4. YAML Frontmatter 전체 필드

```yaml
---
name: agent-name
description: When to use this agent and what it does
tools: Tool1, Tool2, Tool3
disallowedTools: Bash, Write
model: sonnet
skills: skill-1, skill-2
permissionMode: acceptEdits
memory: project
background: false
isolation: worktree
mcpServers: server-1, server-2
maxTurns: 50
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/check.sh"
---
```

### 필드 상세

| 필드 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `name` | 권장 | 파일명 | 소문자, 하이픈만. 에이전트 고유 식별자. |
| `description` | 권장 | - | Claude가 언제 이 에이전트를 사용할지 판단 기준. |
| `tools` | - | 모든 도구 | 허용 목록 (allowlist). 쉼표 구분. |
| `disallowedTools` | - | 없음 | 거부 목록 (denylist). `tools`와 배타적 사용. |
| `model` | - | sonnet | `sonnet`, `opus`, `haiku`, `'inherit'` |
| `skills` | - | 없음 | 프리로드할 Skills. 전체 콘텐츠가 시작 시 주입됨. |
| `permissionMode` | - | default | 권한 동작 방식 (아래 참조). |
| `memory` | - | 없음 | **(신규 v2.1.33)** 세션 간 지속 메모리 스코프. |
| `background` | - | false | **(신규 v2.1.49)** `true`: 항상 백그라운드 실행. |
| `isolation` | - | 없음 | **(신규 v2.1.49)** `worktree`: 임시 git worktree 격리 실행. |
| `mcpServers` | - | 없음 | **(문서화됨)** 사용할 MCP 서버 지정. |
| `maxTurns` | - | 없음 | **(문서화됨)** 최대 에이전틱 턴 수 제한. |
| `hooks` | - | 없음 | 에이전트 라이프사이클 훅. |
| `initialPrompt` | - | 없음 | **(v2.1.83)** 에이전트 시작 시 자동 제출할 첫 턴 프롬프트. |
| `effort` | - | 없음 | **(v2.1.78)** Plugin-shipped 에이전트의 노력 수준. |

### tools vs disallowedTools

| 방식 | 설명 | 사용 시점 |
|------|------|----------|
| `tools` | 허용 목록 (allowlist) | 소수 도구만 허용 |
| `disallowedTools` | 거부 목록 (denylist) | 대부분 허용, 일부 제외 |

두 필드를 동시에 사용하지 않음.

### permissionMode

| 모드 | 설명 |
|------|------|
| `default` | 각 작업에 사용자 확인 |
| `acceptEdits` | 파일 편집 자동 승인 |
| `dontAsk` | 모든 작업 자동 승인 |
| `bypassPermissions` | 모든 권한 우회 |
| `plan` | 계획 모드에서 실행 |

`dontAsk`, `bypassPermissions`는 신뢰할 수 있는 환경에서만 사용.

### memory (v2.1.33, 신규)

세션 간 지속 메모리. 에이전트가 학습한 패턴, 디버깅 인사이트 등을 축적.

```yaml
memory: project    # 프로젝트 스코프
memory: user       # 사용자 전역 스코프
memory: local      # 로컬 스코프
```

### Monitor Tool (v2.1.98)

`Monitor` 도구 추가: 백그라운드 스크립트의 이벤트를 스트리밍으로 수신. 백그라운드 에이전트/태스크의 진행 상황을 실시간으로 추적하는 데 유용.

### background (v2.1.49, 신규)

```yaml
background: true   # 항상 백그라운드에서 실행
```

### isolation (v2.1.49, 신규)

```yaml
isolation: worktree  # 임시 git worktree에서 격리 실행
```

- 변경사항 없으면 worktree 자동 정리
- 변경사항 있으면 worktree 경로와 브랜치 반환

### Task(agent_type) 스폰 제한 (v2.1.33, 신규)

에이전트가 스폰할 수 있는 서브에이전트를 화이트리스트로 제한:

```yaml
tools: Task(worker, researcher), Read, Write
```

`claude --agent`로 실행되는 에이전트에만 적용.

### `--print` / `--agent` 모드 frontmatter 준수 (v2.1.119)

- `--print` 모드가 이제 에이전트 정의의 `tools:`와 `disallowedTools:` frontmatter를 interactive 모드와 동일하게 준수
- `--agent <name>`으로 built-in agent 실행 시 에이전트 정의의 `permissionMode`를 준수

이전 버전에서는 headless/print 모드에서 이 필드들이 무시되어 예상치 못한 도구 호출이 가능했던 문제가 수정됨.

### MCP 서버 병렬 연결 (v2.1.119)

서브에이전트와 SDK MCP 서버의 reconfiguration이 직렬 → 병렬로 바뀌어 시작 속도 개선. 다수의 MCP 서버를 쓰는 서브에이전트일수록 체감 차이 큼.

---

## 5. Hooks

### 이벤트 유형

| 이벤트 | 매처 | 설명 |
|--------|------|------|
| `PreToolUse` | 도구 이름 | 도구 실행 전 |
| `PostToolUse` | 도구 이름 | 도구 실행 후 |
| `Stop` | 없음 | 에이전트 종료 시 |
| `SubagentStart` | 에이전트 이름 | 서브에이전트 시작 시 (프로젝트 레벨) |
| `SubagentStop` | 에이전트 이름 | 서브에이전트 완료 시 (프로젝트 레벨) |
| `TeammateIdle` | - | **(신규 v2.1.33)** Agent Teams용. exit 2로 작업 계속 강제. |
| `TaskCompleted` | - | **(신규 v2.1.33)** 태스크 완료 시. exit 2로 차단 및 피드백. |
| `WorktreeCreate` | - | **(v2.1.50)** isolation worktree 생성 시. |
| `WorktreeRemove` | - | **(v2.1.50)** isolation worktree 삭제 시. |
| `PermissionDenied` | - | **(v2.1.88)** auto mode 권한 거부 후. `{retry: true}` 반환 가능. |
| `TaskCreated` | - | **(v2.1.84)** `TaskCreate`로 태스크 생성 시. |
| `CwdChanged` | - | **(v2.1.83)** 작업 디렉토리 변경 시 (예: direnv 연동). |
| `FileChanged` | - | **(v2.1.83)** 파일 변경 감지 시. |
| `StopFailure` | - | **(v2.1.78)** API 에러(rate limit, auth 실패 등)로 턴 종료 시. |
| `PostCompact` | - | **(v2.1.76)** 컨텍스트 압축 완료 후. |
| `InstructionsLoaded` | - | **(v2.1.69)** CLAUDE.md / rules 로드 시. |
| `Elicitation` | - | **(v2.1.76)** MCP 서버가 구조화된 입력을 요청할 때. |

### Hook 동작

- exit code `0`: 통과
- exit code `2`: 작업 차단 (stderr 메시지 표시)
- 입력은 stdin으로 JSON 형식 전달
- **(v2.1.69)** `agent_id` (서브에이전트) 및 `agent_type` (서브에이전트 + `--agent`) 필드가 훅 이벤트에 포함
- **(v2.1.85)** `if` 필드: 조건부 실행. permission rule 문법 사용 (예: `Bash(git *)`). **(v2.1.89 수정)** compound commands 및 env-var 접두사 매칭 정상화.
- **(v2.1.88)** PreToolUse/PostToolUse에서 Write/Edit/Read의 `file_path`가 절대 경로로 제공
- **(v2.1.85)** `PreToolUse` 훅이 `AskUserQuestion`에 `updatedInput` + `permissionDecision: "allow"` 반환 가능 (headless 연동)
- **(v2.1.89)** `PreToolUse` 훅에서 `permissionDecision: "defer"` 반환 가능. Headless 세션에서 도구 호출 일시 중지 후 `-p --resume`으로 재개.

### HTTP Hooks (v2.1.63)

셸 커맨드 대신 HTTP POST로 훅 실행 가능:

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: http
          url: "https://example.com/webhook"
```

### MCP Tool Hooks (v2.1.118)

훅이 셸 커맨드/HTTP 대신 MCP 도구를 직접 호출 가능:

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: mcp_tool
          server: my-mcp-server
          tool: validate_command
```

MCP 서버에 정의된 도구로 검증/처리 로직을 위임할 수 있음.

### PostToolUse 실행 시간 측정 (v2.1.119)

`PostToolUse`와 `PostToolUseFailure` 훅 입력에 `duration_ms` 필드가 포함 (permission prompt와 PreToolUse 훅 시간 제외한 순수 도구 실행 시간).

### Stop/SubagentStop 훅 (v2.1.47 추가)

`last_assistant_message` 필드: 에이전트 최종 응답 텍스트를 훅에서 직접 접근 가능 (트랜스크립트 파싱 불필요).

### 예시

```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
  Stop:
    - hooks:
        - type: command
          command: "./scripts/cleanup.sh"
```

---

## 6. 실행 모드

### Foreground (기본)

서브에이전트 완료까지 메인 대화 대기. 결과 즉시 확인.

### Background

```yaml
background: true  # YAML 설정
```

또는:
- Task tool의 `run_in_background: true`
- 실행 중 `Ctrl+B`로 백그라운드 전환

**동작**: ESC로 메인 취소 시 백그라운드는 계속 실행. `Ctrl+F`로 강제 종료.

**(v2.1.76)** 백그라운드 에이전트를 kill하면 부분 결과가 대화 컨텍스트에 보존됨.

### 병렬 실행

여러 서브에이전트를 동시에 실행 가능. Task tool을 한 메시지에서 여러 번 호출.

---

## 7. 모델 선택 가이드

| 모델 | 용도 | 속도 | 비용 |
|------|------|------|------|
| `haiku` | 파일 검색, 간단한 포맷팅 | 매우 빠름 | 저렴 |
| `sonnet` | 대부분의 작업 (기본값) | 빠름 | 보통 |
| `opus` | 복잡한 아키텍처, 정교한 분석 | 느림 | 비쌈 |
| `'inherit'` | 메인 대화 모델 상속 | 가변 | 가변 |

---

## 8. Skills 연동

### 서브에이전트에 Skills 프리로드

```yaml
skills: seo-optimizer, ghost-validator
```

- 지정된 Skills 전체 콘텐츠가 시작 시 주입
- 서브에이전트는 부모 스킬을 **상속받지 않음** (명시적 지정 필수)
- 내장 에이전트 (Explore, Plan, general-purpose)는 Skills 접근 불가

---

## 9. CLI 사용법

### JSON 플래그로 정의

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer",
    "prompt": "You are a senior code reviewer...",
    "tools": ["Read", "Grep", "Glob"],
    "model": "sonnet"
  }
}'
```

### 에이전트 목록 확인 (v2.1.50)

```bash
claude agents  # 인터랙티브 세션 없이 에이전트 목록
```

**(v2.1.98)** `/agents` 커맨드가 탭 레이아웃으로 변경: **Running** 탭(실행 중인 에이전트)과 **Library** 탭(사용 가능한 에이전트)으로 분리.

**(v2.1.97)** `/agents`에 `N running` 인디케이터가 표시되어 현재 실행 중인 서브에이전트 수를 즉시 확인 가능.

### Named Subagents in @ Mention (v2.1.88)

**(v2.1.88)** 커스텀 에이전트가 `@` mention typeahead 자동완성에 표시됨. `@agent-name`으로 직접 참조 가능.

### --bare 플래그 (v2.1.81)

스크립트용 `-p` 호출에서 hooks, LSP, plugin sync, skill walks를 건너뛰는 경량 모드:

```bash
claude --bare -p "prompt"  # ANTHROPIC_API_KEY 또는 apiKeyHelper 필요
```

- OAuth/keychain 인증 비활성화
- Auto-memory 완전 비활성화
- ~14% 빠른 API 요청 (v2.1.83)

### Worktree 모드 실행 (v2.1.49)

```bash
claude --worktree  # 또는 -w
```

### EnterWorktree `path` 파라미터 (v2.1.105)

`EnterWorktree` 도구에 `path` 파라미터 추가. 현재 저장소의 **기존** worktree로 전환할 때 사용. 새로 생성하지 않고 기존 worktree를 재사용.

### Stale Worktree 자동 정리 (v2.1.105)

Squash-merge된 PR의 worktree가 무기한 남아있던 동작이 수정됨. PR이 squash merge되면 해당 에이전트 worktree도 정리 대상으로 포함.

### 특정 에이전트 비활성화

```json
{
  "permissions": {
    "deny": ["Task(Explore)", "Task(my-custom-agent)"]
  }
}
```

---

## 10. 컨텍스트 관리

### Resume (재개)

서브에이전트는 전체 히스토리를 유지하며 재개 가능.

**(v2.1.77 Breaking)**: Agent tool의 `resume` 파라미터 제거됨. 대신 `SendMessage({to: agentId})`로 이전 에이전트를 계속. `SendMessage`는 중지된 에이전트를 백그라운드에서 자동 재개.

### Auto-Compaction

컨텍스트 윈도우 임계치 도달 시 자동 요약. 중요 정보 보존.

### Transcript 저장

```
~/.claude/projects/[project-hash]/sessions/[session-id].jsonl
```

`cleanupPeriodDays` 후 자동 정리 (기본 30일).

---

## 11. 제한사항

1. **중첩 불가**: 서브에이전트는 다른 서브에이전트를 생성할 수 없음 (`claude --agent` 메인 실행 시 `Task(agent_type)`으로 스폰 제한 관리 가능)
2. **Agent tool `model` 파라미터 복원** (v2.1.72): 호출별 모델 오버라이드 가능
3. **스킬 상속 불가**: 부모 대화 스킬을 상속받지 않음. `skills` 필드로 명시 필요.
4. **트랜스크립트 격리**: 각 호출은 새로운 컨텍스트 (재개하지 않는 한)
5. **`TaskOutput` 도구 Deprecated** (v2.1.83): `Read`로 백그라운드 태스크 출력 파일 경로를 직접 읽는 방식으로 대체
6. **WorktreeCreate HTTP hook** (v2.1.84): `type: "http"` 지원. `hookSpecificOutput.worktreePath`로 생성된 worktree 경로 반환
7. **(v2.1.92 수정)** tmux 윈도우가 삭제/재번호화된 후 서브에이전트 스폰이 영구 실패하던 버그 수정 ("Could not determine pane count")
8. **(v2.1.90 수정)** `--resume` 시 deferred tools, MCP 서버, 커스텀 에이전트가 있는 사용자에게 프롬프트 캐시 전체 미스 발생하던 회귀 버그 수정 (v2.1.69 이후)
9. **(v2.1.98 수정)** 서브에이전트가 동적 주입된 MCP 서버의 도구를 상속받지 못하던 버그 수정
10. **(v2.1.98 수정)** 격리된 worktree의 서브에이전트가 자체 worktree에 대한 Read/Edit 접근이 거부되던 버그 수정
11. **(v2.1.101 수정)** `--resume`/`--continue` 시 대형 세션에서 컨텍스트 유실되던 버그 수정
12. **(v2.1.101 수정)** `--resume` 체인 복구 시 관련 없는 서브에이전트 대화로 잘못 연결되던 버그 수정

---

## 12. Best Practice

### DO

- 단일 책임 원칙: 하나의 명확한 역할
- 상세한 프롬프트: 예제와 제약사항 포함
- 최소 권한: `tools` 또는 `disallowedTools`로 제한
- Description에 트리거 키워드 포함 ("use proactively", "when user mentions X")
- Claude와 협업하여 초안 생성 후 반복 개선
- 프로젝트 에이전트는 Git 커밋

### DON'T

- 모호한 description ("Help with code")
- 불필요하게 `opus` 모델 사용
- 모든 도구 허용 (필요 없는 경우)
- 민감한 작업에 `bypassPermissions` 사용

---

## Sources

- [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Agent Teams](https://code.claude.com/docs/en/agent-teams)
- [Claude Code Changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)

## Related

- [[skills-guide]] - Skills 시스템 가이드
- [[claude-md-guide]] - CLAUDE.md 가이드

---

## Update History

- **2026-04-19**: v2.1.110~2.1.114 변경사항 반영
  - **서브에이전트 stall timeout 도입 (v2.1.114)**: 서브에이전트가 mid-stream에서 멈추면 10분 후 명확한 에러로 실패 (기존: 무한 hang)
  - 사용자가 실행 중 서브에이전트를 보면서 입력한 메시지가 트랜스크립트에서 사라지고 부모 AI에게 misattributed 되던 버그 수정 (v2.1.114)
  - Remote Control 세션이 서브에이전트 트랜스크립트를 스트리밍하지 못하던 버그 수정 (v2.1.114)
  - Remote Control 세션이 Claude Code 종료 시 archive 되지 않던 버그 수정 (v2.1.114)
  - `/ultrareview` 클라우드 기반 코드 리뷰 추가 (v2.1.111) — 병렬 multi-agent 분석/비평. `/ultrareview <PR#>`로 GitHub PR 직접 리뷰
  - `CLAUDE_CODE_EXTRA_BODY`의 `output_config.effort`가 effort 미지원 모델/Vertex AI 서브에이전트 호출 시 400 에러 내던 버그 수정 (v2.1.114)
- **2026-04-15**: v2.1.105~2.1.109 변경사항 반영
  - `EnterWorktree`에 `path` 파라미터 추가 - 기존 worktree 전환 (v2.1.105)
  - Squash-merge된 PR의 stale 에이전트 worktree 자동 정리 (v2.1.105)
  - Agent tool auto mode에서 safety classifier transcript 컨텍스트 초과 시 권한 요청 버그 수정 (v2.1.108)
  - `--resume`이 자기 참조 메시지 포함 트랜스크립트 시 세션 잘림 수정 (v2.1.108)
- **2026-04-13**: v2.1.93~2.1.101 변경사항 반영
  - Monitor 도구 추가 (v2.1.98) - 백그라운드 스크립트 이벤트 스트리밍
  - `/agents` 탭 레이아웃으로 변경: Running + Library (v2.1.98)
  - `/agents`에 `N running` 인디케이터 추가 (v2.1.97)
  - 서브에이전트 동적 MCP 도구 상속 수정 (v2.1.98)
  - 격리된 worktree 서브에이전트 Read/Edit 접근 수정 (v2.1.98)
  - `--resume`/`--continue` 대형 세션 컨텍스트 유실 수정 (v2.1.101)
  - `--resume` 체인 복구 시 잘못된 서브에이전트 연결 수정 (v2.1.101)
  - `/team-onboarding` 커맨드 추가 (v2.1.101) - 팀원 온보딩 가이드 생성
- **2026-04-04**: v2.1.90~2.1.92 변경사항 반영
  - tmux 윈도우 kill/재번호화 후 서브에이전트 스폰 실패 수정 (v2.1.92)
  - `--resume` 프롬프트 캐시 미스 회귀 수정 (v2.1.90)
  - prompt-type Stop 훅 소형 모델 `ok:false` 시 오류 수정 (v2.1.92)
  - MCP tool result persistence override `_meta["anthropic/maxResultSizeChars"]` 최대 500K (v2.1.91)
- **2026-04-01**: v2.1.89 변경사항 반영
  - `"defer"` PreToolUse permission decision 추가 (headless 세션 일시중지/재개)
  - hooks `if` 조건 compound commands 및 env-var 접두사 매칭 수정
- **2026-03-31**: v2.1.79~2.1.88 변경사항 반영
  - Named subagents in `@` mention typeahead (v2.1.88)
  - `initialPrompt` frontmatter (v2.1.83)
  - `--bare` 경량 모드 (v2.1.81)
  - Hook 이벤트 4종 추가: PermissionDenied, TaskCreated, CwdChanged, FileChanged
  - 조건부 훅 `if` 필드 (v2.1.85)
  - PreToolUse `AskUserQuestion` 훅 응답 (v2.1.85)
  - `TaskOutput` deprecated, `Read` 사용 (v2.1.83)
  - WorktreeCreate HTTP hook (v2.1.84)
- **2026-03-18**: v2.1.51~2.1.78 변경사항 반영
  - `effort` frontmatter 필드 추가 (v2.1.78, plugin-shipped agents)
  - Agent tool `resume` 파라미터 제거 → `SendMessage` 사용 (v2.1.77 Breaking)
  - Agent tool `model` 파라미터 복원 (v2.1.72)
  - Hook 이벤트 4종 추가: StopFailure, PostCompact, InstructionsLoaded, Elicitation
  - HTTP Hooks 지원 (v2.1.63)
  - `agent_id`, `agent_type` 훅 이벤트 필드 (v2.1.69)
  - 백그라운드 에이전트 kill 시 부분 결과 보존 (v2.1.76)
  - 프로젝트 설정/auto memory가 git worktree 간 공유 (v2.1.63)
- **2026-02-22**: 전면 갱신 (source of truth 목적)
  - 신규 YAML 필드 5개: memory, background, isolation, mcpServers, maxTurns
  - Task(agent_type) 스폰 제한 문법
  - 신규 Hook 이벤트 4개: TeammateIdle, TaskCompleted, WorktreeCreate, WorktreeRemove
  - Stop/SubagentStop last_assistant_message 필드
  - claude agents CLI, --worktree 플래그
  - 빌트인 에이전트 추가 (statusline-setup, Claude Code Guide)
  - 불필요한 예시 축소, 핵심 레퍼런스에 집중
- **2026-01-16**: 초기 작성
