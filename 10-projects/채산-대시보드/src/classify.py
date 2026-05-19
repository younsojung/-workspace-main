"""
분류 엔진 — YAML 룰 기반.

사용법:
    from classify import Classifier
    clf = Classifier(config_dir="config/")
    transactions = clf.classify(bank_csv_path, card_xls_path)
    # transactions는 통합된 거래 단위 DataFrame, 각 행에 'item_id', 'category' 컬럼 부여

룰 매칭 우선순위:
    1. exclusions.yaml (영업외) — 가장 먼저 (가장 명확한 패턴)
    2. revenue.yaml (매출) — 통장 입금
    3. taxonomy.yaml (지출 항목) — 위에서 아래로 순서대로
    4. 어디에도 매칭 안 됨 → 'UNCLASSIFIED'
"""

import pandas as pd
import yaml
import re
from pathlib import Path


class Classifier:
    def __init__(self, config_dir):
        self.config_dir = Path(config_dir)
        self.taxonomy = self._load(self.config_dir / "taxonomy.yaml")
        self.revenue = self._load(self.config_dir / "revenue.yaml")
        self.exclusions = self._load(self.config_dir / "exclusions.yaml")

    @staticmethod
    def _load(p):
        if not p.exists():
            raise FileNotFoundError(f"YAML 파일 없음: {p}")
        with open(p, encoding='utf-8') as f:
            d = yaml.safe_load(f)
        # version/updated 메타는 제외
        return {k: v for k, v in d.items() if k not in ('version','updated')}

    # ----------------------------------------
    # 데이터 로드
    # ----------------------------------------
    def load_bank(self, csv_path):
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        df['date'] = pd.to_datetime(df['거래일시'].astype(str).str[:8], format='%Y%m%d', errors='coerce')
        df['내용'] = df['내용'].fillna('').astype(str)
        df['적요'] = df['적요'].astype(str)
        df['입금액'] = pd.to_numeric(df['입금액'], errors='coerce').fillna(0)
        df['출금액'] = pd.to_numeric(df['출금액'], errors='coerce').fillna(0)
        df['month'] = df['date'].dt.to_period('M').astype(str)
        return df

    def load_card(self, xls_path):
        df = pd.read_excel(xls_path, engine='xlrd')
        df['date'] = pd.to_datetime(df['이용일'], format='%Y.%m.%d', errors='coerce')
        df['가맹점명'] = df['가맹점명'].fillna('').astype(str)
        df['가맹점업종명'] = df['가맹점업종명'].fillna('').astype(str)
        df['이용금액'] = pd.to_numeric(df['이용금액'], errors='coerce').fillna(0)
        df['month'] = df['date'].dt.to_period('M').astype(str)
        return df

    # ----------------------------------------
    # 룰 매칭 로직
    # ----------------------------------------
    @staticmethod
    def _match_rule(rule, tx):
        """tx는 dict: {source, content, jeok, amount, merchant, ujong}"""
        src = rule.get('source')
        if src != tx['source']:
            return False

        # content_contains: 키워드 중 하나라도 포함
        kws = rule.get('content_contains')
        if kws is not None:
            if not any(k in tx['content'] for k in kws):
                return False

        # content_contains_any: 같음
        kws2 = rule.get('content_contains_any')
        if kws2 is not None:
            if not any(k in tx['content'] for k in kws2):
                return False

        # content_exact
        ex = rule.get('content_exact')
        if ex is not None:
            if tx['content'] not in ex:
                return False

        # content_not_contains: 하나라도 포함되면 매칭 실패
        nk = rule.get('content_not_contains')
        if nk is not None:
            if any(k in tx['content'] for k in nk):
                return False

        # content_regex
        rg = rule.get('content_regex')
        if rg is not None:
            if not re.search(rg, tx['content']):
                return False

        # jeok_exact (통장 적요)
        je = rule.get('jeok_exact')
        if je is not None:
            if tx['jeok'] not in je:
                return False

        # merchant_contains (카드 가맹점명)
        mc = rule.get('merchant_contains')
        if mc is not None:
            if not any(k in tx['merchant'] for k in mc):
                return False

        # merchant_exact
        me = rule.get('merchant_exact')
        if me is not None:
            if tx['merchant'] not in me:
                return False

        # ujong_contains
        uc = rule.get('ujong_contains')
        if uc is not None:
            if not any(k in tx['ujong'] for k in uc):
                return False

        # 금액
        mn = rule.get('min_amount')
        if mn is not None and tx['amount'] < mn:
            return False
        mx = rule.get('max_amount')
        if mx is not None and tx['amount'] > mx:
            return False
        ar = rule.get('amount_range')
        if ar is not None:
            if not (ar[0] <= tx['amount'] < ar[1]):
                return False
        ai = rule.get('amount_in')
        if ai is not None:
            if tx['amount'] not in ai:
                return False
        amin = rule.get('amount_min')
        if amin is not None and tx['amount'] < amin:
            return False

        return True

    def _classify_one(self, tx):
        """우선순위: 영업외 → 매출(차감 외) → 지출 → 매출차감 → fallback"""
        # 1. 영업외 (exclusions) 먼저
        for item_id, spec in self.exclusions.items():
            for rule in spec.get('rules', []):
                if self._match_rule(rule, tx):
                    return item_id, spec['category'], spec['name']

        # 2. 매출 (매출차감 제외) — 입금만 대상
        fallback_item = None
        if tx['source'] == 'bank_in':
            for item_id, spec in self.revenue.items():
                if spec.get('category') == '매출차감':
                    continue   # 환불은 지출 분류 후에
                if spec.get('fallback'):
                    fallback_item = (item_id, spec['category'], spec['name'])
                    continue
                for rule in spec.get('rules', []):
                    if self._match_rule(rule, tx):
                        return item_id, spec['category'], spec['name']
            if fallback_item:
                return fallback_item

        # 3. 지출 (taxonomy) — 출금/카드 명시적 매칭
        if tx['source'] in ('bank_out', 'card'):
            for item_id, spec in self.taxonomy.items():
                for rule in spec.get('rules', []):
                    if self._match_rule(rule, tx):
                        return item_id, spec['category'], spec['name']

        # 4. 매출차감 (환불) — 지출 명시 매칭이 다 실패한 후
        #    출금인데 명시적 지출 카테고리에 없는 한글 이름 송금만 잡힘
        if tx['source'] == 'bank_out':
            for item_id, spec in self.revenue.items():
                if spec.get('category') != '매출차감':
                    continue
                for rule in spec.get('rules', []):
                    if self._match_rule(rule, tx):
                        return item_id, spec['category'], spec['name']

        # 5. fallback: 소액 운영비 자동
        SMALL_AMOUNT_THRESHOLD = 500000
        if tx['source'] in ('bank_out', 'card') and tx['amount'] < SMALL_AMOUNT_THRESHOLD:
            return 'OPEX-MISC-AUTO', '운영비', '운영비 기타 (자동 fallback, 50만 미만)'

        return 'UNCLASSIFIED', '미분류', '미분류'

    # ----------------------------------------
    # 통합 분류
    # ----------------------------------------
    def classify(self, bank_csv, card_xls):
        bank = self.load_bank(bank_csv)
        card = self.load_card(card_xls)

        records = []

        # 통장 입금
        for _, r in bank[bank['입금액'] > 0].iterrows():
            tx = {
                'source': 'bank_in',
                'content': r['내용'],
                'jeok': r['적요'],
                'amount': int(r['입금액']),
                'merchant': '',
                'ujong': '',
            }
            item_id, cat, name = self._classify_one(tx)
            records.append({
                'date': r['date'], 'month': r['month'],
                'source': 'bank_in', 'amount': int(r['입금액']),
                'content': r['내용'], 'jeok': r['적요'],
                'merchant': '', 'ujong': '',
                'item_id': item_id, 'category': cat, 'item_name': name,
            })

        # 통장 출금
        for _, r in bank[bank['출금액'] > 0].iterrows():
            tx = {
                'source': 'bank_out',
                'content': r['내용'],
                'jeok': r['적요'],
                'amount': int(r['출금액']),
                'merchant': '',
                'ujong': '',
            }
            item_id, cat, name = self._classify_one(tx)
            records.append({
                'date': r['date'], 'month': r['month'],
                'source': 'bank_out', 'amount': int(r['출금액']),
                'content': r['내용'], 'jeok': r['적요'],
                'merchant': '', 'ujong': '',
                'item_id': item_id, 'category': cat, 'item_name': name,
            })

        # 카드
        for _, r in card.iterrows():
            if r['전표구분'] == '취소':
                item_id, cat, name = 'CARD-CANCEL', '취소', '카드 취소'
            else:
                tx = {
                    'source': 'card',
                    'content': '',
                    'jeok': '',
                    'amount': int(r['이용금액']),
                    'merchant': r['가맹점명'],
                    'ujong': r['가맹점업종명'],
                }
                item_id, cat, name = self._classify_one(tx)
            records.append({
                'date': r['date'], 'month': r['month'],
                'source': 'card', 'amount': int(r['이용금액']),
                'content': '', 'jeok': '',
                'merchant': r['가맹점명'], 'ujong': r['가맹점업종명'],
                'item_id': item_id, 'category': cat, 'item_name': name,
            })

        return pd.DataFrame(records)


if __name__ == '__main__':
    import sys
    BASE = Path(__file__).parent.parent
    clf = Classifier(BASE / "config")

    # 기본 경로 (Downloads 폴더)
    bank_csv = sys.argv[1] if len(sys.argv) > 1 else "/Users/sojungyoun/Downloads/통장입출금내역 (1).csv"
    card_xls = sys.argv[2] if len(sys.argv) > 2 else "/Users/sojungyoun/Downloads/카드지출총합1.xls"

    print(f"분류 중...")
    tx = clf.classify(bank_csv, card_xls)

    out = BASE / "data" / "processed" / "transactions.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    tx.to_csv(out, index=False, encoding='utf-8-sig')
    print(f"✅ 저장: {out}")

    # 분류 결과 요약
    print("\n=== 분류별 합계 ===")
    summary = tx.groupby(['category','item_id','item_name']).agg(
        건수=('amount','count'),
        합계=('amount','sum')
    ).sort_values(['category','합계'], ascending=[True, False])
    print(summary.to_string())

    # 미분류 확인
    unc = tx[tx['item_id']=='UNCLASSIFIED']
    if len(unc) > 0:
        print(f"\n⚠️  미분류 {len(unc)}건 ({unc['amount'].sum():,.0f}원)")
        out_unc = BASE / "data" / "unclassified.csv"
        unc.to_csv(out_unc, index=False, encoding='utf-8-sig')
        print(f"   저장: {out_unc}")
        # 통장 미분류
        print("\n  ※ 통장 미분류 TOP 10:")
        unc_bank = unc[unc['source'].str.startswith('bank')]
        if len(unc_bank):
            print(unc_bank.groupby('content').agg(건수=('amount','count'), 합계=('amount','sum')).sort_values('합계', ascending=False).head(10).to_string())
        print("\n  ※ 카드 미분류 TOP 10:")
        unc_card = unc[unc['source']=='card']
        if len(unc_card):
            print(unc_card.groupby(['ujong','merchant']).agg(건수=('amount','count'), 합계=('amount','sum')).sort_values('합계', ascending=False).head(10).to_string())
    else:
        print("\n✅ 미분류 0건")
