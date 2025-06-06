# -*- coding: utf-8 -*-
# ============================================
# AI経営診断GPT【Lite版 v1.9.1 β版】 完全版（コピペOK・GitHub品質）
# バージョン: 2025-07-15_v1.9.1（β版・Googleスプレッド保存無効版）
# ============================================

# --- 1️⃣ インポート ---
import streamlit as st
import os
import io
import re
import pandas as pd
from openai import OpenAI
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, ListFlowable, ListItem
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- 2️⃣ アプリ初期設定（必ず先頭に配置！） ---
APP_TITLE = "AI経営診断GPT【Lite版 v1.9.1 β版】"
st.set_page_config(page_title=APP_TITLE, layout="wide")

# --- 2️⃣a デバッグモード設定 ---
# 本番モードにするには False に変更してください
debug = False

# --- 3️⃣ CSSスタイル（ChatGPT/Notion風・黒白高級感・中央寄せなど） ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
<style>
/* 全体フォント・背景・文字色 */
body, .stApp {
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
    background: #ffffff;
    color: #000000;
}
/* タイトル中央寄せ */
.page-title {
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
}
/* 同意チェックボックス中央寄せ */
.consent-box {
    display: flex;
    justify-content: center;
    margin-bottom: 1.5rem;
}
/* ワイドカード（各フェーズのコンテナ） */
.widecard {
    background: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 24px 20px;
    margin: 24px auto;
    max-width: 1100px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
/* セクションカード（フォーム内・エグゼクティブサマリーBOXなど） */
.section-card {
    background: #fafafa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 16px 12px;
    margin-bottom: 16px;
}
/* 情報ボックス（注意書き） */
.info-box {
    background: #f0f0f0;
    border-left: 4px solid #4b4b4b;
    padding: 12px 14px;
    font-size: 1.02em;
    border-radius: 6px;
    margin-bottom: 12px;
    color: #333333;
}
/* エラー表示 */
.err-box {
    background: #ffe8e8;
    border-left: 4px solid #d32f2f;
    color: #d32f2f;
    padding: 12px 14px;
    font-size: 1.02em;
    border-radius: 6px;
    margin-bottom: 12px;
}
/* フォーム入力バリデーション */
input:invalid, textarea:invalid,
.stTextInput > div > input:invalid,
.stTextArea textarea:invalid {
    border: 1px solid #cccccc !important;
    box-shadow: none !important;
    background: #ffffff !important;
    color: #000000 !important;
}
input:focus:invalid, textarea:focus:invalid,
.stTextInput > div > input:focus:invalid,
.stTextArea textarea:focus:invalid {
    border: 1px solid #888888 !important;
    box-shadow: none !important;
    background: #ffffff !important;
    color: #000000 !important;
}
/* サイドバー */
.stSidebar {
    background: #ffffff !important;
    border-right: 1px solid #e0e0e0;
}
/* ボタン（最新Streamlit対応版） */
[data-testid="baseButton-secondary"], 
[data-testid="baseButton-primary"] {
    font-size: 1.1em !important;
    font-family: 'Inter', 'Noto Sans JP', sans-serif !important;
    padding: 0.75em 2em !important;
    border-radius: 8px !important;
    background: #000000 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
    transition: all 0.1s ease-in-out !important;
}
[data-testid="baseButton-secondary"]:hover, 
[data-testid="baseButton-primary"]:hover {
    background: #333333 !important;
    transform: translateY(-1px);
}
.stButton > button:hover {
    background: #333333 !important;
    transform: translateY(-1px);
}
/* ラベル */
label, .stTextInput label, .stSelectbox label {
    font-size: 1.03em;
    font-weight: 600;
    color: #222222;
    margin-bottom: 4px;
}
.stCheckbox > label {
    font-size: 1.02em;
    color: #222222;
}
/* ボタンバー */
.button-bar {
    display: flex;
    justify-content: center;
    gap: 16px;
    margin: 16px 0;
}
/* 戻るボタン中央寄せ */
.center-button {
    text-align: center;
    margin: 12px 0;
}
/* --- チェックボックスをネイティブ風に整える --- */
[data-testid="stCheckbox"] {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 6px 0;
    margin-bottom: 16px;
    font-size: 1.05em;
    font-weight: 600;
    color: #222222;
}
[data-testid="stCheckbox"] input[type="checkbox"] {
    transform: scale(1.4);
    accent-color: #000000;
    cursor: pointer;
}
[data-testid="stCheckbox"] > div {
    display: flex;
    align-items: center;
}
/* ダークモード対応 */
[data-testid="stAppViewContainer"][class*="dark"] .widecard {
    background: #1e1e1e;
    border: 1px solid #444444;
}
[data-testid="stAppViewContainer"][class*="dark"] .section-card {
    background: #252525;
    border: 1px solid #444444;
}
[data-testid="stAppViewContainer"][class*="dark"] .info-box {
    background: #2b2b2b;
    color: #eeeeee;
    border-left: 4px solid #bbbbbb;
}
[data-testid="stAppViewContainer"][class*="dark"] .err-box {
    background: #3b1f1f;
    border-left: 4px solid #ff5555;
    color: #ffcccc;
}
</style>
""", unsafe_allow_html=True)

# --- 4️⃣ OpenAI API 設定 ---
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
client = OpenAI(api_key=api_key) if api_key else None

# --- 6️⃣ バリデーション関数 ---
def is_valid_non_negative(val: str, allow_empty: bool = True) -> bool:
    """
    非負整数のみ許容。空文字列は allow_empty が True なら True。
    """
    if val == "" and allow_empty:
        return True
    try:
        return int(val) >= 0
    except:
        return False

def is_integer(val: str, allow_empty: bool = True) -> bool:
    """
    整数（負数含む）を許容。空文字列は allow_empty が True を True。
    """
    if val == "" and allow_empty:
        return True
    try:
        int(val)
        return True
    except:
        return False

# --- 7️⃣ ポリシー同意チェック（ステップ0化＋次へボタン） ---
def show_policy_step() -> None:
    """
    ステップ0：利用規約・ポリシー同意画面を表示し、
    同意したらステップ1に進むボタンを提示する。
    """
    st.markdown(f'<div class="page-title">{APP_TITLE}</div>', unsafe_allow_html=True)

    policy_html = """
    <div style="
        background: #f9f9f9;
        border: 1px solid #cccccc;
        border-radius: 8px;
        padding: 12px 14px;
        height: 300px;
        overflow-y: scroll;
        font-size: 0.95rem;
        line-height: 1.5;
        color: #333333;
        margin-bottom: 12px;
    ">
    <b>【個人情報の取扱い・プライバシーポリシー】</b><br>
    ・ご入力いただいた内容は、本サービスの動作にのみ一時的に利用され、サーバー等に保存されません。<br>
    ・AIの学習用途（OpenAI等の品質向上・二次利用）には使用されません。<br>
    ・PDFファイルはお客様ご自身の端末にてダウンロード・管理していただきます。<br>
    ・第三者への提供は行いません。<br>
    ・利用に伴う入力データは、PDF生成後に当サービス上からは自動的に消去されます。<br>
    <br>
    <b>【利用規約・免責事項】</b><br>
    ・AI出力内容の正確性・完全性は保証できません。利用者ご自身の判断と責任にてご活用ください。<br>
    ・本サービスは医療・法務・財務の専門アドバイスを代替するものではありません。<br>
    ・本サービスの利用により発生した直接・間接的な損害について、提供者は責任を負いません。<br>
    ・予告なくサービス内容が変更・中断・終了する場合があります。<br>
    <br>
    <b>【その他】</b><br>
    ・サービス改善のため、匿名のアクセス状況（利用回数・エラー発生状況等）を統計的に取得する場合があります。<br>
    ・利用規約・ポリシーは随時改定される場合があります。改定後の内容は本画面にて掲示します。<br>
    <br>
    【最終更新日】2025年6月05日<br>
    </div>
    """
    st.markdown(policy_html, unsafe_allow_html=True)

    # --- チェックボックス ---
    st.markdown('<div class="consent-box">', unsafe_allow_html=True)
    consent = st.checkbox("上記の内容に同意します", key="consent", label_visibility="visible")
    st.markdown('</div>', unsafe_allow_html=True)

    if consent:
        if st.button("内容を確認して診断をはじめる", key="btn_policy_next"):
            st.session_state.step = 1
            st.rerun()

        # 補足コメントを常に表示（ボタンの下）
        st.markdown(
            '<div style="margin-top: 8px; font-size: 0.9rem; color: #555555;">'
            '※ このあと、入力フォームが表示されます。'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="err-box">⚠ ご利用には同意が必要です。</div>',
            unsafe_allow_html=True
        )

# --- 8️⃣ プラン選択UI ---
def select_plan() -> str:
    with st.sidebar:
        st.header("プラン選択")
        st.markdown("""
| プラン名            | サービス内容                                     | 月額（税込）  |
|------------------|-----------------------------------------------|--------------|
| Lite（経営診断医）      | AI現場診断・PDF出力                              | 無料          |
| Starter（右腕）       | 決算3期比較＋API連携・月次ベンチマーク             | 準備中       |
| Pro（参謀）           | 決算3期比較・KPI設計・実行支援・個別相談           | 準備中       |
""")
        plan = st.radio(
            "ご希望のサービスプランをお選びください",
            [
                "Lite（AI経営診断GPT・無料）",
                "Starter（右腕・API連携）準備中",
                "Pro（参謀・戦略実行支援）準備中",
            ],
            key="field_plan"
        )
        return plan

# --- 9️⃣ フォントチェック ---
def check_font() -> str:
    font_path = "ipag.ttf"
    if not os.path.exists(font_path):
        st.warning("""
PDF日本語出力には 'ipag.ttf' フォントが必要です。
以下のリンクからダウンロードして、この Streamlit アプリと同じフォルダに配置してください。
https://ipafont.ipa.go.jp/node26#jp
""")
    return font_path

# --- 🔟 財務指標計算 ---
def calc_finance_metrics(inp: dict) -> dict:
    def _to_i(v: str) -> int:
        try:
            return int(v)
        except:
            return 0

    sales    = _to_i(inp.get("年間売上高", "0"))
    profit   = _to_i(inp.get("営業利益／所得金額", "0"))
    cash     = _to_i(inp.get("現金・預金残高", "0"))
    loan     = _to_i(inp.get("借入金合計", "0"))
    repay    = _to_i(inp.get("毎月返済額", "0")) * 12

    # 営業CF は簡易的に営業利益と同義とする
    op_cf    = max(profit, 0)

    # 新指標：営業利益率（個人の場合は所得利益率として扱う）
    profit_margin = (profit / sales * 100) if sales else None
    # 新指標：キャッシュ残高／月商（何ヶ月分か）
    cash_months = (cash / (sales / 12)) if sales else None
    # 新指標：借入金返済負担感（年間返済額／営業利益割合）
    burden_ratio = ((repay / profit) * 100) if profit else None

    return {
        "sales": sales,
        "profit": profit,
        "cash": cash,
        "loan": loan,
        "repay": repay,
        "op_cf": op_cf,
        "profit_margin": profit_margin,
        "cash_months": cash_months,
        "burden_ratio": burden_ratio,
    }

# --- 1️⃣1️⃣ EXEC SUMMARY 表示（白黒ボックス内に・改良指標版） ---
def render_exec_summary(inp: dict, fin: dict) -> None:
    """
    エグゼクティブサマリーを「左：箇条書き」「右：ボックス形式で数値」表示する関数。
    新指標（営業利益率・キャッシュ残高/月商・返済負担感）を含める。
    「営業利益／所得金額」は法人／個人で動的切替。
    """
    entity_type = inp.get("法人／個人区分", "")
    profit_label = "営業利益" if entity_type == "法人" else "所得金額"

    sales_str         = f"{fin['sales']:,} 円" if fin.get("sales") is not None else "未入力"
    profit_str        = f"{fin['profit']:,} 円" if fin.get("profit") is not None else "未入力"
    op_cf_str         = f"{fin['op_cf']:,} 円" if fin.get("op_cf") is not None else "未入力"
    profit_margin_str = f"{fin['profit_margin']:.1f}%" if fin.get("profit_margin") is not None else "未入力"
    cash_months_str   = f"{fin['cash_months']:.1f} ヶ月分" if fin.get("cash_months") is not None else "未入力"
    burden_ratio_str  = f"{fin['burden_ratio']:.1f}%" if fin.get("burden_ratio") is not None else "未入力"

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("###  エグゼクティブサマリー")

    # 小見出し追加
    col_info, col_boxes = st.columns([2, 3], gap="medium")

    with col_info:
        st.markdown("#### 基本情報")
        bullets_basic = [
            f"法人／個人区分: {entity_type or '未入力'}",
            f"業種: {inp.get('業種', '未入力')}",
            f"地域: {inp.get('地域', '未入力')}"
        ]
        for b in bullets_basic:
            st.markdown(f"- {b}")

        st.markdown("#### 財務状況")
        bullets_fin = [
            f"年間売上高: {sales_str}",
            f"{profit_label}: {profit_str} ({profit_label}率: {profit_margin_str})",
            f"営業CF (簡易): {op_cf_str}",
            f"キャッシュ残高/月商: {cash_months_str}",
            f"借入金合計: {fin['loan']:,} 円 (年間返済: {fin['repay']:,} 円, 返済負担感: {burden_ratio_str})"
        ]
        for b in bullets_fin:
            st.markdown(f"- {b}")

        st.markdown("#### 顧客・競合・課題")
        bullets_cc = [
            f"主力商品・サービス: {inp.get('主力商品・サービス', '未入力')}",
            f"売上トレンド: {inp.get('売上高の増減', '未入力')}",
            f"{profit_label}トレンド: {inp.get('営業利益の増減／所得金額の増減', '未入力')}",
            f"主要顧客数トレンド: {inp.get('主要顧客数の増減', '未入力')}",
            f"競合環境: {inp.get('競合の多さ', '未入力')}",
            f"資金繰り: {inp.get('資金繰りの状態', '未入力')}",
            f"強みキーワード: {inp.get('自社の強み', '未入力')}",
            f"課題キーワード: {inp.get('経営課題選択', '未入力')}"
        ]
        for b in bullets_cc:
            st.markdown(f"- {b}")

    with col_boxes:
        # 数値ボックスはそのまま維持（見やすさ優先）
        html = f"""
<div style="display: flex; flex-wrap: wrap; gap: 12px;">
  <div style="
      flex: 1 1 45%;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 12px;
      text-align: center;
  ">
    <div style="font-size: 0.95rem; color: #555555; margin-bottom: 4px;">年間売上高</div>
    <div style="font-size: 1.3rem; font-weight: 700; color: #111111;">
      {sales_str}
    </div>
  </div>

  <div style="
      flex: 1 1 45%;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 12px;
      text-align: center;
  ">
    <div style="font-size: 0.95rem; color: #555555; margin-bottom: 4px;">{profit_label}</div>
    <div style="font-size: 1.3rem; font-weight: 700; color: #111111;">
      {profit_str}
    </div>
  </div>

  <div style="
      flex: 1 1 45%;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 12px;
      text-align: center;
  ">
    <div style="font-size: 0.95rem; color: #555555; margin-bottom: 4px;">{profit_label}率</div>
    <div style="font-size: 1.3rem; font-weight: 700; color: #111111;">
      {profit_margin_str}
    </div>
  </div>

  <div style="
      flex: 1 1 45%;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 12px;
      text-align: center;
  ">
    <div style="font-size: 0.95rem; color: #555555; margin-bottom: 4px;">キャッシュ残高/月商</div>
    <div style="font-size: 1.3rem; font-weight: 700; color: #111111;">
      {cash_months_str}
    </div>
  </div>

  <div style="
      flex: 1 1 45%;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 12px;
      text-align: center;
  ">
    <div style="font-size: 0.95rem; color: #555555; margin-bottom: 4px;">返済負担感</div>
    <div style="font-size: 1.3rem; font-weight: 700; color: #111111;">
      {burden_ratio_str}
    </div>
  </div>
</div>
"""
        st.markdown(html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- 1️⃣2️⃣ 用語辞典表示 ---
def render_glossary() -> None:
    with st.expander("📖 用語ミニ辞典"):
        st.markdown("""
* **営業利益率／所得利益率** – 売上高に対する営業利益／所得金額の割合。利益性の目安。  
* **キャッシュ残高/月商** – キャッシュが営業を何ヶ月維持できるかの目安。3ヶ月以上が無理ない水準。  
* **返済負担感** – 年間返済額が営業利益／所得金額の何％か。50％以下が無理ない水準。  
* **5フォース分析（Five Forces Analysis）** – 競争者・新規参入者・代替品・供給者・顧客の5つの力から業界構造を分析する手法。  
* **VRIO分析** – 強み(Valuable)、希少性(Rare)、模倣困難性(Inimitable)、組織活用力(Organization)の4観点で戦略案を比較し、最も競争優位につながる案を選定する手法。  
* **PL/BS/CF** – 損益計算書 / 貸借対照表 / キャッシュフロー計算書。  
""")

# --- 1️⃣3️⃣ 外部環境（PEST＋5フォース＋市場ニーズ＋競合）取得（改良版）---
def fetch_pest_competition(user_input: dict) -> str | None:
    """
    外部環境分析用プロンプトを生成し、Responses API で Web検索を実行。
    優先サイトマスターを事前に加えて検索精度向上を図る。
    （強化版: PEST/5フォース/市場ニーズ/競合で各種具体的要求を厳密に盛り込む）
    """
    static_sites = {
        "全産業": [
            "https://www.boj.or.jp/research/brp/rer/index.htm",
            "https://www.smrj.go.jp/research_case/research/",
            "https://freelabo.jp/",
        ],
        "製造業（食品）": [
            "https://www.meti.go.jp/statistics/tyo/kougyo/result-2.html",
            "https://www.jeita.or.jp/japanese/stat/index.htm",
        ],
        "製造業（化学）": [
            "https://www.meti.go.jp/statistics/tyo/kougyo/result-2.html",
            "https://www.jeita.or.jp/japanese/stat/index.htm",
        ],
        "製造業（金属）": [
            "https://www.meti.go.jp/statistics/tyo/kougyo/result-2.html",
            "https://www.jeita.or.jp/japanese/stat/index.htm",
        ],
        "製造業（機械）": [
            "https://www.meti.go.jp/statistics/tyo/kougyo/result-2.html",
            "https://www.jeita.or.jp/japanese/stat/index.htm",
        ],
        "製造業（その他）": [
            "https://www.meti.go.jp/statistics/tyo/kougyo/result-2.html",
            "https://www.jeita.or.jp/japanese/stat/index.htm",
        ],
        "建設業（住宅）": [
            "https://www.mlit.go.jp/statistics/details/t-kensetsu.html",
            "https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00600403",
            "https://www.mlit.go.jp/statistics/details/t-kouji.html",
        ],
        "建設業（インフラ・土木）": [
            "https://www.mlit.go.jp/statistics/details/t-kensetsu.html",
            "https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00600403",
            "https://www.mlit.go.jp/statistics/details/t-kouji.html",
        ],
        "建設業（その他）": [
            "https://www.mlit.go.jp/statistics/details/t-kensetsu.html",
            "https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00600403",
            "https://www.mlit.go.jp/statistics/details/t-kouji.html",
        ],
        "小売業（食品）": [
            "https://www.meti.go.jp/statistics/tyo/syoudou/index.html",
            "https://www.stat.go.jp/data/kakei/index.html",
            "https://www.stat.go.jp/data/kouri/index.html",
            "https://www.depart.or.jp/",
            "https://jfa-fc.or.jp/contents/about/statistics/",
            "https://www.jcsa.gr.jp/",
            "https://www.super.or.jp/data/",
        ],
        "小売業（日用品）": [
            "https://www.meti.go.jp/statistics/tyo/syoudou/index.html",
            "https://www.stat.go.jp/data/kakei/index.html",
            "https://www.stat.go.jp/data/kouri/index.html",
            "https://www.depart.or.jp/",
            "https://jfa-fc.or.jp/contents/about/statistics/",
            "https://www.jcsa.gr.jp/",
            "https://www.super.or.jp/data/",
        ],
        "小売業（衣料品）": [
            "https://www.meti.go.jp/statistics/tyo/syoudou/index.html",
            "https://www.stat.go.jp/data/kakei/index.html",
            "https://www.stat.go.jp/data/kouri/index.html",
            "https://www.depart.or.jp/",
            "https://jfa-fc.or.jp/contents/about/statistics/",
            "https://www.jcsa.gr.jp/",
            "https://www.super.or.jp/data/",
        ],
        "小売業（その他）": [
            "https://www.meti.go.jp/statistics/tyo/syoudou/index.html",
            "https://www.stat.go.jp/data/kakei/index.html",
            "https://www.stat.go.jp/data/kouri/index.html",
            "https://www.depart.or.jp/",
            "https://jfa-fc.or.jp/contents/about/statistics/",
            "https://www.jcsa.gr.jp/",
            "https://www.super.or.jp/data/",
        ],
        "サービス業（医療・福祉）": [
            "https://www.stat.go.jp/data/ssds/index.html",
        ],
        "サービス業（教育）": [
            "https://www.stat.go.jp/data/ssds/index.html",
        ],
        "サービス業（IT・ソフトウェア）": [
            "https://www.stat.go.jp/data/ssds/index.html",
        ],
        "サービス業（コンサル）": [
            "https://www.stat.go.jp/data/ssds/index.html",
        ],
        "サービス業（その他）": [
            "https://www.stat.go.jp/data/ssds/index.html",
        ],
        "飲食業（飲食店・カフェ）": [
            "https://www.jfnet.or.jp/",
        ],
        "飲食業（居酒屋・バー）": [
            "https://www.jfnet.or.jp/",
        ],
        "飲食業（その他）": [
            "https://www.jfnet.or.jp/",
        ],
        "地方自治体": [],  # 後で地域から動的に生成
    }

    industry = user_input.get("業種", "")
    sites_to_include = []

    # 地方自治体の場合、地域から県名を抽出してURLを生成
    if industry == "地方自治体":
        region = user_input.get("地域", "")
        match = re.match(r".*?([^\s]+?県)", region)
        if match:
            prefecture_name = match.group(1)
            prefecture_slug_map = {
                "北海道": "hokkaido", "青森県": "aomori", "岩手県": "iwate", "宮城県": "miyagi",
                "秋田県": "akita", "山形県": "yamagata", "福島県": "fukushima", "茨城県": "ibaraki",
                "栃木県": "tochigi", "群馬県": "gunma", "埼玉県": "saitama", "千葉県": "chiba",
                "東京都": "tokyo", "神奈川県": "kanagawa", "新潟県": "niigata", "富山県": "toyama",
                "石川県": "ishikawa", "福井県": "fukui", "山梨県": "yamanashi", "長野県": "nagano",
                "岐阜県": "gifu", "静岡県": "shizuoka", "愛知県": "aichi", "三重県": "mie",
                "滋賀県": "shiga", "京都府": "kyoto", "大阪府": "osaka", "兵庫県": "hyogo",
                "奈良県": "nara", "和歌山県": "wakayama", "鳥取県": "tottori", "島根県": "shimane",
                "岡山県": "okayama", "広島県": "hiroshima", "山口県": "yamaguchi", "徳島県": "tokushima",
                "香川県": "kagawa", "愛媛県": "ehime", "高知県": "kochi", "福岡県": "fukuoka",
                "佐賀県": "saga", "長崎県": "nagasaki", "熊本県": "kumamoto", "大分県": "oita",
                "宮崎県": "miyazaki", "鹿児島県": "kagoshima", "沖縄県": "okinawa",
            }
            slug = prefecture_slug_map.get(prefecture_name, None)
            if slug:
                sites_to_include = [f"https://www.pref.{slug}.lg.jp/"]
    else:
        sites_to_include = static_sites.get(industry, [])

    sites_text = ""
    if sites_to_include:
        sites_text = "（参照優先サイト: " + ", ".join(sites_to_include) + "）\n\n"

    query = (
        f"{user_input.get('地域', '')} {industry} {user_input.get('主力商品・サービス', '')} "
        f"業界 {user_input.get('主な関心テーマ', user_input.get('経営課題選択', 'トレンド'))} 最新動向 PEST 市場ニーズ 競合"
    )
    prompt = (
        f"あなたはトップクラスの経営コンサルタントです。\n"
        f"{sites_text}"
        "以下の要件を厳格に守り、外部環境分析（PEST＋5フォース分析＋市場ニーズ＋競合分析）をA4 1～2枚分・専門家レポート並みに詳しく、日本語で出力してください。\n\n"
        "■ PEST分析（Political, Economic, Social, Technological）:\n"
        "  ・各PEST項目ごとに「実例／統計データ／政策動向／法改正／市場規模／成長率」を最低1件以上示す。\n"
        "■ 5フォース分析:\n"
        "  ・新規参入、供給者、買い手、代替品、業界内競争の5つすべてを文章で深掘りし、各項目を最低1段落以上書く。\n"
        "■ 市場ニーズ分析:\n"
        "  ・消費者ニーズ、市場成長性、需要変化、購買動向を最低3点示し、必ず数値や事例を含める。\n"
        "■ 競合分析:\n"
        "  ・主要競合を5社以上取り上げ、それぞれ「企業名／主な事業内容／強み／弱み／最新ニュース・事例（URL付）」をすべて記載する。\n"
        "■ 出典URL:\n"
        "  ・最低5件以上、推奨10件以上をMarkdownリンク形式で必ず示す。\n"
        "■ 抽象論・一般論は禁止。必ず対象地域と業種に基づく具体的事実・データを活用する。\n\n"
        f"【検索テーマ】{query}\n"
    )

    with st.spinner("Web検索＋PEST/市場ニーズ/競合AI分析中…"):
        try:
            response = client.responses.create(
                model="gpt-4o",
                input=prompt,
                tools=[{"type": "web_search"}]
            )
            return response.output_text
        except Exception as e:
            st.error(f"Responses APIエラー: {e}")
            return None

# --- 段階出力モード用 make_prompt_chapter() ---
def make_prompt_chapter(chapter_num: int) -> str:
    """
    段階出力モード用プロンプトを生成する関数。
    chapter_num: 現在出力したい章番号 (1〜9)
    """
    entity_type = st.session_state.user_input.get("法人／個人区分", "不明")
    profit_label = "営業利益" if entity_type == "法人" else "所得金額"

    # 財務指標を文字列化
    fin = st.session_state.fin
    profit_margin_val = fin.get("profit_margin")
    profit_margin_str = f"{profit_margin_val:.1f}%" if profit_margin_val is not None else "不明"
    cash_months_val = fin.get("cash_months")
    cash_months_str = f"{cash_months_val:.1f} ヶ月分" if cash_months_val is not None else "不明"
    burden_ratio_val = fin.get("burden_ratio")
    burden_ratio_str = f"{burden_ratio_val:.1f}%" if burden_ratio_val is not None else "不明"

    # 章タイトルマスター
    chapter_titles = {
        1: "1. 外部環境分析",
        2: "2. 内部環境分析",
        3: "3. 経営サマリー",
        4: "4. 真因分析",
        5: "5. 戦略アイディア",
        6: "6. VRIO分析",
        7: "7. 実行計画",
        8: "8. 次回モニタリング・PDCA設計",
        9: "9. 参考データ・URL"
    }
    chapter_title = chapter_titles.get(chapter_num, f"{chapter_num}. 未定義章")

    prompt = f"""
あなたは超一流の戦略系経営コンサルタントです。

これから **段階出力モード** でレポートを作成します。  
【第 {chapter_num} 章】（{chapter_title}）のみを、**必ず章番号と章タイトルをつけて出力**してください。  

【段階出力ルール】

・**1回に1章ずつのみ出力する**（他章は出力しない）。  
・章タイトルが飛ばないよう、「章番号＋章タイトル＋本文」の順で必ず出力する。  
・**未入力項目は「未入力」「不明」と明記**し、AI補完・推測は禁止。  
・抽象論・一般論は禁止。**ユーザー入力・外部データ**を最大限活用する。  
・**「質問モード」になったり、途中停止することは禁止**。  
・章番号が正しいか必ず確認すること。  

---

【今回出力する章】  
→ **{chapter_title}**（第 {chapter_num} 章のみ）  

---

【法人／個人区分】:
{entity_type}

【地域】:
{st.session_state.user_input.get("地域", "未入力")}

【業種】:
{st.session_state.user_input.get("業種", "未入力")}

【主力商品・サービス】:
{st.session_state.user_input.get("主力商品・サービス", "未入力")}

【財務指標】:
- 年間売上高: {fin['sales']:,} 円
- {profit_label}: {fin['profit']:,} 円
- 営業CF (簡易): {fin['op_cf']:,} 円
- {profit_label}率: {profit_margin_str}
- キャッシュ残高/月商: {cash_months_str}
- 借入金合計: {fin['loan']:,} 円
- 年間返済額: {fin['repay']:,} 円
- 返済負担感: {burden_ratio_str}

【ユーザー情報】:
{st.session_state.user_input}

【AI深掘り質問＋ユーザー回答】:
{st.session_state.ai_question}
{st.session_state.user_answer}

【外部環境（PEST・市場ニーズ・競合・Web情報）】:
{st.session_state.display_env}
"""
    return prompt

# --- 1️⃣4️⃣ PDF生成（目次自動生成付き） ---
def create_pdf(text_sections: list[dict], filename: str = "AI_Dock_Report.pdf") -> io.BytesIO:
    """
    PDFを生成します。目次ページを自動挿入。
    VRIO分析セクションは完全にスキップし、見やすい PDF レイアウトにする。
    """
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont("IPAexGothic", "ipag.ttf"))
    styles = getSampleStyleSheet()
    elements = []

    # 表紙タイトルスタイル
    title_style = ParagraphStyle(
        "Title",
        fontName="IPAexGothic",
        fontSize=22,
        textColor=colors.white,
        alignment=1,
        spaceAfter=12,
        backColor=colors.HexColor("#111111"),
        leading=30,
        borderPadding=4,
    )
    elements.append(Paragraph("AI経営診断GPTレポート", title_style))
    elements.append(Spacer(1, 16))

    # 目次ページ
    toc_style_title = ParagraphStyle(
        "TOC_Title",
        fontName="IPAexGothic",
        fontSize=18,
        textColor=colors.HexColor("#111111"),
        alignment=0,
        spaceAfter=10,
    )
    toc_style_item = ParagraphStyle(
        "TOC_Item",
        fontName="IPAexGothic",
        fontSize=12,
        textColor=colors.black,
        leftIndent=20,
        spaceAfter=4,
    )
    elements.append(Paragraph("目次", toc_style_title))
    # VRIOセクションを除いたセクションリスト
    filtered_sections = [sec for sec in text_sections if sec.get("title") != "VRIO分析"]
    for idx, sec in enumerate(filtered_sections, start=1):
        title = sec.get("title", "")
        elements.append(Paragraph(f"{idx}. {title}", toc_style_item))
    elements.append(Spacer(1, 20))

    # 各セクションをPDFに追加
    for sec in filtered_sections:
        title = sec.get("title", "")
        text = sec.get("text", "")

        # 見出しスタイル
        if title:
            section_style = ParagraphStyle(
                "Section",
                fontName="IPAexGothic",
                fontSize=16,
                textColor=colors.HexColor("#111111"),
                spaceBefore=20,
                spaceAfter=10,
                leading=24,
                leftIndent=0,
                alignment=0,
            )
            elements.append(Paragraph(title, section_style))

        # 本文スタイル（行間・スペース調整）
        para_style = ParagraphStyle(
            "Body",
            fontName="IPAexGothic",
            fontSize=11,
            textColor=colors.black,
            leading=18,      # 行間を18に
            spaceAfter=10,   # 段落間スペースを10に
            leftIndent=0,
            alignment=0,
        )

        # VRIO分析はすべてスキップ済み
        # それ以外のセクションは段落ごとに追加
        for para in text.split("\n\n"):
            clean_para = para.strip().replace("**", "")  # 太字マーク削除
            # 番号付きリストを箇条書きに変換
            if re.match(r"^\s*\d+\.\s+", clean_para):
                # リストアイテムを分割
                items = re.split(r"\s*\d+\.\s+", clean_para)[1:]
                lf = ListFlowable(
                    [ListItem(Paragraph(item.strip(), para_style), leftIndent=12) for item in items],
                    bulletType="bullet",
                    start="circle"
                )
                elements.append(lf)
            else:
                if clean_para:
                    # リンク [text](url) は "text (url)" に変換
                    clean_para = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r"\1 (\2)", clean_para)
                    elements.append(Paragraph(clean_para, para_style))

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    doc.build(elements)
    buffer.seek(0)
    return buffer

# --- 1️⃣5️⃣ CSVエクスポート ---
def export_to_csv() -> bytes | None:
    user_input = st.session_state.get("user_input", None)
    if not user_input:
        st.warning("エクスポートできる入力データがありません。")
        return None
    df = pd.DataFrame([user_input])
    return df.to_csv(index=False).encode("utf-8-sig")

# --- 1️⃣6️⃣ Excelエクスポート ---
def export_to_excel() -> bytes | None:
    user_input = st.session_state.get("user_input", None)
    if not user_input:
        return None
    try:
        import xlsxwriter
    except ImportError:
        return None
    df = pd.DataFrame([user_input])
    excel = io.BytesIO()
    with pd.ExcelWriter(excel, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    return excel.getvalue()

# --- 1️⃣7️⃣ ユーザー入力フォーム ---
def input_form(plan: str) -> None:
    """
    ステップ1：ユーザーが会社情報・財務情報・ヒアリング情報を入力するフォーム。
    セッション復元対応、主力商品・サービスを追加。
    「営業利益」→「所得金額」表記を法人／個人で切替。
    赤字入力を許容。
    """
    st.markdown('<div class="widecard">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1.6rem; font-weight:700; color:#111111; margin-bottom:8px;">'
        f'✅ {APP_TITLE}'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="info-box">'
        '・必須項目は「★」マーク。  \n'
        '・数字は半角数字のみ（カンマ不要）。  \n'
        '・住所は「番地まで書くと外部環境分析の精度が上がります」（任意）。  \n'
        '・入力は社長の感覚・主観でOKです。'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("form1"):
        col1, col2 = st.columns(2, gap="large")
        prev = st.session_state.get("user_input", {})

        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 基本情報")

            entity_type = st.radio(
                "★法人／個人事業主の区分",
                options=["法人", "個人事業主"],
                horizontal=True,
                index=["法人", "個人事業主"].index(prev.get("法人／個人区分", "法人")),
                key="field_entity_type"
            )

            company_name = st.text_input(
                "★会社名（屋号でもOK）",
                value=prev.get("会社名", ""),
                placeholder="例：株式会社サンプルアパレル／〇〇工房",
                key="field_company_name"
            )

            region = st.text_input(
                "★地域（番地まで任意）",
                value=prev.get("地域", ""),
                placeholder="例：東京都新宿区西新宿2-8-1",
                key="field_region"
            )

            industry_master = [
                "製造業（食品）", "製造業（化学）", "製造業（金属）", "製造業（機械）", "製造業（その他）",
                "建設業（住宅）", "建設業（インフラ・土木）", "建設業（その他）",
                "小売業（食品）", "小売業（日用品）", "小売業（衣料品）", "小売業（その他）",
                "サービス業（医療・福祉）", "サービス業（教育）", "サービス業（IT・ソフトウェア）", "サービス業（コンサル）", "サービス業（その他）",
                "飲食業（飲食店・カフェ）", "飲食業（居酒屋・バー）", "飲食業（その他）",
                "地方自治体"
            ]
            selected_industry = prev.get("業種", "")
            if selected_industry not in industry_master:
                selected_industry = industry_master[0]
            industry = st.selectbox(
                "★業種",
                industry_master,
                index=industry_master.index(selected_industry),
                key="field_industry"
            )

            industry_free = st.text_input(
                "業種（上記にない場合はこちらにご記入ください）",
                value=prev.get("業種（リスト外）", ""),
                placeholder="例：エンタメ系サービス業、複合型施設 など",
                key="field_industry_free"
            )

            main_product = st.text_input(
                "★主力の商品・サービス",
                value=prev.get("主力商品・サービス", ""),
                placeholder="例：高級食パン／業務用厨房機器／化粧品OEM など",
                key="field_main_product"
            )

            main_theme = st.text_input(
                "主な関心テーマ",
                value=prev.get("主な関心テーマ", ""),
                placeholder="市場動向、競合動向など",
                key="field_main_theme"
            )

            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 売上・財務")

            sales = st.text_input(
                "★年間売上高（円）",
                value=prev.get("年間売上高", ""),
                placeholder="90000000",
                key="field_sales"
            )

            sale_trend = st.selectbox(
                "売上高の増減",
                ["増加", "変わらない", "減少"],
                index=["増加", "変わらない", "減少"].index(prev.get("売上高の増減", "増加"))
                    if prev.get("売上高の増減") in ["増加", "変わらない", "減少"] else 0,
                help="現在の売上高が前年と比べて増加／変わらない／減少しているかを選択してください",
                key="field_sale_trend"
            )

            profit_label = "営業利益（円）" if entity_type == "法人" else "所得金額（円）"
            profit = st.text_input(
                f"★{profit_label}",
                value=prev.get("営業利益／所得金額", ""),
                placeholder="2000000",
                key="field_profit"
            )

            profit_trend_label = "営業利益の増減" if entity_type == "法人" else "所得金額の増減"
            profit_trend = st.selectbox(
                profit_trend_label,
                ["増加", "変わらない", "減少"],
                index=["増加", "変わらない", "減少"].index(prev.get("営業利益の増減／所得金額の増減", "増加"))
                    if prev.get("営業利益の増減／所得金額の増減") in ["増加", "変わらない", "減少"] else 0,
                help="現在の利益が前年と比べて増加／変わらない／減少しているかを選択してください",
                key="field_profit_trend"
            )

            cash = st.text_input(
                "現金・預金残高（円）",
                value=prev.get("現金・預金残高", ""),
                placeholder="5000000",
                key="field_cash"
            )

            loan_total = st.text_input(
                "借入金合計（円）",
                value=prev.get("借入金合計", ""),
                placeholder="10000000",
                key="field_loan_total"
            )

            monthly_repayment = st.text_input(
                "毎月返済額（円）",
                value=prev.get("毎月返済額", ""),
                placeholder="200000",
                key="field_monthly_repayment"
            )

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 組織・顧客")

            employee = st.text_input(
                "従業員数",
                value=prev.get("従業員数", ""),
                placeholder="18",
                key="field_employee"
            )

            customer_type = st.text_input(
                "主な顧客層",
                value=prev.get("主な顧客層", ""),
                placeholder="個人顧客／若年層中心",
                key="field_customer_type"
            )

            customer_trend = st.selectbox(
                "主要顧客数の増減",
                ["増加", "変わらない", "減少"],
                index=["増加", "変わらない", "減少"].index(prev.get("主要顧客数の増減", "増加"))
                    if prev.get("主要顧客数の増減") in ["増加", "変わらない", "減少"] else 0,
                help="現在の主要顧客数が増加／変わらない／減少しているかを選択してください",
                key="field_customer_trend"
            )

            channel = st.text_input(
                "★主な販売チャネル",
                value=prev.get("主な販売チャネル", ""),
                placeholder="店舗／EC／SNS",
                key="field_channel"
            )

            competitor = st.selectbox(
                "競合の多さ",
                ["多い", "普通", "少ない"],
                index=["多い", "普通", "少ない"].index(prev.get("競合の多さ", "普通"))
                    if prev.get("競合の多さ") in ["多い", "普通", "少ない"] else 1,
                key="field_competitor"
            )
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 現場ヒアリング・強み")

            hearing_raw_default = "\n".join(prev.get("現場ヒアリング所見", []))
            hearing_raw = st.text_area(
                "★現場・営業・顧客などの“生の声”や現場所見（1～3行、肌感でOK）",
                value=hearing_raw_default,
                height=110,
                placeholder=(
                    "例：販売スタッフ「来店客数が前年同月比で15%減少しています。特に平日の午後はほとんど動きがありません。」"
                ),
                key="field_hearing_raw"
            )
            hearing_list = [s.strip() for s in hearing_raw.split("\n") if s.strip()]
            st.session_state["field_hearing_list"] = hearing_list

            strength = st.text_input(
                "自社の強み（主観でOK、1文）",
                value=prev.get("自社の強み", ""),
                placeholder="地元密着の接客／独自セレクト商品",
                key="field_strength"
            )

            issue_choice = st.selectbox(
                "★最も課題と感じるテーマ",
                ["資金繰り", "売上低迷", "人材確保", "新規顧客獲得", "その他"],
                index=["資金繰り", "売上低迷", "人材確保", "新規顧客獲得", "その他"].index(prev.get("経営課題選択", "資金繰り")),
                key="field_issue_choice"
            )

            issue_detail = st.text_area(
                "★課題の具体的な内容（1〜2行でOK）",
                value=prev.get("経営課題自由記述", ""),
                height=70,
                placeholder="来店客数の減少と在庫回転の悪化",
                key="field_issue_detail"
            )

            cash_status = st.selectbox(
                "資金繰りの状態",
                ["安定", "やや不安", "危機的"],
                index=["安定", "やや不安", "危機的"].index(prev.get("資金繰りの状態", "安定")),
                key="field_cash_status"
            )

            legal_flag = st.checkbox(
                "法律・税務・社労士領域等の専門的な悩みも入力した場合はチェック",
                value=prev.get("法務税務フラグ", False),
                key="field_legal_flag"
            )

            external_env = st.text_area(
                "外部環境・市況感（例：人口減、材料高騰、業界再編等）",
                value=prev.get("外部環境肌感", ""),
                height=70,
                placeholder=(
                    "コロナ禍以降、商業施設の来場者数が減少傾向。ECサイト利用率上昇。為替変動による仕入価格上昇など。"
                ),
                key="field_external_env"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        # --- バリデーション ---
        errors = []
        non_neg_fields = [
            ("年間売上高", sales),
            ("借入金合計", loan_total),
            ("毎月返済額", monthly_repayment),
            ("現金・預金残高", cash),
            ("従業員数", employee),
        ]
        for label, val in non_neg_fields:
            if val and not is_valid_non_negative(val):
                errors.append(f"「{label}」は0以上の半角数字のみ入力してください。")

        if profit and not is_integer(profit):
            errors.append(f"「{profit_label}」は整数で入力してください。")

        industry_value = industry_free.strip() if industry_free.strip() else industry

        for key, val in [
            ("会社名", company_name),
            ("地域", region),
            ("業種", industry_value),
            ("主力商品・サービス", main_product),
            ("主な販売チャネル", channel),
            ("最も課題と感じるテーマ", issue_choice),
        ]:
            if not val:
                errors.append(f"{key}は必須です")

        if not hearing_list:
            errors.append("現場・営業・顧客などの“生の声”を1つ以上入力してください")
        if not issue_detail.strip():
            errors.append("課題の具体的な内容は必須です")

        submit = st.form_submit_button("▶ AI診断を開始する")
        if errors and submit:
            st.markdown('<div class="err-box">' + "<br>".join(errors) + '</div>', unsafe_allow_html=True)
            return

        if submit:
            # セッションにユーザー入力データを保存
            st.session_state.user_input = {
                "法人／個人区分": entity_type,
                "会社名": company_name,
                "地域": region,
                "業種": industry_value,
                "業種（リスト外）": industry_free,
                "主力商品・サービス": main_product,
                "主な関心テーマ": main_theme,
                "年間売上高": sales,
                "売上高の増減": sale_trend,
                "営業利益／所得金額": profit,
                "営業利益の増減／所得金額の増減": profit_trend,
                "現金・預金残高": cash,
                "借入金合計": loan_total,
                "毎月返済額": monthly_repayment,
                "従業員数": employee,
                "主な顧客層": customer_type,
                "主要顧客数の増減": customer_trend,
                "主な販売チャネル": channel,
                "競合の多さ": competitor,
                "経営課題選択": issue_choice,
                "経営課題自由記述": issue_detail,
                "自社の強み": strength,
                "資金繰りの状態": cash_status,
                "現場ヒアリング所見": hearing_list,
                "外部環境肌感": external_env,
                "プラン": plan,
                "法務税務フラグ": legal_flag,
            }
            # AIログ用
            if "log" not in st.session_state:
                st.session_state.log = []
            st.session_state.step = 2
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="button-bar">', unsafe_allow_html=True)
    if st.button("⟳ 入力内容をリセット", key="btn_reset_partial"):
        for key in list(st.session_state.keys()):
            if key.startswith("field_") or key in [
                "user_input", "ai_question", "user_answer",
                "final_report", "text_sections", "keep_report",
                "pdf_buffer", "log", "fin", "display_env"
            ]:
                del st.session_state[key]
        st.rerun()
    if st.button("🚫 セッション完全リセット", key="btn_reset_full"):
        st.session_state.clear()
        st.session_state["_rerun_triggered"] = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.get("_rerun_triggered", False):
        st.session_state["_rerun_triggered"] = False
        st.rerun()

# --- 1️⃣8️⃣ AI追加質問フェーズ ---
def ai_deep_question() -> None:
    """
    ステップ2：AIによる追加ヒアリング質問を生成し、ユーザーの回答を受け取る。
    """
    st.markdown('<div class="widecard">', unsafe_allow_html=True)
    st.subheader("AIによる追加ヒアリング（深掘り質問）")
    st.markdown(
        '<div class="info-box">'
        'AIが“現場のプロ診断”を作成するため、あと1点だけ追加質問をします。必ずご回答ください。'
        '</div>',
        unsafe_allow_html=True,
    )

    user_input = st.session_state.user_input
    question_prompt = f"""
あなたは超一流の経営コンサルタントです。下記のクライアント企業の現状データ・ヒアリング内容を読んでください。
この経営診断レポートの質と現場リアリティ・説得力を最大化するため、
「“誰の声・どんな頻度・どんな実例/現象・費用感・根拠・壁”までリアルに掘り下げる最重要な追加質問」を1つ厳選して必ず出力してください。
推測や決めつけは禁止し、「ユーザーが入力した内容以外は尋ねない」こと。
【必ず参考回答例も出力してください。】
【現状データ・ヒアリング情報】
{user_input}
"""

    with st.spinner("AIが追加質問を自動生成中…"):
        try:
            q_resp = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": question_prompt}],
                max_tokens=700,
                temperature=0.13,
            )
            ai_question = q_resp.choices[0].message.content
            st.session_state.ai_question = ai_question
            st.session_state.log.append({
                "stage": "deep_question",
                "prompt": question_prompt,
                "response": ai_question
            })
        except Exception as e:
            st.error(f"AIエラー: {e}")
            st.stop()

    st.markdown("### AIからの質問")
    st.markdown(ai_question)

    prev_answer = st.session_state.get("user_answer", "")
    with st.form("form2"):
        user_answer = st.text_area(
            "上記のAI質問へのご回答を自由にご記入ください（実名・役職・頻度・金額・根拠・失敗経験もできるだけ具体的に）",
            value=prev_answer,
            height=150,
            key="field_user_answer"
        )
        submit2 = st.form_submit_button("▶ 診断レポートを生成")

    st.markdown('<div class="button-bar">', unsafe_allow_html=True)
    if st.button("← 戻る", key="btn_back_to_step1"):
        st.session_state.step = 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if submit2:
        st.session_state.user_answer = user_answer
        st.session_state.step = 3
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- 1️⃣9️⃣ レポート生成フェーズ ---
def generate_report(font_path: str) -> None:
    """
    ステップ3：AIを使って最終診断レポートを生成し、PDF/CSV/Excel出力をまとめる。
    進捗バー＆ログ記録対応。アンケートリンクをレポート最下部に追加。
    """
    st.markdown('<div class="widecard">', unsafe_allow_html=True)
    st.subheader("AI経営診断GPTレポート")

    # 財務指標計算をセッションに保存
    fin = calc_finance_metrics(st.session_state.user_input)
    st.session_state.fin = fin

    tab_exec, tab_report, tab_gloss = st.tabs(["EXEC SUMMARY", "詳細レポート", "用語辞典"])

    with tab_exec:
        render_exec_summary(st.session_state.user_input, fin)

    with tab_gloss:
        render_glossary()

    with tab_report:
        # すでに生成済みなら再利用
        if "final_report" not in st.session_state or not st.session_state.get("keep_report", False):
            st.info("AI診断レポート生成中… 進捗状況を表示します。")
            progress = st.progress(0)

            user_input   = st.session_state.user_input
            ai_question  = st.session_state.ai_question
            user_answer  = st.session_state.user_answer

            # --- 外部環境データ取得 ---
            with st.spinner("外部環境データ取得中…"):
                external_env_text = fetch_pest_competition(user_input) or ""
            progress.progress(20)

            # display_env をセッションに保存
            if external_env_text.strip() == "" or "取得エラー" in external_env_text:
                display_env = "未入力：外部環境分析情報が不足しています。"
            else:
                display_env = external_env_text.strip()
            st.session_state.display_env = display_env

            # --- レポート作成プロンプト組立 ---
            def make_prompt() -> str:
                entity_type = user_input.get("法人／個人区分", "不明")
                profit_label = "営業利益" if entity_type == "法人" else "所得金額"
                profit_trend_label = "営業利益トレンド" if entity_type == "法人" else "所得金額トレンド"

                # 財務指標の文字列化
                profit_margin_val = fin.get("profit_margin")
                profit_margin_str = f"{profit_margin_val:.1f}%" if profit_margin_val is not None else "不明"
                cash_months_val = fin.get("cash_months")
                cash_months_str = f"{cash_months_val:.1f} ヶ月分" if cash_months_val is not None else "不明"
                burden_ratio_val = fin.get("burden_ratio")
                burden_ratio_str = f"{burden_ratio_val:.1f}%" if burden_ratio_val is not None else "不明"

                return f"""
あなたは超一流の戦略系経営コンサルタントです。

以下の順で、**現場の社長／経営者がそのまま社内外に使える「納品レベルの詳細レポート（約A4 2〜3枚相当の情報量）」**を作成してください。
構成順は必ず守り、各章で抜け漏れ・薄さがないよう、具体的な数値・事例・出典URLを必ず示してください。
未入力の箇所は「未入力」「不明」と明記し、AI推測は禁止です。

【構成順】（順番は絶対厳守。全項目を必ず出力すること）

1. 外部環境分析  
   ・PEST分析(Political, Economic, Social, Technological)では各項目ごとに「実例／統計データ／政策動向／法改正／市場規模／成長率」の具体数値・事例を最低1件以上示すこと。  
   ・5フォース分析では「新規参入」「供給者」「買い手」「代替品」「業界内競争」の5項目すべてを深掘りし、各1段落以上記載すること。  
   ・市場ニーズ分析では「消費者ニーズ」「市場成長性」「需要変化」「購買動向」の最低3点を示し、必ず数値・事例を含めること。  
   ・競合分析では主要競合5社以上を取り上げ、「企業名」「主な事業内容」「強み」「弱み」「最新ニュース・事例(URL付)」すべて記載すること。  
   ・出典URLは最低5件以上、推奨10件以上をMarkdownリンク形式で必ず示し、情報の信頼性を担保すること。  
   ・抽象論・一般論は禁止。必ず対象地域・業種に基づく具体的事実・データを活用すること。  
   ・未入力の場合は「外部環境分析: 未入力」と明記し、出力を続行すること。

2. 内部環境分析  
   ・現場ヒアリング所見やユーザー入力を可能な限り活用し、従業員の声・内部プロセス改善状況を具体的に記載すること。  
   ・ユーザー未入力項目は「未入力」と明記し、AI推測を行わないこと。  
   ・現場視点での課題・ボトルネックを整理し、事例・数値を含めること。

3. 経営サマリー  
   ・「現状数字(財務指標)」「主な課題(ユーザー入力)」を整理し、内部情報と矛盾がないように記載すること。  
   ・ユーザー未入力項目は「未入力」「不明」と明記し、AI推測を禁止すること。  
   ・簡潔に要点をまとめ、社内外に提示できるレベルの品質とすること。

4. 真因分析  
   ・KPI悪化の本当の原因を、現場視点で要因分解し、論理的に分析すること。  
   ・ユーザー入力内容を最大限活用し、AIによる勝手な推測は禁止すること。  
   ・未入力の場合は「未入力」と明記し、先に進めること。

5. 戦略アイディア  
   ・必ず4案を提示し、各案について以下を明確に記載すること：  
     ① 案名  
     ② 根拠・事例  
     ③ 投資額（数値）  
     ④ 期待効果（数値目標）  
     ⑤ 回収月数（数値）  
     ⑥ 他案との差別性・選定理由（なぜこの案が最適か、他案はなぜ劣るか）  
   ・クロスSWOTのS×Oを中心とし、具体的な数値・事例を使って説得力を高めること。

6. VRIO分析  
   ・上記の4案を「Valuable（価値）」「Rare（希少性）」「Inimitable（模倣困難性）」「Organization（組織活用力）」の4観点で、必ず数値(1～5点)で点数化し、Markdown表形式で出力すること。  
   ・「高・中・低」といった表現は禁止し、必ず数値を使用すること。  
   ・表の下に評価基準例(例：5点=極めて高い競争優位、1点=競争優位がほとんどない)を必ず記載すること。  
   ・「最もスコア高い案: ○○○」を明示し、選定理由を論理的に説明すること。  
   ・PDF化時は最終案のみ強調表示すること。

7. 実行計画  
   ・最も優先すべき案について、以下を5W1Hで具体化して記載すること。  
     Who: 担当者  
     What: 施策内容  
     When: 期限（具体的な日付は禁止、例：「半年以内」「今期中」など曖昧表現）  
     Where: 実行場所や部署  
     Why: なぜこの案が最適なのか論理的に説明  
     How: 実行プロセス  
     How much: 投資額やリソース  
   ・リスク要因と対策案を具体的に記載し、明確化すること。

8. 次回モニタリング・PDCA設計  
   ・実行計画のKPIと整合性をとり、具体的なKPI指標を設定すること。  
   ・チェック頻度(例：月次、週次)、担当者、指標(数値)を明確に記載すること。  
   ・改善アクションを明示し、PDCAのフローを具体的に設計すること。

9. 参考データ・URL  
   ・外部環境分析などで使用した出典・参考URLをMarkdownリンク形式で最低5件以上、推奨10件以上記載すること。  
   ・URLだけでなくタイトルも明記し、情報の信頼性を担保すること。

【必須条件】

・「202X年」「20XX年」「〇年〇月」「〇月」などの具体的な年月表現は禁止。年次・時期など、曖昧な表現に置き換えること。  
・数字、現場エピソード、論理根拠を重視し、抽象論・一般論は使用しない。  
・AIがユーザー情報を勝手に補完することを禁止し、ユーザー未入力項目は必ず「未入力」「不明」と明記する。  
・構成順は必ず順守し、章番号と見出しを必ず含めること。途中でレポート出力を中断しない。  
・全体として約2000〜3000字程度の「A4 2〜3枚相当」の現場納品品質を目指す。  
・絶対に全9章（1.～9.）の構成順で、すべての章を出力すること。  
・途中で停止しないこと。  
・章が未記載／飛ばし／省略にならないよう注意すること。  
・出力が長くなる場合は「章ごとに区切って段階的に出力」してもよい。  
---

【法人／個人区分】:
{entity_type}

【地域】:
{user_input.get("地域", "未入力")}

【業種】:
{user_input.get("業種", "未入力")}

【主力商品・サービス】:
{user_input.get("主力商品・サービス", "未入力")}

【財務指標】:
- 年間売上高: {fin['sales']:,} 円
- {profit_label}: {fin['profit']:,} 円
- 営業CF (簡易): {fin['op_cf']:,} 円
- {profit_label}率: {profit_margin_str}
- キャッシュ残高/月商: {cash_months_str}
- 借入金合計: {fin['loan']:,} 円
- 年間返済額: {fin['repay']:,} 円
- 返済負担感: {burden_ratio_str}

【ユーザー情報】:
{user_input}

【AI深掘り質問＋ユーザー回答】:
{ai_question}
{user_answer}

【外部環境（PEST・市場ニーズ・競合・Web情報）】:
{display_env}
"""
            # 1回目のレポート生成
            try:
                main_prompt = make_prompt()
                st.session_state.log.append({
                    "stage": "report_generation_prompt",
                    "prompt": main_prompt
                })
                resp1 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": main_prompt}],
                    max_tokens=4000,
                    temperature=0.01,
                )
                first_report = resp1.choices[0].message.content
                st.session_state.log.append({
                    "stage": "report_generation_response_initial",
                    "response": first_report
                })
                progress.progress(50)

                # ダブルチェック＆修正プロンプト
                double_prompt = f"""
あなたは超一流の戦略系経営コンサルタントです。
以下のレポート初稿を、現場納品レベルに引き上げるため、厳格なダブルチェック＋改善提案を行ってください。
全体の構成順(1〜9章)が正しいことを必ず確認し、抜け漏れがないかチェックしながら修正してください。
ユーザー未入力項目には「未入力」「不明」と明記されているか厳密に確認してください。
AI補完や推測は禁止です。

【特に重点的にチェック・改善する事項】

1. 外部環境分析（PEST／5フォース／市場ニーズ／競合分析）
・ 市場規模／成長率／法改正／政策動向／主要競合動向／先行事例を必ず明記すること
・ 各章に事例／データ／数値／出典URL（Markdownリンク）を含め、具体性を高めること
・ 抽象論・一般論が混じっていないか確認すること

2. 内部環境分析／真因分析
・ ユーザー入力内容・現場ヒアリング内容が100%反映されているか確認すること
・ AIの補完・推測は禁止
・ 未入力項目には「未入力」と明記されているか確認すること

3. 経営サマリー
・ 財務数値、現状課題、内部情報に矛盾・抜けがないか確認すること
・ ユーザー未入力項目は「未入力」「不明」と明記されているか確認すること

4. 戦略アイディア（4案）
・ 各案の「実効性／投資額／期待効果／回収月数」を明確に記載しているか確認すること
・ 他案との差別性・選定理由（なぜこの案が最適か、他案はなぜ劣るか）を必ず記載すること

5. VRIO分析
・ Markdown表形式で数値(1〜5点)を出力しているか確認すること
・ 「高・中・低」による表現は禁止 → 数値のみで表記されているか確認すること
・ 評価基準（例：5点＝極めて高い競争優位、1点＝競争優位ほぼなし）を必ず表の下に記載しているか確認すること
・ 「最もスコア高い案: ○○○」が明示されているか確認すること

6. 実行計画
・ KPI・担当・期限・リスク・最初の一歩が5W1Hで具体化されているか確認すること
・ 「なぜこの案が最適なのか？」「なぜ他案は劣るのか？」の説明が十分か確認すること

7. 次回モニタリング・PDCA設計
・ KPIが実行計画と整合しているか確認すること（例：売上向上施策なら売上KPI）
・ チェック頻度・担当者・指標が具体的に記載されているか確認すること
・ PDCAのフローが具体的に設計されているか確認すること

8. 参考データ・URL
・ 最低5件以上（タイトル＋URL）をMarkdownリンク形式で記載しているか確認すること
・ 出典の信頼性が高いか確認すること

9. 構成順と抜け漏れ
・ 1〜9章がすべて出力されているか確認すること
・ 各章の見出し番号が正しい順番か確認すること
・ 未入力項目が「未入力」「不明」と明記されているか確認すること
・構成順が崩れていないかを章ごとに厳密に確認すること（1～9章）。
・「章番号が飛んでいないか」「章タイトルがすべて存在するか」を明確に確認し、欠けている場合は必ず補完すること。

【禁止事項】
・「202X年」「20XX年」「〇年〇月」「〇月」などの具体的日付表現は禁止。
・AIがユーザー未入力項目を推測・補完することは禁止。
・構成順が崩れていないか必ず確認し、最後までレポート形式で出力を継続すること。

【全体方針】
・抜け漏れゼロ、薄さゼロ、具体性高めの「現場納品品質」を徹底すること。
・数値、現場エピソード、論理根拠を重視し、抽象論を禁止すること。
・ユーザー入力と外部データを最大限活用し、事実ベースで記載すること。
・「現場納得感」「実行可能性」「具体性」を最優先すること。

【レポート初稿】
{first_report}
"""
                st.session_state.log.append({
                    "stage": "double_check_prompt",
                    "prompt": double_prompt
                })
                resp2 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": double_prompt}],
                    max_tokens=4000,
                    temperature=0.01,
                )
                final_report = resp2.choices[0].message.content
                st.session_state.log.append({
                    "stage": "double_check_response",
                    "response": final_report
                })
                progress.progress(80)

                # 不要な末尾メッセージを自動的に取り除く
                final_report = final_report.replace(
                    "以上の修正により、レポートは現場での実行に耐えうる品質となっています。", ""
                ).strip()

                # セクション分割＆番号振り直し（GPTミス対策）
                section_titles = [
                    ("外部環境分析", r"\d+[\.．]\s*外部環境分析"),
                    ("内部環境分析", r"\d+[\.．]\s*内部環境分析"),
                    ("経営サマリー", r"\d+[\.．]\s*経営サマリー"),
                    ("真因分析", r"\d+[\.．]\s*真因分析"),
                    ("戦略アイディア", r"\d+[\.．]\s*戦略アイディア"),
                    ("VRIO分析", r"\d+[\.．]\s*VRIO分析"),
                    ("実行計画", r"\d+[\.．]\s*実行計画"),
                    ("次回モニタリング・PDCA設計", r"\d+[\.．]\s*次回モニタリング・PDCA設計"),
                    ("参考データ・URL", r"\d+[\.．]\s*参考データ・URL"),
                ]
                text_sections = []
                # 改行前に番号をリセットして1〜9を強制付番
                normalized_report = final_report
                for idx, (title, pattern) in enumerate(section_titles, start=1):
                    normalized_report = re.sub(
                        pattern,
                        f"{idx}. {title}",
                        normalized_report,
                        flags=re.MULTILINE
                    )
                # セクションごとに切り出し
                for i, (title, _) in enumerate(section_titles):
                    pattern_i = rf"{i+1}\.\s*{title}"
                    match_i = re.search(pattern_i, normalized_report)
                    if match_i:
                        start = match_i.end()
                        if i+1 < len(section_titles):
                            pattern_next = rf"{i+2}\.\s*{section_titles[i+1][0]}"
                            match_next = re.search(pattern_next, normalized_report[start:])
                            end = start + match_next.start() if match_next else len(normalized_report)
                        else:
                            end = len(normalized_report)
                        section_text = normalized_report[start:end].strip()
                        text_sections.append({
                            "title": title,
                            "text": section_text
                        })

                # セッションに保存
                st.session_state["final_report"]  = normalized_report
                st.session_state["text_sections"] = text_sections
                st.session_state["keep_report"]   = True
                progress.progress(100)

            except Exception as e:
                st.error(f"AIエラー内容: {e}")
                st.stop()

        # --- レポート本文を表示（Markdownを強調調整） ---
        st.markdown(st.session_state["final_report"], unsafe_allow_html=False)

        # 再生成オプション
        st.markdown("---")
        st.markdown("#### 入力内容の再編集・再生成")
        st.markdown('<div class="button-bar">', unsafe_allow_html=True)
        if st.button("入力内容を再編集して再生成", key="btn_restart_generation"):
            st.session_state.step        = 1
            st.session_state.keep_report = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # --- PDF生成・ダウンロード ---
        if st.session_state.get("pdf_buffer") is None:
            buffer = create_pdf(st.session_state["text_sections"], filename="AI_Dock_Report.pdf")
            st.session_state["pdf_buffer"] = buffer

        st.download_button(
            "PDFをダウンロード",
            data=st.session_state["pdf_buffer"],
            file_name="AI_Dock_Report.pdf",
            mime="application/pdf",
        )

        # --- 入力データのエクスポート（CSV/Excel） ---
        st.markdown("---")
        st.markdown("#### 入力データのエクスポート")
        col1, col2 = st.columns(2)
        with col1:
            csv_data = export_to_csv()
            if csv_data:
                st.download_button(
                    label="CSVダウンロード",
                    data=csv_data,
                    file_name="AI_Dock_Input.csv",
                    mime="text/csv",
                )
        with col2:
            excel_data = export_to_excel()
            if excel_data:
                st.download_button(
                    label="Excelダウンロード",
                    data=excel_data,
                    file_name="AI_Dock_Input.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                st.caption("（Excel出力には xlsxwriter パッケージが必要です）")

        # --- アンケートリンク表示 ---
        st.markdown("---")
        st.markdown("### 📣 アンケートのお願い")
        st.markdown("""
大変お手数ですが、本アプリの改善のためにご協力ください。  
[ご利用後アンケート（Googleフォーム）はこちら](https://docs.google.com/forms/d/e/1FAIpQLSeOwzqGwktHwJNgh9vBCUT8cGfFEHuAd8zwQ04k1uxDNgcKQA/viewform?usp=sf_link)  
""", unsafe_allow_html=True)

    st.markdown('<div class="button-bar">', unsafe_allow_html=True)
    if st.button("← 戻る", key="btn_back_to_step2"):
        st.session_state.step = 2
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 活用イメージ表示（ChatGPT/Notion風シンプルカード） ---
def render_usage_scenarios() -> None:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### ✨ このAI診断の活用イメージ")
    st.markdown("""
✅ **忙しい中でも今の経営状況や課題をスッキリ整理して、頭をクリアにしたい**  
✅ **売上が伸び悩み、次の一手や新たな打ち手を見つけたい**  
✅ **資金繰りや借入返済に先行きの不安があり、早めに対策を練りたい**  
✅ **社員や家族と「これからどうするか」を共有し、方向性を揃えたい**  
✅ **頭の中の考えや現場の声をまとめて「見える化」したい**  
✅ **金融機関との面談や融資交渉で、説得力ある経営方針を示したい**  
✅ **補助金申請に向けて、納得感のある事業計画のたたき台を作りたい**  
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 2️⃣0️⃣ メイン実行部 ---
def main() -> None:
    # PDF用フォント確認
    font_path = check_font()

    # セッションのstep初期化
    if "step" not in st.session_state:
        # ステップ0（規約同意）から始める
        st.session_state.step = 0

    # --- デバッグ用セッション初期化 ---
    if debug:
        if "user_input" not in st.session_state:
            st.session_state.user_input = {
                "法人／個人区分": "法人",
                "会社名": "大阪食品工業株式会社",
                "地域": "大阪府東大阪市",
                "業種": "製造業（食品）",
                "業種（リスト外）": "",
                "主力商品・サービス": "業務用冷凍総菜・冷凍パン",
                "主な関心テーマ": "業界動向・省人化投資",
                "年間売上高": "45000000",
                "売上高の増減": "変わらない",
                "営業利益／所得金額": "3000000",
                "営業利益の増減／所得金額の増減": "減少",
                "現金・預金残高": "8000000",
                "借入金合計": "10000000",
                "毎月返済額": "250000",
                "従業員数": "18",
                "主な顧客層": "外食チェーン・給食事業者",
                "主要顧客数の増減": "減少",
                "主な販売チャネル": "法人営業・卸",
                "競合の多さ": "多い",
                "経営課題選択": "人材確保",
                "経営課題自由記述": "製造現場の人手不足と技能継承の課題あり。採用難が続いている。",
                "自社の強み": "品質管理の徹底／小ロット対応／OEM実績",
                "資金繰りの状態": "やや不安",
                "現場ヒアリング所見": [
                    "中堅スタッフの退職が続き現場に負担がかかっている",
                    "自動包装機導入により一部工程は改善したが、梱包・出荷工程は依然として手作業中心"
                    "原材料費高騰により利益率が低下"
                ],
                "外部環境肌感": "最低賃金上昇、人手不足が深刻化、取引先からの価格交渉が厳しい",
                "プラン": "Lite（AI経営診断GPT・無料）",
                "法務税務フラグ": False,
            }
            st.session_state.ai_question = "製造現場の技能継承に関して、現在どのような取り組みや課題がありますか？現場からの声も教えてください。"
            st.session_state.user_answer = "現在は現場リーダーがOJTで新人教育を行っていますが、マニュアル整備が遅れており、属人化が進んでいます。リーダー層からは『教育の時間が取れない』という声が出ています。"
            if "log" not in st.session_state:
                st.session_state.log = []
            st.session_state.step = 3  # デバッグで直接レポート生成へ

    # --- プラン選択 ---
    if debug:
        # デバッグ時はセッションの user_input からプラン取得（固定：Lite）
        plan = st.session_state.user_input.get("プラン", "Lite（AI経営診断GPT・無料）")
        st.sidebar.success(f"✅ デバッグモード中 - 使用プラン: {plan}")
    else:
        # 通常時は活用イメージ → サイドバーでプラン選択
        render_usage_scenarios()
        plan = select_plan()
        if plan.startswith("Starter"):
            st.info("「Starter（右腕・API連携）」プランは現在準備中です。しばらくお待ちください。")
            return
        if plan.startswith("Pro"):
            st.info("「Pro（参謀・戦略実行支援）」プランは現在準備中です。しばらくお待ちください。")
            return

    # --- ステップごとの画面遷移 ---
    step = st.session_state.get("step", 0)
    if step == 0:
        show_policy_step()
        return
    elif step == 1:
        input_form(plan)
    elif step == 2:
        ai_deep_question()
    elif step == 3:
        generate_report(font_path)
    else:
        st.error("AIレポートの生成に失敗しました。入力内容やプロンプトを見直し、再度お試しください。")

# --- 2️⃣1️⃣ エントリーポイント ---
if __name__ == "__main__":
    main()
