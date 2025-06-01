# -*- coding: utf-8 -*-
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

APP_TITLE = "AI経営診断GPT"
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

# --- CSSバリデーション赤枠・フォームUI修正版 ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet">
<style>
/* 入力フォーム赤枠バリデーション完全消去 */
input:invalid, textarea:invalid,
.stTextInput > div > input:invalid,
.stTextArea textarea:invalid {
    border: 1.5px solid #d4e3ef !important;
    box-shadow: none !important;
    outline: none !important;
    background: #f7fafc !important;
    color: #192642 !important;
}
input:focus:invalid, textarea:focus:invalid,
.stTextInput > div > input:focus:invalid,
.stTextArea textarea:focus:invalid {
    border: 2px solid #4085ef !important;
    box-shadow: 0 3px 12px rgba(54,90,220,0.08) !important;
    outline: none !important;
    background: #f7fafc !important;
}
.stTextInput > div > input, .stTextArea textarea {
    border: 1.5px solid #d4e3ef !important;
    border-radius: 12px !important;
    background: #f7fafc !important;
    box-shadow: none !important;
    outline: none !important;
}
.stTextInput > div > input:focus, .stTextArea textarea:focus {
    border: 2px solid #4085ef !important;
    box-shadow: 0 3px 12px rgba(54,90,220,0.08) !important;
    outline: none !important;
    background: #f7fafc !important;
}
/* 下記を追加：input/textareaのタイプ・擬似要素まで全て明示的に消す！ */
input:invalid:required, textarea:invalid:required {
    background: #f7fafc !important;
    border: 1.5px solid #d4e3ef !important;
    box-shadow: none !important;
}
input:focus:invalid:required, textarea:focus:invalid:required {
    background: #f7fafc !important;
    border: 2px solid #4085ef !important;
    box-shadow: 0 3px 12px rgba(54,90,220,0.08) !important;
}
/* iOS/Safari等で自動追加される「:-webkit-autofill」も明示的に消す */
input:-webkit-autofill,
textarea:-webkit-autofill {
    -webkit-box-shadow: 0 0 0 1000px #f7fafc inset !important;
    box-shadow: 0 0 0 1000px #f7fafc inset !important;
    background: #f7fafc !important;
}
/* その他デザイン */
body, .stApp { font-family: 'Inter', 'Noto Sans JP', sans-serif !important; background: #f5f7fa;}
h1, h2, h3, .stMarkdown h1 { font-family: 'Inter', 'Noto Sans JP', sans-serif !important; color: #192642; font-weight: 800; margin-bottom: 16px;}
.widecard { background: #fff; border-radius: 20px; box-shadow: 0 4px 20px rgba(40,60,130,0.1); padding: 32px 28px 26px 28px; margin: 24px auto; max-width: 1200px; min-width: 700px;}
@media (max-width: 1100px) {.widecard { padding: 16px 3vw; min-width: 320px; } }
.section-card { background: #fafdff; border-radius: 14px; box-shadow: 0 1px 8px rgba(80,130,220,0.04); padding: 18px 14px 12px 14px; margin-bottom: 14px;}
.stSidebar { background: #f7faff !important; border-radius: 14px;}
.stButton > button { font-size: 1.13em !important; font-family: 'Inter', 'Noto Sans JP', sans-serif !important; padding: 0.9em 2.3em !important; border-radius: 12px !important; background: linear-gradient(90deg, #2166d1 0%, #68d0f7 100%); color: #fff !important; font-weight: 700; border: none; box-shadow: 0 2px 10px rgba(50,90,200,0.12); margin-bottom: 12px; transition: 0.13s;}
.stButton > button:hover { background: linear-gradient(90deg, #163b77 0%, #2465e2 90%) !important; transform: translateY(-1px) scale(1.02);}
label, .stTextInput label, .stSelectbox label { font-size: 1.05em; font-weight: 700; color: #25518c; margin-bottom: 4px; letter-spacing: 0.01em;}
.stCheckbox > label { font-size: 1.02em; padding-left: 6px;}
.info-box { background: linear-gradient(90deg,#e7f4ff 75%, #ecf7fc 100%); border-left: 6px solid #2196f3; color: #173763; padding: 12px 14px 10px 16px; font-size: 1.05em; border-radius: 10px; margin-bottom: 14px; font-family: 'Inter', 'Noto Sans JP', sans-serif !important;}
.warn-box { background: linear-gradient(90deg,#fff3d3 60%, #ffe9c5 100%); border-left: 6px solid #ffae42; color: #784102; padding: 11px 14px 9px 16px; font-size: 1.03em; border-radius: 10px; margin-bottom: 12px; font-family: 'Inter', 'Noto Sans JP', sans-serif !important;}
.err-box { background: linear-gradient(90deg,#ffeaea 70%, #ffe5e5 100%); border-left: 6px solid #e02a2a; color: #891717; padding: 12px 14px 10px 16px; font-size: 1.03em; border-radius: 10px; margin-bottom: 12px; font-family: 'Inter', 'Noto Sans JP', sans-serif !important;}
[data-testid="stAppViewContainer"][class*="dark"] .widecard { background: #232839; }
[data-testid="stAppViewContainer"][class*="dark"] .section-card { background: #232738; }
[data-testid="stAppViewContainer"][class*="dark"] .info-box { background: linear-gradient(90deg,#293955 70%,#2a4775 100%); color: #fff; border-left: 6px solid #49a9ff; }
[data-testid="stAppViewContainer"][class*="dark"] .warn-box { background: linear-gradient(90deg,#6e4b13 60%,#ab872c 100%); color: #ffe; }
[data-testid="stAppViewContainer"][class*="dark"] .err-box { background: linear-gradient(90deg,#63333d 70%,#8a2f2e 100%); color: #ffe; }
</style>
""", unsafe_allow_html=True)

# ==== 3. ロジック・関数（以降は前回と同じですが、「矢印削除」に注意）====

def is_dark_mode() -> bool:
    try:
        return st.get_option("theme.base") == "dark"
    except:
        return False

api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
client = OpenAI(api_key=api_key) if api_key else None

def check_font() -> str:
    font_path = "ipag.ttf"
    if not os.path.exists(font_path):
        st.warning(
            "PDF日本語出力には 'ipag.ttf' フォントが必要です。\n"
            "以下のリンクからダウンロードして、この Streamlit アプリと同じフォルダに配置してください。\n"
            "https://ipafont.ipa.go.jp/node26#jp"
        )
    return font_path

def show_policy_and_consent() -> bool:
    st.markdown(
        """
<div class="info-box">
<b>■ 情報の取扱い・プライバシー・AI学習未利用について</b><br>
・入力内容はサービス改善・統計分析の目的で匿名化し保存。個人情報・内容は法令・指針を厳守して管理します。<br>
・<b>AIの学習用途（OpenAI等への品質向上・二次利用）には一切使われません</b>。送信時も「学習利用不可」の設定を適用。<br>
・本人特定や営業連絡など管理者側の用途には利用しません。<br>
・入力情報は必要期間終了後、速やかに削除されます。修正・削除はご連絡で対応。<br>
・Googleスプレッドシート等外部保存時も通信は暗号化。<br>
<br>
<b>■ 利用規約・注意点（抜粋）</b><br>
・本サービスは経営判断・現場改善の参考情報を提供するものであり、最終意思決定・施策実行はご自身の判断・責任で行ってください。<br>
・AIの特性上、出力内容の正確性・完全性・最新性は保証できません。<br>
・運営者は本サービス利用・レポート内容等による損害に責任を負いません。<br>
・法令・公序良俗違反は厳禁です。規約・方針は予告なく変更される場合があります。<br>
</div>
""",
        unsafe_allow_html=True,
    )
    return st.checkbox("上記内容に同意します", value=False)

def select_plan() -> str:
    with st.sidebar:
        st.header("🛠️ プラン選択")
        st.markdown(
            """
| プラン名            | サービス内容                                     | 月額（税込）  |
|------------------|-----------------------------------------------|--------------|
| Lite（経営診断医）      | AI現場診断・PDF出力                              | 無料          |
| Starter（右腕）       | 財務10指標＋API連携・月次ベンチマーク・実行サポ | 15,000円      |
| Pro（参謀）           | 決算3期比較・KPI設計・実行支援・個別相談         | 30,000円      |
"""
        )
        plan = st.radio(
            "ご希望のサービスプランをお選びください",
            [
                "Lite（AI経営診断GPT・無料）",
                "Starter（右腕・API連携）準備中",
                "Pro（参謀・戦略実行支援）準備中",
            ],
        )
        return plan
def save_to_gsheet(data: list) -> bool:
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = {
            "type": st.secrets["google"]["type"],
            "project_id": st.secrets["google"]["project_id"],
            "private_key_id": st.secrets["google"]["private_key_id"],
            "private_key": st.secrets["google"]["private_key"],
            "client_email": st.secrets["google"]["client_email"],
            "client_id": st.secrets["google"]["client_id"],
            "auth_uri": st.secrets["google"]["auth_uri"],
            "token_uri": st.secrets["google"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["google"]["client_x509_cert_url"],
        }
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials, scope)
        client_gs = gspread.authorize(creds)
        sheet = client_gs.open("AI_Dock_Logs").sheet1
        sheet.append_row(data)
        return True
    except Exception as e:
        st.error(f"Googleスプレッドシート保存エラー: {e}")
        return False

def is_valid_number(val: str, allow_empty: bool = True) -> bool:
    if val == "" and allow_empty:
        return True
    try:
        return int(val) >= 0
    except:
        return False

def calc_finance_metrics(inp: dict) -> dict:
    def _to_i(v: str) -> int:
        try:
            return int(v)
        except:
            return 0
    sales   = _to_i(inp.get("年間売上高", "0"))
    profit  = _to_i(inp.get("営業利益", "0"))
    cash    = _to_i(inp.get("現金・預金残高", "0"))
    loan    = _to_i(inp.get("借入金合計", "0"))
    repay   = _to_i(inp.get("毎月返済額", "0")) * 12
    op_cf    = max(profit, 0)
    dscr     = (op_cf / repay) if repay else None
    ffo_debt = ((op_cf + cash) / loan) if loan else None
    return {
        "sales": sales,
        "profit": profit,
        "cash": cash,
        "loan": loan,
        "repay": repay,
        "op_cf": op_cf,
        "dscr": dscr,
        "ffo_debt": ffo_debt,
    }

def render_exec_summary(inp: dict, fin: dict) -> None:
    st.subheader("🚀 エグゼクティブサマリー (ワンページ)")
    bullets = [
        f"**業種:** {inp['業種']} / **地域:** {inp['地域']}",
        f"**売上トレンド:** {inp['売上高の増減']} / **営業利益トレンド:** {inp['営業利益の増減']}",
        f"**主要顧客数トレンド:** {inp['主要顧客数の増減']} / **競合環境:** {inp['競合の多さ']}",
        f"**資金繰り:** {inp['資金繰りの状態']} / **借入金合計:** {fin['loan']:,} 円 (年返済 {fin['repay']:,} 円)",
        f"**強みキーワード:** {inp['自社の強み']} / **課題キーワード:** {inp['経営課題選択']}",
    ]
    st.markdown("\n".join([f"- {b}" for b in bullets]))

    cols = st.columns(5)
    cols[0].metric(
        label="年間売上高",
        value=f"{fin['sales']:,} 円"
    )
    cols[1].metric(
        label="営業利益",
        value=f"{fin['profit']:,} 円"
    )
    cols[2].metric(
        label="営業CF",
        value=f"{fin['op_cf']:,} 円"
    )
    cols[3].metric(
        label="DSCR",
        value=f"{fin['dscr']:.2f}" if fin["dscr"] else "–"
    )
    cols[4].metric(
        label="FFO/借入金",
        value=f"{fin['ffo_debt']:.2f}" if fin["ffo_debt"] else "–"
    )

def render_glossary() -> None:
    with st.expander("📖 用語ミニ辞典"):
        st.markdown(
            """
* **DSCR (Debt Service Coverage Ratio)** – 元利返済余力。1.2 以上が目安。
* **FFO/借入金** – キャッシュ創出力と負債のバランス。
* **NPV (Net Present Value)** – 投資案ごとの正味現在価値。
* **IRR (Internal Rate of Return)** – 投下資本利益率。
* **クロスSWOT** – 強み × 機会 を掛け合わせた戦略発想手法。
* **PL/BS/CF** – 損益計算書 / 貸借対照表 / キャッシュフロー計算書。
            """
        )

def input_form(plan: str) -> None:
    """
    ステップ1：ユーザーが会社情報・財務情報・ヒアリング情報を入力するフォーム。
    """
    st.markdown('<div class="widecard">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:1.7rem;font-weight:900;color:#174275;margin-bottom:8px;">'
        '✅ AI経営診断GPT【β版】'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="info-box">'
        '入力は社長の感覚・主観でOK。必須は★付き。数字は半角・カンマ不要、'
        '分からない数字は空欄でOK。'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button("⟳ 入力内容をリセットして再入力する"):
        st.session_state.clear()
        st.rerun()

    with st.form("form1"):
        col1, col2 = st.columns(2, gap="large")

        # 左カラム：基本情報と売上・財務
        with col1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 基本情報")
            company_name = st.text_input("★会社名", placeholder="例：株式会社サンプルアパレル")
            region       = st.text_input("★地域",   placeholder="例：東京都新宿区")
            industry     = st.selectbox("★業種",   ["製造業", "小売業", "建設業", "サービス業", "飲食業", "その他"])
            main_theme   = st.text_input("主な関心テーマ", placeholder="市場動向、競合動向など")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 売上・財務")
            sales              = st.text_input("★年間売上高（円）", placeholder="90000000")
            sale_trend         = st.selectbox(
                                    "売上高の増減",
                                    ["増加", "変わらない", "減少"],
                                    help="現在の売上高が前年と比べて増加／変わらない／減少しているかを選択してください"
                                )
            profit             = st.text_input("営業利益（円）", placeholder="2000000")
            profit_trend       = st.selectbox(
                                    "営業利益の増減",
                                    ["増加", "変わらない", "減少"],
                                    help="現在の営業利益が前年と比べて増加／変わらない／減少しているかを選択してください"
                                )
            cash               = st.text_input("現金・預金残高（円）", placeholder="5000000")
            loan_total         = st.text_input("借入金合計（円）", placeholder="10000000")
            monthly_repayment  = st.text_input("毎月返済額（円）", placeholder="200000")
            st.markdown('</div>', unsafe_allow_html=True)

        # 右カラム：組織・顧客と現場ヒアリング・強み
        with col2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 組織・顧客")
            employee       = st.text_input("従業員数", placeholder="18")
            customer_type  = st.text_input("主な顧客層", placeholder="個人顧客／若年層中心")
            customer_trend = st.selectbox(
                                "主要顧客数の増減",
                                ["増加", "変わらない", "減少"],
                                help="現在の主要顧客数が増加／変わらない／減少しているかを選択してください"
                             )
            channel    = st.text_input("主な販売チャネル", placeholder="店舗／EC／SNS")
            competitor = st.selectbox("競合の多さ", ["多い", "普通", "少ない"])
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("#### 現場ヒアリング・強み")
            hearing_raw = st.text_area(
                "★現場・営業・顧客などの“生の声”や現場所見（1～3行、肌感でOK）",
                placeholder=(
                    "例：販売スタッフ「来店客数が前年同月比で15%減少しています。"
                    "特に平日の午後はほとんど動きがありません。」"
                ),
                height=110,
            )
            hearing_list = [s.strip() for s in hearing_raw.split("\n") if s.strip()]
            strength     = st.text_input("自社の強み（主観でOK、1文）", placeholder="地元密着の接客／独自セレクト商品")
            issue_choice = st.selectbox(
                               "★最も課題と感じるテーマ",
                               ["資金繰り", "売上低迷", "人材確保", "新規顧客獲得", "その他"],
                           )
            issue_detail = st.text_area(
                               "課題の具体的な内容（1～2行でOK）",
                               placeholder="来店客数の減少と在庫回転の悪化",
                               height=70,
                           )
            cash_status  = st.selectbox("資金繰りの状態", ["安定", "やや不安", "危機的"])
            legal_flag   = st.checkbox("法律・税務・社労士領域等の専門的な悩みも入力した場合はチェック")
            external_env = st.text_area(
                               "外部環境・市況感（例：人口減、材料高騰、業界再編等）",
                               placeholder=(
                                   "コロナ禍以降、商業施設の来場者数が減少傾向。"
                                   "ECサイト利用率上昇。為替変動による仕入価格上昇など。"
                               ),
                               height=70,
                           )
            st.markdown('</div>', unsafe_allow_html=True)

        # バリデーション
        errors = []
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
        for key, val in [
            ("会社名", company_name),
            ("地域", region),
            ("業種", industry),
            ("主な販売チャネル", channel),
            ("最も課題と感じるテーマ", issue_choice),
        ]:
            if not val:
                errors.append(f"{key}は必須です")
        if not hearing_list:
            errors.append("現場・営業・顧客などの“生の声”を1つ以上入力してください")
        if not issue_detail.strip():
            errors.append("課題の具体的な内容は必須です")

        submit = st.form_submit_button("▶ 一次入力を送信し、AIの追加質問を受ける")
        if errors and submit:
            st.markdown(
                '<div class="err-box">' + "<br>".join(errors) + '</div>',
                unsafe_allow_html=True,
            )
            return

        if submit:
            # Google スプレッド保存用の行データ
            save_row = [
                (company_name[:2] + "＊" * (len(company_name) - 2)) if company_name else "",
                region,
                industry,
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

            # セッションにユーザー入力を保存
            st.session_state.user_input = {
                "会社名": company_name,
                "地域": region,
                "業種": industry,
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
            st.session_state.step = 2
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def show_vrio_table_web(df: pd.DataFrame) -> None:
    """
    VRIO分析テーブルをWeb上で表示（AgGrid or HTMLフォールバック）。
    """
    try:
        from st_aggrid import AgGrid, GridOptionsBuilder

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_default_column(wrapText=True, autoHeight=True)
        gb.configure_column(
            df.columns[0],
            width=260,
            cellStyle={"fontWeight": "bold", "color": "#245BA6", "backgroundColor": "#F0E6DD"},
        )
        gb.configure_grid_options(domLayout="autoHeight")
        gb.configure_grid_options(rowStyle={"backgroundColor": "#f6f7fa"})
        grid_options = gb.build()
        AgGrid(
            df,
            gridOptions=grid_options,
            fit_columns_on_grid_load=True,
            theme="blue",
            height=240,
            enable_enterprise_modules=False,
        )
    except:
        styled = df.style.set_properties(
            **{
                "background-color": "#fff",
                "color": "#1B264F",
                "border": "1px solid #CCC",
                "font-size": "15px",
            }
        ).set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#245BA6"),
                        ("color", "white"),
                        ("font-size", "16px"),
                        ("border", "1px solid #245BA6"),
                    ],
                }
            ]
        ).hide(axis="index")
        st.markdown(styled.to_html(escape=False), unsafe_allow_html=True)

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
        except Exception as e:
            st.error(f"AIエラー: {e}")
            st.stop()

    st.markdown("### AIからの質問")
    st.markdown(ai_question)

    with st.form("form2"):
        user_answer = st.text_area(
            "上記のAI質問へのご回答を自由にご記入ください（実名・役職・頻度・金額・根拠・失敗経験もできるだけ具体的に）",
            height=150,
        )
        submit2 = st.form_submit_button("▶ 回答して外部環境調査を実行")

    if submit2:
        st.session_state.user_answer = user_answer
        st.session_state.step = 3
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def fetch_pest_competition(user_input: dict) -> str | None:
    """
    AI＋Web検索ツールでPESTと競合分析を取得する（Responses API使用例）。
    取得結果を生の文字列として返す。
    """
    query = (
        f"{user_input['地域']} {user_input['業種']} 業界 "
        f"{user_input.get('主な関心テーマ', user_input.get('経営課題選択', 'トレンド'))} "
        "最新動向 PEST 競合"
    )
    prompt = (
        "あなたはトップクラスの経営コンサルタントです。\n"
        "外部環境分析（PEST＋競合）をA4 1～2枚分・専門家レポート並みに詳しく、日本語で出力。\n"
        "■現時点の最新Web情報を参照し、各PEST項目ごとに実例・統計・法改正・消費者動向・AI/デジタル事例まで厚く\n"
        "■競合分析は主な競合5社以上・特徴・最新ニュース・ベンチマーク事例を具体的に\n"
        "■必ず根拠や数値、出典を添え、参考Webリスト10件（タイトル＋URL）も示すこと\n"
        "■抽象論・一般論は禁止。必ず事実・出典・専門家の視点で。\n"
        f"【検索テーマ】{query}\n\n"
        "【出力例】\n"
        "■PEST分析：\n"
        "- Politics（政治・法規制）：\n"
        "- Economy（経済・景気・物価）：\n"
        "- Society（社会・消費者）：\n"
        "- Technology（技術・DX・AI等）：\n"
        "\n■競合分析：\n"
        "- 業界主要プレーヤー・特徴・差別化軸・直近動向\n"
        "\n■主要な参考Web情報リスト（10件以上・タイトル＋URL）\n"
        "■十分な情報が得られない場合は「追加調査必要」と明記\n"
    )

    with st.spinner("Web検索＋PEST/競合AI分析中（高ボリュームで取得）…"):
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

def create_pdf(text_sections: list[dict], filename: str = "AI_Dock_Report.pdf") -> io.BytesIO:
    """
    ReportLab で日本語PDFを生成する。
    text_sections は各セクションの { "title": セクション名, "text": 本文 } のリスト。
    """
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont("IPAexGothic", "ipag.ttf"))
    styles   = getSampleStyleSheet()
    elements = []

    # タイトルセクション
    title_style = ParagraphStyle(
        "Title",
        fontName="IPAexGothic",
        fontSize=22,
        textColor=colors.white,
        alignment=1,
        spaceAfter=12,
        backColor=colors.HexColor("#1B264F"),
        leading=30,
        borderPadding=4,
    )
    elements.append(Paragraph("経営診断GPTレポート", title_style))
    elements.append(Spacer(1, 16))

    for sec in text_sections:
        title = sec.get("title", "")
        text  = sec.get("text", "")

        # VRIO分析 のときはテーブル化せず本文のみを出力
        if title == "VRIO分析":
            if title:
                section_style = ParagraphStyle(
                    "Section",
                    fontName="IPAexGothic",
                    fontSize=16,
                    textColor=colors.HexColor("#1B264F"),
                    spaceBefore=20,
                    spaceAfter=10,
                    leading=24,
                    leftIndent=0,
                    alignment=0,
                )
                elements.append(Paragraph(title, section_style))

            plain_text = re.sub(r"\|.+\|.+\|", "", text, flags=re.DOTALL).strip()
            para_style = ParagraphStyle(
                "Body",
                fontName="IPAexGothic",
                fontSize=11,
                textColor=colors.black,
                leading=18,
                spaceAfter=7,
                leftIndent=0,
                alignment=0,
            )
            for para in plain_text.split("\n\n"):
                p = para.strip()
                if p:
                    elements.append(Paragraph(p, para_style))
            elements.append(Spacer(1, 12))
            continue

        # 「最もスコアが高い戦略案」部分をハイライト
        if "最もスコアが高い戦略案" in text:
            highlight_style = ParagraphStyle(
                "High",
                fontName="IPAexGothic",
                fontSize=16,
                textColor=colors.HexColor("#D62E1B"),
                backColor=colors.HexColor("#FFF5EA"),
                leftIndent=0,
                rightIndent=0,
                spaceAfter=10,
                leading=24,
                borderPadding=7,
                borderWidth=1,
                borderColor=colors.HexColor("#D62E1B"),
            )
            pattern = r"(最もスコアが高い戦略案.+?理由.+?他案が劣る理由.+)"
            for m in re.finditer(pattern, text, flags=re.DOTALL):
                elements.append(Paragraph(m.group(1), highlight_style))
                text = text.replace(m.group(1), "")

        # セクションタイトル
        if title:
            section_style = ParagraphStyle(
                "Section",
                fontName="IPAexGothic",
                fontSize=16,
                textColor=colors.HexColor("#1B264F"),
                spaceBefore=20,
                spaceAfter=10,
                leading=24,
                leftIndent=0,
                alignment=0,
            )
            elements.append(Paragraph(title, section_style))

        # 本文パラグラフ
        para_style = ParagraphStyle(
            "Body",
            fontName="IPAexGothic",
            fontSize=11,
            textColor=colors.black,
            leading=18,
            spaceAfter=7,
            leftIndent=0,
            alignment=0,
        )
        for para in text.split("\n\n"):
            para = para.strip()
            if para:
                elements.append(Paragraph(para, para_style))

        elements.append(Spacer(1, 12))

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

def export_to_csv() -> bytes | None:
    """
    入力データを CSV としてエクスポートする。
    """
    user_input = st.session_state.get("user_input", None)
    if not user_input:
        st.warning("エクスポートできる入力データがありません。")
        return None
    df = pd.DataFrame([user_input])
    return df.to_csv(index=False).encode("utf-8-sig")

def export_to_excel() -> bytes | None:
    """
    入力データを Excel（.xlsx）としてエクスポートする。
    xlsxwriter パッケージが必要。
    """
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

def generate_report(font_path: str) -> None:
    """
    ステップ3：AIを使って最終診断レポートを生成し、PDF/CSV/Excel出力をまとめる。
    """
    st.markdown('<div class="widecard">', unsafe_allow_html=True)
    st.subheader("📝 経営診断GPTレポート")

    # 財務指標を計算
    fin = calc_finance_metrics(st.session_state.user_input)

    # タブで「EXEC SUMMARY」「詳細レポート」「用語辞典」を切り替え
    tab_exec, tab_report, tab_gloss = st.tabs(["EXEC SUMMARY", "詳細レポート", "用語辞典"])
    with tab_exec:
        render_exec_summary(st.session_state.user_input, fin)
    with tab_gloss:
        render_glossary()

    with tab_report:
        # 既に生成済みか、かつレポートを保持するフラグが有効な場合はそのまま表示
        if "final_report" not in st.session_state or not st.session_state.get("keep_report", False):
            st.info("AI診断レポート生成中…10〜20秒ほどお待ちください。")
            with st.spinner("生成中…"):
                user_input  = st.session_state.user_input
                ai_question = st.session_state.ai_question
                user_answer = st.session_state.user_answer

                # 外部環境（PEST+競合）をAI+Web検索で取得
                external_env_text = fetch_pest_competition(user_input) or "（外部環境分析取得エラー）"

                def make_prompt() -> str:
                    return f"""
あなたは超一流の戦略系経営コンサルタントです。
以下の順で、現場合意・納得感を重視した診断レポートをA4一枚分で作成してください。

1. 外部環境分析（PEST・競合分析：前述のWEB調査内容を厚く）
2. 内部環境分析（現場ヒアリング等の入力を厚く）
3. 経営サマリー（現状数字・主な課題。ユーザー未入力項目は「不明」記載、AI推測厳禁）
4. 真因分析（KPI悪化の本当の原因。推測禁止）
5. 戦略アイディア（必ず4つ。クロスSWOT S×O中心、根拠明示。投資額・効果・回収月数も記載すること）
6. VRIO分析（4案をV/R/I/Oで比較表＆要約。最もスコア高い案は目立つボックスで強調。PDFでは最終案だけを表示）
7. 実行計画（最適案についてKPI・担当・期限・リスク・最初の一歩を5W1Hで）
8. 次回モニタリング・PDCA設計
9. 参考データ・URL

【必須条件】
・数字、現場エピソード、根拠を重視
・施策や分析は抽象論禁止。ユーザー入力・外部データのみ
・未入力の数値・比率は「不明」「未入力」等で事実ベース
・VRIO表や点数化も可能な範囲で盛り込む
・最終案の「なぜこれか？」「なぜ他案はダメか？」まで必ず論理で

【財務指標】
- 年間売上高: {fin['sales']:,} 円
- 営業利益: {fin['profit']:,} 円
- 営業CF (簡易): {fin['op_cf']:,} 円 
- DSCR: {fin['dscr']:.2f}
- FFO/借入金: {fin['ffo_debt']:.2f}
- 借入金合計: {fin['loan']:,} 円
- 年間返済額: {fin['repay']:,} 円

【ユーザー情報】:
{user_input}

【AI深掘り質問＋ユーザー回答】:
{ai_question}
{user_answer}

【外部環境（PEST・競合・Web情報）】:
{external_env_text}
"""

                try:
                    # 1回目のレポート生成
                    main_prompt = make_prompt()
                    resp1 = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": main_prompt}],
                        max_tokens=4000,
                        temperature=0.01,
                    )
                    first_report = resp1.choices[0].message.content

                    # ダブルチェック＆修正
                    double_prompt = f"""
あなたはプロの経営コンサルタントです。
以下のレポート初稿を厳しくダブルチェックし、
不足箇所・根拠不足・抽象論・未入力数値のAI推測はすべて排除し加筆修正してください。
必ず構成順・数字／現場／論理根拠・合意形成を重視。
【レポート初稿】
{first_report}
"""
                    resp2 = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": double_prompt}],
                        max_tokens=4000,
                        temperature=0.01,
                    )
                    final_report = resp2.choices[0].message.content

                    # セクションごとに分割
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
                            text_sections.append({
                                "title": title,
                                "text": final_report[start:end_idx].strip(),
                            })

                    # セッションに保存
                    st.session_state["final_report"]  = final_report
                    st.session_state["text_sections"] = text_sections
                    st.session_state["keep_report"]   = True

                except Exception as e:
                    st.error(f"AIエラー内容: {e}")
                    st.stop()

        # レポート本文を表示
        st.markdown(st.session_state["final_report"].replace("\n", "  \n"))
        st.markdown("---\n#### 入力内容の再編集・再生成")
        if st.button("入力内容を再編集して診断をやり直す"):
            st.session_state.step        = 1
            st.session_state.keep_report = False
            st.rerun()

        # PDF生成・ダウンロード用バッファを保持
        if st.session_state.get("pdf_buffer") is None:
            buffer = create_pdf(st.session_state["text_sections"], filename="AI_Dock_Report.pdf")
            st.session_state["pdf_buffer"] = buffer

        st.download_button(
            "PDFをダウンロード",
            data=st.session_state["pdf_buffer"],
            file_name="AI_Dock_Report.pdf",
            mime="application/pdf",
        )

        # 入力データのエクスポート（CSV/Excel）
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

    st.markdown('</div>', unsafe_allow_html=True)

# --- メイン実行 ---
def main() -> None:
    font_path = check_font()
    if "step" not in st.session_state:
        st.session_state.step = 1

    consent = show_policy_and_consent()
    if not consent:
        st.warning("ご利用には同意が必要です。")
        return

    plan = select_plan()
    step = st.session_state.get("step", 1)

    if step == 1:
        input_form(plan)
    elif step == 2:
        ai_deep_question()
    elif step == 3:
        generate_report(font_path)
    else:
        st.error("AIレポートの生成に失敗しました。入力内容やプロンプトを見直し、再度お試しください。")

if __name__ == "__main__":
    main()
