# Google Drive Reorganization (2026-05-11)

귀염둥이의 My Drive를 페르소나 중심 구조로 재편하는 1회성 프로젝트.

## 현재 상태

- ✅ **1-A** 페르소나 폴더 16개 생성 완료 (이 폴더의 `folder-ids.md` 참조)
- ✅ **1-B** 최근 1년 (2025-05-11 이후) 루트 파일 분류 룰 작성 — `classification-rules.md`
- ⏸️ **1-C** 실제 이동 실행 — `gws auth login` 후 `execute-moves.sh` 실행

## 다음 액션

귀염둥이 액션 1개:
```bash
gws auth login
```

그다음 Claude (또는 직접) 실행:
```bash
bash 10-projects/google-drive-reorg/execute-moves.sh --dry-run    # 미리보기
bash 10-projects/google-drive-reorg/execute-moves.sh              # 실제 이동
```

## 안전장치

- `--dry-run` 모드로 먼저 이동 대상 출력만
- 본 이동 전에 매칭되지 않은 파일은 그대로 루트에 둠 (안전)
- 룰에 매칭 안 되는 모호 파일은 `_inbox`로 모음 (다음 세션에서 수동 분류)
- 공유 링크는 Drive에서 file ID로 작동 → 부모 변경해도 안 깨짐

## 1단계에서 다루지 않는 것

- 2025-05-11 이전 파일 (다음 세션)
- 7개 레거시 폴더 (윤소정의 생각구독, 채산표 관리 등) — _archive 이동은 다음 세션
- "제목 없는 문서" 30+ 휴지통 처리 — 내용 확인 후 일괄 결정 필요
- 음악·디자인 파일(.mp3/.ai) — 작가 페르소나용인지 개인용인지 결정 필요
