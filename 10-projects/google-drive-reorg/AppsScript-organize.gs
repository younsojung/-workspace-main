/**
 * Google Drive — 페르소나 정리 (2026-05-11)
 * 최근 1년 루트 파일을 페르소나 폴더로 자동 분류·이동.
 *
 * 사용법:
 *   1. https://script.google.com 에서 "새 프로젝트"
 *   2. 이 파일 내용 전체를 붙여넣기 (기본 myFunction 코드 삭제)
 *   3. 처음엔 DRY_RUN = true 인 상태로 ▶ 실행 → 권한 승인 → 로그 확인 (보기 > 실행 기록)
 *   4. 결과 OK면 DRY_RUN = false 로 바꾸고 다시 ▶ 실행 → 실 이동
 *
 * 실행 함수: organizeDrive
 */

// === 설정 ===
const DRY_RUN = true;                        // 처음엔 true (미리보기). 검증 후 false로 바꿔서 실행.
const SINCE = '2025-05-11T00:00:00';         // 이 날짜 이후 수정된 파일만 대상
const ROOT_ID = '0AN3yxw6Kl-6VUk9PVA';       // 내 드라이브 루트

// 페르소나 폴더 ID (folder-ids.md 와 동기화됨)
const FOLDERS = {
  생각마라톤:   '1nuKriuHiKVvcaIF0HqEOmcF_wTN2k1WP',
  앤드엔:       '1PGt7NVKa-EzFLO81lpEMCDoySF-D6Xlg',
  뛰어노는논술: '1uRsgJvH3LayB62u8AJHqg5njq1PgTlzk',
  단행본:       '1OJYevblsEK_rynZ4IVRsmo4OsfOz-ASl',
  채산표:       '1HgS2wrsAYtSqxbAhnfPNBkYPbVk0fn5A',
  러쉬:         '12FwNOcnrrDBg3F3w-kav7xpmy0L5VWwt',
  코치:         '10ghq3GpBKq4B1_ahSE_wmWKRXLpxM9Di',
  뷰클런즈:     '1fneWWEWwVkV5989SV_KFvWTaXoqxlPMn',
  개인:         '1KFfEYBs6nfgsepSDPHnZWR9wKk4A1JsJ',
  inbox:        '1Vj4dNYRKariU0AKR_bsbV103tgfK9eEe',
};

const FOLDER_NAMES = {
  [FOLDERS.생각마라톤]:   '교육기획/생각마라톤',
  [FOLDERS.앤드엔]:       '교육기획/앤드엔클럽',
  [FOLDERS.뛰어노는논술]: '교육기획/뛰어노는논술',
  [FOLDERS.단행본]:       '작가-생각구독/단행본-원고',
  [FOLDERS.채산표]:       '작가-생각구독/채산표',
  [FOLDERS.러쉬]:         '러쉬코리아-CD',
  [FOLDERS.코치]:         '코치-CEO비즈니스',
  [FOLDERS.뷰클런즈]:     '사업체/뷰클런즈',
  [FOLDERS.개인]:         '개인',
  [FOLDERS.inbox]:        '_inbox',
};

// === 분류 룰 (위에서 아래로, 첫 매칭) ===
function classify(title) {
  if (/생각마라톤|생각 마라톤|^DAY7_|^DAY8_|학습자본|깨끗한 학습력/.test(title)) return FOLDERS.생각마라톤;
  if (/앤드엔/.test(title)) return FOLDERS.앤드엔;
  if (/뛰어노는 ?논술|트루스 에듀케이트|트루에듀컬처|Trus educulture/.test(title)) return FOLDERS.뛰어노는논술;
  if (/러쉬|LUSH|무명배우|러쉬씨어터|RETAIL STRATEGY|WORK AFTER PARTY/.test(title)) return FOLDERS.러쉬;
  if (/트루스데이|트루스 전략|26년 트루스|트루스의 비전|트루스 _학습|트루스 그룹|트루스 설날|트루스 스토리|리브랜딩_단가_인터뷰_TRUS|진정한 성과|기업의 체질개선|고객에 대하여/.test(title)) return FOLDERS.코치;
  if (/2033_book|2033_one_pager|2033_presentation|ASTRA BOOK|Astra book|일의[ _]교과서|시스템 1장|직관의 시대|날것의 감각|생각 교과서|5월\. 알고리즘|6월\. 브랜드|7월\. 떠나고|7월\. 잘사는|11월의 생각구독|1월\. 30대|생각구독 Pt|생각구독 라이브|생각구독의 끝점|사람공부|김득신|맹상군|욕망에 대한 스터디|회의록 ?4단계 ?슬라이드|회의록_4단계_슬라이드|소울정|유투브|유학법|라이브 방송|오프닝 영상/.test(title)) return FOLDERS.단행본;
  if (/브레빌|보헤미안/.test(title)) return FOLDERS.뷰클런즈;
  if (/결혼식 사회|축사|절기 체크|추석|펜타포트|생일잔치|명절|^IMG_|송도동|destiny_dates|VIF 신청|영혼의 친구/.test(title)) return FOLDERS.개인;
  if (/\.(mp3|m4a)$|Playlist|𝐏𝐥𝐚𝐲𝐥𝐢𝐬𝐭|Laufey|Mo' Better|Keep Me Warm|Love, Love|Let us walk|You are in low voice|사클 샘플/.test(title)) return FOLDERS.생각마라톤;
  if (/학습자본\.ai|시간을 자유로|숫자를 언어로|나의 자리/.test(title)) return FOLDERS.단행본;
  return FOLDERS.inbox;
}

// === 메인 ===
function organizeDrive() {
  const query = `"${ROOT_ID}" in parents and mimeType != "application/vnd.google-apps.folder" and modifiedTime > "${SINCE}" and trashed = false`;
  const iter = DriveApp.searchFiles(query);

  const counts = {};
  const errors = [];
  let total = 0, moved = 0;

  Logger.log(`=== Drive 페르소나 정리 ${DRY_RUN ? '(DRY-RUN — 실 이동 안 함)' : '(LIVE — 실 이동)'} ===`);
  Logger.log(`Cutoff: ${SINCE}`);
  Logger.log('');

  while (iter.hasNext()) {
    const file = iter.next();
    const title = file.getName();
    const targetId = classify(title);
    const targetName = FOLDER_NAMES[targetId];

    total++;
    counts[targetName] = (counts[targetName] || 0) + 1;

    if (DRY_RUN) {
      Logger.log(`[DRY] ${title}  →  ${targetName}`);
    } else {
      try {
        const targetFolder = DriveApp.getFolderById(targetId);
        file.moveTo(targetFolder);
        moved++;
        Logger.log(`[OK]  ${title}  →  ${targetName}`);
      } catch (e) {
        errors.push({ title: title, error: e.message });
        Logger.log(`[ERR] ${title}: ${e.message}`);
      }
    }
  }

  Logger.log('');
  Logger.log('=== 통계 ===');
  Object.keys(counts).sort().forEach(function (k) {
    Logger.log(`${k}: ${counts[k]}`);
  });
  Logger.log('');
  Logger.log(`총 ${total}개${DRY_RUN ? ' (미리보기 — 실제 이동 안 함)' : ` 중 ${moved}개 이동, ${errors.length}개 실패`}`);
  if (errors.length > 0) {
    Logger.log('');
    Logger.log('=== 실패 목록 (공동 소유 파일은 보통 권한 부족) ===');
    errors.forEach(function (e) { Logger.log(`- ${e.title}: ${e.error}`); });
  }
}
