"""
개인 채산표 분류 엔진.
- 카카오뱅크 입출금 + 삼성카드 2장 사용내역
- config/personal/*.yaml 룰 적용
- 결과: data/processed/personal_transactions.csv
"""
import pandas as pd
import yaml
import re
from pathlib import Path

BASE = Path(__file__).parent.parent
CONFIG = BASE / "config" / "personal"
DATA_RAW = BASE / "data" / "raw" / "personal"

def load_yaml(p):
    if not p.exists(): return {}
    with open(p, encoding='utf-8') as f:
        d = yaml.safe_load(f)
    return {k: v for k, v in d.items() if k not in ('version','updated')}

TAXONOMY = load_yaml(CONFIG / "taxonomy.yaml")
REVENUE  = load_yaml(CONFIG / "revenue.yaml")
EXCLUSIONS = load_yaml(CONFIG / "exclusions.yaml")

# ============================================================
# 데이터 로드
# ============================================================
def load_bank():
    """카카오뱅크 거래내역. 헤더 행 10."""
    df = pd.read_excel(DATA_RAW / "kakao_bank_2025-12_2026-05.xlsx",
                       sheet_name=0, header=10).dropna(how='all').reset_index(drop=True)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df['거래일시'] = pd.to_datetime(df['거래일시'], errors='coerce')
    df = df.dropna(subset=['거래일시'])
    df['거래금액'] = df['거래금액'].astype(str).str.replace(',','').str.replace(' ','').astype(float)
    df['내용'] = df['내용'].fillna('').astype(str)
    df['거래구분'] = df['거래구분'].fillna('').astype(str)
    df['date'] = df['거래일시']
    df['month'] = df['date'].dt.to_period('M').astype(str)
    return df

def load_cards():
    """삼성카드 2장 합치기."""
    dfs = []
    for f in ['samsung_card_1_2026-01_2026-05.xlsx', 'samsung_card_2_2026-01_2026-05.xlsx']:
        df = pd.read_excel(DATA_RAW / f, sheet_name=0)
        df['카드구분'] = f.split('_')[2]
        dfs.append(df)
    card = pd.concat(dfs, ignore_index=True)
    card['승인일자'] = pd.to_datetime(card['승인일자'], format='%Y.%m.%d', errors='coerce')
    card = card.dropna(subset=['승인일자'])
    card['date'] = card['승인일자']
    card['month'] = card['date'].dt.to_period('M').astype(str)
    card['승인금액(원)'] = card['승인금액(원)'].astype(int)
    card['가맹점명'] = card['가맹점명'].fillna('').astype(str).str.strip()
    return card

# ============================================================
# 룰 매칭
# ============================================================
def match_rule(rule, tx):
    """tx dict: {source, content, jeok, amount, merchant, ujong, geo_gu}"""
    src = rule.get('source')
    if src and src != tx['source']:
        return False

    kws = rule.get('content_contains')
    if kws is not None:
        if not any(k in tx['content'] for k in kws): return False

    nk = rule.get('content_not_contains')
    if nk is not None:
        if any(k in tx['content'] for k in nk): return False

    ex = rule.get('content_exact')
    if ex is not None:
        if tx['content'] not in ex: return False

    mc = rule.get('merchant_contains')
    if mc is not None:
        if not any(k in tx['merchant'] for k in mc): return False

    je = rule.get('거래구분_exact')
    if je is not None:
        if tx['jeok'] not in je: return False

    amin = rule.get('min_amount')
    if amin is not None and tx['amount'] < amin: return False

    return True

def classify_one(tx):
    """우선순위: 영업외(명시) → 매출 → 지출 → 영업외(정규식 fallback) → 소액 fallback"""
    # 1. 영업외 — NONOP-PERSONAL-TRANSFER는 마지막에 (정규식 광범위 매칭 방지)
    for item_id, spec in EXCLUSIONS.items():
        if item_id == 'NONOP-PERSONAL-TRANSFER':
            continue
        for rule in spec.get('rules', []):
            if match_rule(rule, tx):
                return item_id, spec['category'], spec['name']

    # 2. 매출 / 매출차감
    fallback_rev = None
    for item_id, spec in REVENUE.items():
        if spec.get('fallback'):
            fallback_rev = (item_id, spec['category'], spec['name'])
            continue
        for rule in spec.get('rules', []):
            if match_rule(rule, tx):
                return item_id, spec['category'], spec['name']
    if tx['source'] == 'bank_in' and fallback_rev:
        return fallback_rev

    # 3. 지출 (taxonomy) — 카드, 통장출금
    if tx['source'] in ('bank_out', 'card'):
        for item_id, spec in TAXONOMY.items():
            for rule in spec.get('rules', []):
                if match_rule(rule, tx):
                    return item_id, spec['category'], spec['name']

    # 4. 영업외 NONOP-PERSONAL-TRANSFER (정규식 매칭) — 지출 분류 다 실패한 후
    if 'NONOP-PERSONAL-TRANSFER' in EXCLUSIONS:
        spec = EXCLUSIONS['NONOP-PERSONAL-TRANSFER']
        for rule in spec.get('rules', []):
            if match_rule(rule, tx):
                return 'NONOP-PERSONAL-TRANSFER', spec['category'], spec['name']

    # 5. fallback: 소액 50만 미만 → OPEX-MISC
    if tx['source'] in ('bank_out', 'card') and tx['amount'] < 500000:
        return 'OPEX-MISC', '운영비', '운영비 기타 (자동 fallback)'

    return 'UNCLASSIFIED', '미분류', '미분류'

# ============================================================
# 분류 실행
# ============================================================
def main():
    bank = load_bank()
    card = load_cards()

    records = []

    # 통장 입금
    for _, r in bank[bank['거래금액'] > 0].iterrows():
        tx = {'source':'bank_in', 'content':r['내용'], 'jeok':r['거래구분'],
              'amount':int(r['거래금액']), 'merchant':'', 'ujong':''}
        item_id, cat, name = classify_one(tx)
        records.append({'date':r['date'], 'month':r['month'],
                       'source':'bank_in', 'amount':int(r['거래금액']),
                       'content':r['내용'], 'jeok':r['거래구분'], 'merchant':'', 'ujong':'',
                       'item_id':item_id, 'category':cat, 'item_name':name})

    # 통장 출금
    for _, r in bank[bank['거래금액'] < 0].iterrows():
        amt = int(abs(r['거래금액']))
        tx = {'source':'bank_out', 'content':r['내용'], 'jeok':r['거래구분'],
              'amount':amt, 'merchant':'', 'ujong':''}
        item_id, cat, name = classify_one(tx)
        records.append({'date':r['date'], 'month':r['month'],
                       'source':'bank_out', 'amount':amt,
                       'content':r['내용'], 'jeok':r['거래구분'], 'merchant':'', 'ujong':'',
                       'item_id':item_id, 'category':cat, 'item_name':name})

    # 카드
    for _, r in card.iterrows():
        if r['취소여부'] != '-':
            item_id, cat, name = 'CARD-CANCEL', '취소', '카드 취소'
        else:
            tx = {'source':'card', 'content':'', 'jeok':'',
                  'amount':int(r['승인금액(원)']),
                  'merchant':r['가맹점명'], 'ujong':''}
            item_id, cat, name = classify_one(tx)
        records.append({'date':r['date'], 'month':r['month'],
                       'source':'card', 'amount':int(r['승인금액(원)']),
                       'content':'', 'jeok':'',
                       'merchant':r['가맹점명'], 'ujong':'',
                       'item_id':item_id, 'category':cat, 'item_name':name})

    df = pd.DataFrame(records)
    out = BASE / "data" / "processed" / "personal_transactions.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding='utf-8-sig')
    print(f"✅ 저장: {out} ({len(df)}건)")

    # 잔액 추출
    bank_sorted = bank.sort_values('date')
    last_balance = bank_sorted.iloc[-1]
    print(f"\n현재 잔액 (카카오뱅크 {last_balance['date'].strftime('%Y-%m-%d %H:%M')}):")
    bal = int(str(last_balance['거래 후 잔액']).replace(',','').strip())
    print(f"  ₩ {bal:,}")

    # 분류 요약
    print("\n=== 분류 결과 ===")
    summary = df.groupby(['category','item_id','item_name']).agg(
        건수=('amount','count'), 합계=('amount','sum')
    ).sort_values(['category','합계'], ascending=[True, False])
    print(summary.to_string())

    # 미분류
    unc = df[df['item_id']=='UNCLASSIFIED']
    if len(unc) > 0:
        print(f"\n⚠️  미분류 {len(unc)}건 ({unc['amount'].sum():,}원)")
        print(unc[['date','source','content','merchant','amount']].to_string(index=False))

if __name__ == '__main__':
    main()
