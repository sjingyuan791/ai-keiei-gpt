# -*- coding: utf-8 -*-
# ============================================
# AI経営診断GPT Lite版 v1.4-beta2_fixed 完全版（コピペOK・GitHub品質）
# バージョン: 2025-06-20_v1.4-beta2_fixed
# ============================================

# --- 1️⃣ インポート ---
import streamlit as st
import os
import io
import re
import pandas as pd
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# --- 2️⃣ アプリ初期設定（必ず先頭に配置！） ---
APP_TITLE = "AI経営診断GPT【Lite版 v1.4-beta2_fixed】"
st.set_page_config(page_title=APP_TITLE, layout="wide")

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
/* ボタン */
.stButton > button {
    font-size: 1.1em !important;
    font-family: 'Inter', 'Noto Sans JP', sans-serif !important;
    padding: 0.75em 2em !important;
    border-radius: 8px !important;
    background: #000000 !important;
    color: #ffffff !important;
    font-weight: 600;
    border: none;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    transition: all 0.1s ease-in-out;
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
/* 戻るボタン中央寄せ */
.center-button {
    text-align: center;
    margin: 12px 0;
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

# --- 5️⃣ Googleスプレッド保存関数（デバッグ強化版＆ヘッダー検証） ---
def save_to_gsheet(data: list) -> bool:
    """
    Googleスプレッドシートにデータを保存する（デバッグ強化版）。
    既存ヘッダーと照合し、異なる場合はクリアしてヘッダー再作成。
    """
    headers = [
        "法人／個人区分",
        "会社名（マスク済）",
        "地域",
        "業種",
        "主力商品・サービス",
        "★年間売上高",
        "売上高の増減",
        "営業利益",
        "営業利益の増減",
        "借入金合計",
        "毎月返済額",
        "現金・預金残高",
        "従業員数",
        "主な顧客層",
        "主要顧客数の増減",
        "主な販売チャネル",
        "競合の多さ",
        "経営課題選択",
        "経営課題自由記述",
        "自社の強み",
        "資金繰りの状態",
        "現場ヒアリング所見",
        "外部環境肌感",
        "プラン",
        "法務税務フラグ",
        "主な関心テーマ",
    ]

    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = {
            "type": st.secrets["google"]["type"],
            "project_id": st.secrets["google"]["project_id"],
            "private_key_id": st.secrets["google"]["private_key_id"],
            "private_key": st.secrets["google"]["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["google"]["client_email"],
            "client_id": st.secrets["google"]["client_id"],
            "auth_uri": st.secrets["google"]["auth_uri"],
            "token_uri": st.secrets["google"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["google"]["client_x509_cert_url"],
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
        client_gs = gspread.authorize(creds)

        # 新しいスプレッドシートIDに固定
        sheet_id = st.secrets["google"]["sheet_id"]
        st.info(f"[DEBUG] sheet_id: {sheet_id}")

        # シート取得
        sheet = client_gs.open_by_key(sheet_id).sheet1

        # 全データ確認
        all_vals = sheet.get_all_values()
        st.info(f"[DEBUG] 取得した全行: (行数: {len(all_vals)})")

        # ヘッダーが必要か判定
        if not all_vals or all_vals == [['']] or len(all_vals) == 0:
            st.info("✅ [DEBUG] シートが空です → ヘッダー行を書き込みます。")
            sheet.append_row(headers)
            st.info("✅ ヘッダーを書き込みました。")
        else:
            first_row = all_vals[0]
            if first_row != headers:
                st.info("⚠️ [DEBUG] 既存ヘッダーが期待と異なります → 既存シートをクリアしてヘッダーを再作成します。")
                sheet.clear()
                sheet.append_row(headers)
                st.info("✅ ヘッダーを再作成しました。")

        # データ整形
        safe_data = [str(item) if not isinstance(item, str) else item for item in data]
        st.info(f"[DEBUG] 保存するデータ行: (列数: {len(safe_data)})")

        # append_row 実行
        try:
            sheet.append_row(safe_data)
            st.success("✅ Googleスプレッドシートにデータを保存しました！（append_row 成功）")
        except Exception as e:
            st.error(f"[ERROR] append_row() に失敗: {type(e).__name__} - {e}")
            return False

        return True

    except Exception as e:
        st.error(f"[ERROR] Googleスプレッドシート保存エラー: {type(e).__name__} - {e}")
        return False

# --- 6️⃣ バリデーション関数 ---
def is_valid_number(val: str, allow_empty: bool = True) -> bool:
    if val == "" and allow_empty:
        return True
    try:
        return int(val) >= 0
    except:
        return False

# --- 7️⃣ ポリシー同意チェック（スクロールボックス版） ---
def show_policy_and_consent() -> bool:
    # タイトルを中央寄せ
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
    ・入力内容はサービス改善・統計分析の目的で匿名化し保存します。<br>
    ・個人情報・内容は法令・ガイドラインに基づき適切に管理されます。<br>
    ・AIの学習用途（OpenAI等への品質向上・二次利用）には使用されません。<br>
    ・第三者への提供は行いません。<br>
    ・保存されたデータは必要期間終了後、速やかに削除します。<br>
    ・修正・削除の希望があればご連絡ください。<br>
    <br>
    <b>【利用規約・免責事項】</b><br>
    ・AI出力内容の正確性・完全性は保証できません。利用者自身の責任で活用してください。<br>
    ・本サービスは医療・法務・財務の専門アドバイスを代替するものではありません。<br>
    ・本サービスの利用により発生した直接・間接的な損害について、提供者は責任を負いません。<br>
    ・予告なくサービス内容が変更・中断・終了する場合があります。<br>
    <br>
    <b>【その他】</b><br>
    ・Googleスプレッドシート等に保存される際の通信は暗号化されます。<br>
    ・利用状況の把握のため、匿名のアクセスログを取得する場合があります。<br>
    ・利用規約・ポリシーは適宜改定される場合があります。改定後の内容は本画面にて掲示します。<br>
    <br>
    【最終更新日】2025年6月3日<br>
    </div>
    """
    st.markdown(policy_html, unsafe_allow_html=True)

    # チェックボックスを中央寄せするため、wrapする <div class="consent-box"> を使う
    st.markdown('<div class="consent-box">', unsafe_allow_html=True)
    checked = st.checkbox("上記の内容に同意します", key="consent_checkbox", label_visibility="visible")
    st.markdown('</div>', unsafe_allow_html=True)

    return checked

# --- 8️⃣ プラン選択UI ---
def select_plan() -> str:
    with st.sidebar:
        st.header("🛠️ プラン選択")
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
    profit   = _to_i(inp.get("営業利益", "0"))
    cash     = _to_i(inp.get("現金・預金残高", "0"))
    loan     = _to_i(inp.get("借入金合計", "0"))
    repay    = _to_i(inp.get("毎月返済額", "0")) * 12

    # 営業CF は簡易的に営業利益と同義とする
    op_cf    = max(profit, 0)

    # 新指標：営業利益率
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
    新指標（営業利益率・キャッシュ残高/月商・借入金返済負担感）を含める。
    """
    # 事前に文字列化しておく
    sales_str         = f"{fin['sales']:,} 円"
    profit_str        = f"{fin['profit']:,} 円"
    op_cf_str         = f"{fin['op_cf']:,} 円"
    profit_margin_str = f"{fin['profit_margin']:.1f}%" if fin.get("profit_margin") is not None else "–"
    cash_months_str   = f"{fin['cash_months']:.1f} ヶ月分" if fin.get("cash_months") is not None else "–"
    burden_ratio_str  = f"{fin['burden_ratio']:.1f}%" if fin.get("burden_ratio") is not None else "–"

    # エグゼクティブサマリー全体を section-card で囲む
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 エグゼクティブサマリー (ワンページ)")

    # 左：箇条書き、右：HTMLボックス
    col_info, col_boxes = st.columns([2, 3], gap="medium")

    with col_info:
        bullets = [
            f"**法人／個人区分:** {inp.get('法人／個人区分', '不明')}  \n**業種:** {inp.get('業種', '不明')}  \n**地域:** {inp.get('地域', '不明')}",
            f"**主力商品・サービス:** {inp.get('主力商品・サービス', '不明')}",
            f"**売上トレンド:** {inp.get('売上高の増減', '不明')}  \n**営業利益トレンド:** {inp.get('営業利益の増減', '不明')}",
            f"**主要顧客数トレンド:** {inp.get('主要顧客数の増減', '不明')}  \n**競合環境:** {inp.get('競合の多さ', '不明')}",
            f"**資金繰り:** {inp.get('資金繰りの状態', '不明')}  \n**借入金合計:** {fin['loan']:,} 円  \n(年返済 {fin['repay']:,} 円)",
            f"**強みキーワード:** {inp.get('自社の強み', '不明')}  \n**課題キーワード:** {inp.get('経営課題選択', '不明')}",
        ]
        for b in bullets:
            st.markdown(f"- {b}")

    with col_boxes:
        # HTMLを使って、各ボックスをフレックスで整列
        html = f"""
<div style="display: flex; flex-wrap: wrap; gap: 12px;">
  <!-- 1. 年間売上高 -->
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

  <!-- 2. 営業利益 -->
  <div style="
      flex: 1 1 45%;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 12px;
      text-align: center;
  ">
    <div style="font-size: 0.95rem; color: #555555; margin-bottom: 4px;">営業利益</div>
    <div style="font-size: 1.3rem; font-weight: 700; color: #111111;">
      {profit_str}
    </div>
  </div>

  <!-- 3. 営業利益率 -->
  <div style="
      flex: 1 1 45%;
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 12px;
      text-align: center;
  ">
    <div style="font-size: 0.95rem; color: #555555; margin-bottom: 4px;">営業利益率</div>
    <div style="font-size: 1.3rem; font-weight: 700; color: #111111;">
      {profit_margin_str}
    </div>
  </div>

  <!-- 4. キャッシュ残高 / 月商 -->
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

  <!-- 5. 借入金返済負担感 -->
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
* **営業利益率** – 売上高に対する営業利益の割合。利益性の目安。  
* **キャッシュ残高/月商** – キャッシュが営業を何ヶ月維持できるかの目安。3ヶ月以上が安心水準。  
* **返済負担感** – 年間返済額が営業利益の何％か。50％以下が無理ない水準。  
* **5フォース分析（Five Forces Analysis）** – 競争者・新規参入者・代替品・供給者・顧客の5つの力から業界構造を分析する手法。  
* **VRIO分析** – 強み(Valuable)、希少性(Rare)、模倣困難性(Inimitable)、組織活用力(Organization)の4観点で戦略案を比較し、最も競争優位につながる案を選定する手法。  
* **PL/BS/CF** – 損益計算書 / 貸借対照表 / キャッシュフロー計算書。  
""")

# --- 1️⃣3️⃣ 外部環境（PEST＋競合）取得 ---
def fetch_pest_competition(user_input: dict) -> str | None:
    query = (
        f"{user_input.get('地域', '')} {user_input.get('業種', '')} {user_input.get('主力商品・サービス', '')} "
        f"業界 {user_input.get('主な関心テーマ', user_input.get('経営課題選択', 'トレンド'))} 最新動向 PEST 競合"
    )
    prompt = (
        "あなたはトップクラスの経営コンサルタントです。\n"
        "外部環境分析（PEST＋5フォース分析＋競合分析）をA4 1～2枚分・専門家レポート並みに詳しく、日本語で出力。\n"
        "■現時点の最新Web情報を参照し、各PEST項目ごとに実例・統計・法改正・消費者動向・AI/デジタル事例まで厚く\n"
        "■5フォース分析で業界構造を分析、主要競合5社以上の特徴・最新ニュース・ベンチマーク事例を具体的に\n"
        "■必ず根拠や数値、出典を添え、参考Webリスト10件（タイトル＋URL）も示すこと\n"
        "■抽象論・一般論は禁止。必ず事実・出典・専門家の視点で。\n\n"
        f"【検索テーマ】{query}\n"
    )

    with st.spinner("Web検索＋PEST/競合AI分析中…"):
        try:
            response = client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search"}],
                input=prompt,
            )
            return response.output_text
        except Exception as e:
            st.error(f"Responses APIエラー: {e}")
            return None

# --- 1️⃣4️⃣ PDF生成（目次自動生成付き） ---
def create_pdf(text_sections: list[dict], filename: str = "AI_Dock_Report.pdf") -> io.BytesIO:
    """
    PDFを生成します。目次ページを自動挿入。
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
    elements.append(Paragraph("経営診断GPTレポート", title_style))
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
    for idx, sec in enumerate(text_sections, start=1):
        title = sec.get("title", "")
        # ページ番号は後付けのため空欄にしておく
        elements.append(Paragraph(f"{idx}. {title} ......", toc_style_item))
    elements.append(Spacer(1, 20))

    # 各セクションをPDFに追加
    for sec in text_sections:
        title = sec.get("title", "")
        text = sec.get("text", "")

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

        para_style = ParagraphStyle(
            "Body",
            fontName="IPAexGothic",
            fontSize=11,
            textColor=colors.black,
            leading=18,
            spaceAfter=8,
            leftIndent=0,
            alignment=0,
        )
        for para in text.split("\n\n"):
            para = para.strip()
            if para:
                elements.append(Paragraph(para, para_style))

        elements.append(Spacer(1, 10))

    # PDF ビルド
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
    """
    st.markdown('<div class="widecard">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1.6rem; font-weight:700; color:#111111; margin-bottom:8px;">'
        '✅ AI経営診断GPT【Lite版 v1.4-beta2_fixed】'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="info-box">'
        '★ 必須項目は「★」マーク。  \n'
        '★ 数字は半角数字・カンマ不要。  \n'
        '★ 住所は「番地まで書くと外部環境分析の精度が上がります」（任意）。  \n'
        '★ 入力は社長の感覚・主観でOKです。'
        '</div>',
        unsafe_allow_html=True,
    )

    # セッション完全リセットボタン（古いキーをすべてクリア）
    if st.button("セッション完全リセット（全初期化）"):
        st.session_state.clear()
        st.experimental_rerun()

    if st.button("⟳ 入力内容をリセットして再入力する"):
        for key in list(st.session_state.keys()):
            if key.startswith("field_") or key in ["user_input", "ai_question", "user_answer", "final_report", "text_sections", "keep_report", "pdf_buffer", "log"]:
                del st.session_state[key]
        st.rerun()

    with st.form("form1"):
        col1, col2 = st.columns(2, gap="large")

        # 前回入力をセッションから復元
        prev = st.session_state.get("user_input", {})

        # 左カラム：基本情報と売上・財務
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 基本情報")

            # 法人／個人選択
            entity_type = st.radio(
                "★法人／個人事業主の区分",
                options=["法人", "個人事業主"],
                horizontal=True,
                index=["法人", "個人事業主"].index(prev.get("法人／個人区分", "法人"))
            )
            st.session_state["field_entity_type"] = entity_type

            company_name = st.text_input(
                "★会社名（屋号でもOK）",
                value=prev.get("会社名", ""),
                placeholder="例：株式会社サンプルアパレル／〇〇工房"
            )
            st.session_state["field_company_name"] = company_name

            region = st.text_input(
                "★地域（番地まで任意）",
                value=prev.get("地域", ""),
                placeholder="例：東京都新宿区西新宿2-8-1"
            )
            st.session_state["field_region"] = region

            industry_master = [
                "製造業（食品）", "製造業（化学）", "製造業（金属）", "製造業（機械）", "製造業（その他）",
                "建設業（住宅）", "建設業（インフラ・土木）", "建設業（その他）",
                "小売業（食品）", "小売業（日用品）", "小売業（衣料品）", "小売業（その他）",
                "サービス業（医療・福祉）", "サービス業（教育）", "サービス業（IT・ソフトウェア）", "サービス業（コンサル）", "サービス業（その他）",
                "飲食業（飲食店・カフェ）", "飲食業（居酒屋・バー）", "飲食業（その他）",
                "その他（自由入力）"
            ]
            selected_industry = prev.get("業種", "製造業（食品）")
            if selected_industry not in industry_master:
                selected_industry = "その他（自由入力）"
            industry = st.selectbox(
                "★業種",
                industry_master,
                index=industry_master.index(selected_industry)
            )
            st.session_state["field_industry"] = industry

            industry_free = ""
            if industry == "その他（自由入力）":
                industry_free = st.text_input(
                    "業種（自由入力）",
                    value=prev.get("業種", "") if prev.get("業種", "") not in industry_master else "",
                    placeholder="例：エンタメ系サービス業"
                )
                st.session_state["field_industry_free"] = industry_free

            main_product = st.text_input(
                "★主力の商品・サービス",
                value=prev.get("主力商品・サービス", ""),
                placeholder="例：高級食パン／業務用厨房機器／化粧品OEM など"
            )
            st.session_state["field_main_product"] = main_product

            main_theme = st.text_input(
                "主な関心テーマ",
                value=prev.get("主な関心テーマ", ""),
                placeholder="市場動向、競合動向など"
            )
            st.session_state["field_main_theme"] = main_theme

            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 売上・財務")
            sales = st.text_input(
                "★年間売上高（円）",
                value=prev.get("年間売上高", ""),
                placeholder="90000000"
            )
            st.session_state["field_sales"] = sales

            sale_trend = st.selectbox(
                "売上高の増減",
                ["増加", "変わらない", "減少"],
                index=["増加", "変わらない", "減少"].index(prev.get("売上高の増減", "増加")) if prev.get("売上高の増減") in ["増加", "変わらない", "減少"] else 0,
                help="現在の売上高が前年と比べて増加／変わらない／減少しているかを選択してください"
            )
            st.session_state["field_sale_trend"] = sale_trend

            profit = st.text_input(
                "営業利益（円）",
                value=prev.get("営業利益", ""),
                placeholder="2000000"
            )
            st.session_state["field_profit"] = profit

            profit_trend = st.selectbox(
                "営業利益の増減",
                ["増加", "変わらない", "減少"],
                index=["増加", "変わらない", "減少"].index(prev.get("営業利益の増減", "増加")) if prev.get("営業利益の増減") in ["増加", "変わらない", "減少"] else 0,
                help="現在の営業利益が前年と比べて増加／変わらない／減少しているかを選択してください"
            )
            st.session_state["field_profit_trend"] = profit_trend

            cash = st.text_input(
                "現金・預金残高（円）",
                value=prev.get("現金・預金残高", ""),
                placeholder="5000000"
            )
            st.session_state["field_cash"] = cash

            loan_total = st.text_input(
                "借入金合計（円）",
                value=prev.get("借入金合計", ""),
                placeholder="10000000"
            )
            st.session_state["field_loan_total"] = loan_total

            monthly_repayment = st.text_input(
                "毎月返済額（円）",
                value=prev.get("毎月返済額", ""),
                placeholder="200000"
            )
            st.session_state["field_monthly_repayment"] = monthly_repayment

            st.markdown('</div>', unsafe_allow_html=True)

        # 右カラム：組織・顧客と現場ヒアリング・強み
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 組織・顧客")
            employee = st.text_input(
                "従業員数",
                value=prev.get("従業員数", ""),
                placeholder="18"
            )
            st.session_state["field_employee"] = employee

            customer_type = st.text_input(
                "主な顧客層",
                value=prev.get("主な顧客層", ""),
                placeholder="個人顧客／若年層中心"
            )
            st.session_state["field_customer_type"] = customer_type

            customer_trend = st.selectbox(
                "主要顧客数の増減",
                ["増加", "変わらない", "減少"],
                index=["増加", "変わらない", "減少"].index(prev.get("主要顧客数の増減", "増加")) if prev.get("主要顧客数の増減") in ["増加", "変わらない", "減少"] else 0,
                help="現在の主要顧客数が増加／変わらない／減少しているかを選択してください"
            )
            st.session_state["field_customer_trend"] = customer_trend

            channel = st.text_input(
                "主な販売チャネル",
                value=prev.get("主な販売チャネル", ""),
                placeholder="店舗／EC／SNS"
            )
            st.session_state["field_channel"] = channel

            competitor = st.selectbox(
                "競合の多さ",
                ["多い", "普通", "少ない"],
                index=["多い", "普通", "少ない"].index(prev.get("競合の多さ", "普通")) if prev.get("競合の多さ") in ["多い", "普通", "少ない"] else 1
            )
            st.session_state["field_competitor"] = competitor
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
                )
            )
            hearing_list = [s.strip() for s in hearing_raw.split("\n") if s.strip()]
            st.session_state["field_hearing_list"] = hearing_list

            strength = st.text_input(
                "自社の強み（主観でOK、1文）",
                value=prev.get("自社の強み", ""),
                placeholder="地元密着の接客／独自セレクト商品"
            )
            st.session_state["field_strength"] = strength

            issue_choice = st.selectbox(
                "★最も課題と感じるテーマ",
                ["資金繰り", "売上低迷", "人材確保", "新規顧客獲得", "その他"],
                index=["資金繰り", "売上低迷", "人材確保", "新規顧客獲得", "その他"].index(prev.get("経営課題選択", "資金繰り"))
            )
            st.session_state["field_issue_choice"] = issue_choice

            issue_detail = st.text_area(
                "課題の具体的な内容（1～2行でOK）",
                value=prev.get("経営課題自由記述", ""),
                height=70,
                placeholder="来店客数の減少と在庫回転の悪化"
            )
            st.session_state["field_issue_detail"] = issue_detail

            cash_status = st.selectbox(
                "資金繰りの状態",
                ["安定", "やや不安", "危機的"],
                index=["安定", "やや不安", "危機的"].index(prev.get("資金繰りの状態", "安定"))
            )
            st.session_state["field_cash_status"] = cash_status

            legal_flag = st.checkbox(
                "法律・税務・社労士領域等の専門的な悩みも入力した場合はチェック",
                value=prev.get("法務税務フラグ", False)
            )
            st.session_state["field_legal_flag"] = legal_flag

            external_env = st.text_area(
                "外部環境・市況感（例：人口減、材料高騰、業界再編等）",
                value=prev.get("外部環境肌感", ""),
                height=70,
                placeholder=(
                    "コロナ禍以降、商業施設の来場者数が減少傾向。ECサイト利用率上昇。為替変動による仕入価格上昇など。"
                )
            )
            st.session_state["field_external_env"] = external_env

            st.markdown('</div>', unsafe_allow_html=True)

        # --- バリデーション ---
        errors = []
        # 数値型チェック
        num_fields = [
            ("年間売上高", sales),
            ("営業利益", profit),
            ("借入金合計", loan_total),
            ("毎月返済額", monthly_repayment),
            ("現金・預金残高", cash),
            ("従業員数", employee),
        ]
        for label, val in num_fields:
            if val and not is_valid_number(val):
                errors.append(f"「{label}」は0以上の半角数字のみ入力してください。")

        # 業種
        industry_value = industry_free if industry == "その他（自由入力）" else industry

        # 必須項目チェック
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

        # --- Submitボタン ---
        submit = st.form_submit_button("▶ 一次入力を送信し、AIの追加質問を受ける")
        if errors and submit:
            st.markdown('<div class="err-box">' + "<br>".join(errors) + '</div>', unsafe_allow_html=True)
            return

        # --- Submit成功時 ---
        if submit:
            # 地域マスキング（市区町村まで）
            masked_region = region.split(" ")[0] if " " in region else region

            # 会社名マスキングは先頭2文字＋残り全て＊
            masked_company = (company_name[:2] + "＊" * (len(company_name) - 2)) if company_name else ""

            save_row = [
                entity_type,
                masked_company,
                masked_region,
                industry_value,
                main_product,
                sales,
                sale_trend,
                profit,
                profit_trend,
                loan_total,
                monthly_repayment,
                cash,
                employee,
                customer_type,
                customer_trend,
                channel,
                competitor,
                issue_choice,
                issue_detail,
                strength,
                cash_status,
                ";".join(hearing_list),
                external_env,
                plan,
                str(legal_flag),
                main_theme,
            ]
            save_to_gsheet(save_row)

            st.session_state.user_input = {
                "法人／個人区分": entity_type,
                "会社名": company_name,
                "地域": region,
                "業種": industry_value,
                "主力商品・サービス": main_product,
                "主な関心テーマ": main_theme,
                "年間売上高": sales,
                "売上高の増減": sale_trend,
                "営業利益": profit,
                "営業利益の増減": profit_trend,
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
            # ログにプロンプトと質問
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
        )
        submit2 = st.form_submit_button("▶ 経営診断レポートの生成")

    # ＜ 戻る ボタン（中央寄せ）＞
    st.markdown('<div class="center-button">', unsafe_allow_html=True)
    back_col1, back_col2, back_col3 = st.columns([1, 1, 1])
    with back_col2:
        if st.button("← 戻る"):
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
    進捗バー＆ログ記録対応。
    """
    st.markdown('<div class="widecard">', unsafe_allow_html=True)
    st.subheader("📝 経営診断GPTレポート")

    # 財務指標を計算
    fin = calc_finance_metrics(st.session_state.user_input)

    # タブで EXEC SUMMARY／詳細レポート／用語辞典 を切り替え
    tab_exec, tab_report, tab_gloss = st.tabs(["EXEC SUMMARY", "詳細レポート", "用語辞典"])

    with tab_exec:
        render_exec_summary(st.session_state.user_input, fin)

    with tab_gloss:
        render_glossary()

    with tab_report:
        # 既に生成済みなら再利用（セッション内）
        if "final_report" not in st.session_state or not st.session_state.get("keep_report", False):
            st.info("AI診断レポート生成中… 進捗状況を表示します。")
            progress = st.progress(0)

            user_input  = st.session_state.user_input
            ai_question = st.session_state.ai_question
            user_answer = st.session_state.user_answer

            # 外部環境（PEST＋競合）をAI＋Web検索で取得
            with st.spinner("外部環境データ取得中…"):
                external_env_text = fetch_pest_competition(user_input) or "（外部環境分析取得エラー）"
            progress.progress(20)

            # レポート作成プロンプト組立
            def make_prompt() -> str:
                return f"""
あなたは超一流の戦略系経営コンサルタントです。
以下の順で、現場合意・納得感を重視した診断レポートをA4一枚分で作成してください。

1. 外部環境分析（PEST・5フォース分析・競合分析：前述のWEB調査内容を厚く）
2. 内部環境分析（現場ヒアリング等の入力を厚く、AI推測厳禁）
3. 経営サマリー（現状数字・主な課題。ユーザー未入力項目は「不明」記載、AI推測絶対厳禁）
4. 真因分析（KPI悪化の本当の原因。AI推測厳禁）
5. 戦略アイディア（必ず4つ。クロスSWOT S×O中心、根拠明示。投資額・効果・回収月数も記載すること）
6. VRIO分析（4案をV/R/I/Oで比較表＆要約。**必ず '最もスコア高い案: ○○○' を書くこと。PDFでは最終案のみ強調**）
7. 実行計画（最適案についてKPI・担当・期限・リスク・最初の一歩を5W1Hで）
8. 次回モニタリング・PDCA設計
9. 参考データ・URL

【必須条件】
・数字、現場エピソード、根拠を重視
・施策や分析は抽象論禁止。ユーザー入力・外部データのみ
・未入力の数値・比率は「不明」「未入力」等で事実ベース
・VRIO表や点数化も可能な範囲で盛り込む
・最終案の「なぜこれか？」「なぜ他案はダメか？」まで必ず論理で

【法人／個人区分】:
{user_input.get("法人／個人区分", "不明")}

【地域】:
{user_input.get("地域", "不明")}

【業種】:
{user_input.get("業種", "不明")}

【主力商品・サービス】:
{user_input.get("主力商品・サービス", "不明")}

【財務指標】:
- 年間売上高: {fin['sales']:,} 円
- 営業利益: {fin['profit']:,} 円
- 営業CF (簡易): {fin['op_cf']:,} 円
- 営業利益率: {fin['profit_margin']:.1f}%
- キャッシュ残高/月商: {fin['cash_months']:.1f} ヶ月分
- 借入金合計: {fin['loan']:,} 円
- 年間返済額: {fin['repay']:,} 円
- 返済負担感: {fin['burden_ratio']:.1f}%

【ユーザー情報】:
{user_input}

【AI深掘り質問＋ユーザー回答】:
{ai_question}
{user_answer}

【外部環境（PEST・競合・Web情報）】:
{external_env_text}
"""

            # 1回目のレポート生成
            try:
                main_prompt = make_prompt()
                # ログにプロンプト
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
                # ログにAIレスポンス
                st.session_state.log.append({
                    "stage": "report_generation_response_initial",
                    "response": first_report
                })
                progress.progress(50)

                # ダブルチェック＆修正プロンプト
                double_prompt = f"""
あなたはプロの経営コンサルタントです。
以下のレポート初稿を厳しくダブルチェックし、
不足箇所・根拠不足・抽象論・未入力数値のAI推測はすべて排除し加筆修正してください。
必ず構成順・数字／現場／論理根拠・合意形成を重視。
【レポート初稿】
{first_report}
"""
                # ログにダブルチェックプロンプト
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
                # ログにダブルチェックAIレスポンス
                st.session_state.log.append({
                    "stage": "double_check_response",
                    "response": final_report
                })
                progress.progress(80)

                # セクション分割とVRIO部分フィルタリング
                section_titles = [
                    ("外部環境分析", r"1[\.．] ?外部環境分析"),
                    ("内部環境分析", r"2[\.．] ?内部環境分析"),
                    ("経営サマリー", r"3[\.．] ?経営サマリー"),
                    ("真因分析", r"4[\.．] ?真因分析"),
                    ("戦略アイディア", r"5[\.．] ?戦略アイディア"),
                    ("VRIO分析", r"6[\.．] ?VRIO分析"),
                    ("実行計画", r"7[\.．] ?実行計画"),
                    ("次回モニタリング・PDCA設計", r"8[\.．] ?次回モニタリング・PDCA設計"),
                    ("参考データ・URL", r"9[\.．] ?参考データ・URL"),
                ]
                text_sections = []
                for i, (title, pattern) in enumerate(section_titles):
                    match = re.search(pattern, final_report)
                    if match:
                        start = match.end()
                        if i + 1 < len(section_titles):
                            next_pattern = section_titles[i + 1][1]
                            end_match = re.search(next_pattern, final_report[start:])
                            end_idx = start + end_match.start() if end_match else len(final_report)
                        else:
                            end_idx = len(final_report)
                        section_text = final_report[start:end_idx].strip()

                        # VRIO分析セクションだけ「最もスコア高い案」抽出
                        if title == "VRIO分析":
                            lines = section_text.splitlines()
                            highest_line = None
                            for ln in lines:
                                if "最もスコア高い案" in ln or "最もスコアが高い案" in ln:
                                    highest_line = ln.strip()
                                    break
                            if highest_line:
                                section_text = f"**VRIO分析（最終案）**\n\n- {highest_line}\n\n\n" + "\n".join(lines)
                            else:
                                section_text = "**VRIO分析（全文）**\n\n" + "\n".join(lines)

                        text_sections.append({
                            "title": title,
                            "text": section_text,
                        })

                # セッションに保存
                st.session_state["final_report"]  = final_report
                st.session_state["text_sections"] = text_sections
                st.session_state["keep_report"]   = True
                progress.progress(100)

            except Exception as e:
                st.error(f"AIエラー内容: {e}")
                st.stop()

        # --- レポート本文を表示 ---
        st.markdown(st.session_state["final_report"].replace("\n", "  \n"))
        st.markdown("---\n#### 入力内容の再編集・再生成")
        if st.button("入力内容を再編集して診断をやり直す"):
            # 再編集時は step=1 に戻す
            st.session_state.step        = 1
            st.session_state.keep_report = False
            st.rerun()

        # --- PDF生成・ダウンロード用バッファを保持 ---
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
        st.markdown("---\n#### 入力データのエクスポート")
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

    # --- ★ 戻るボタンは Tabs の後ろに置く ★ ---
    st.markdown('<div class="center-button">', unsafe_allow_html=True)
    back_col1, back_col2, back_col3 = st.columns([1, 1, 1])
    with back_col2:
        if st.button("← 戻る"):
            st.session_state.step = 2
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- 2️⃣0️⃣ メイン実行部 ---
def main() -> None:
    font_path = check_font()
    if "step" not in st.session_state:
        st.session_state.step = 1

    # --- ポリシー同意チェック ---
    consent = show_policy_and_consent()
    if not consent:
        st.warning("ご利用には同意が必要です。")
        return

    # --- プラン選択 ---
    plan = select_plan()

    # Starter/Pro は準備中案内で止める
    if plan.startswith("Starter"):
        st.info("「Starter（右腕・API連携）」プランは現在準備中です。しばらくお待ちください。")
        return
    if plan.startswith("Pro"):
        st.info("「Pro（参謀・戦略実行支援）」プランは現在準備中です。しばらくお待ちください。")
        return

    # --- 現在のステップに応じて画面を切り替え ---
    step = st.session_state.get("step", 1)

    if step == 1:
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
