# AI経営診断GPT

中小企業・個人事業主向けの無料AI経営診断アプリ  
（現場ヒアリング＋財務データ → AIが自動で改善レポート/PDF出力）

---

## 特徴

- 現場ヒアリング/財務データ入力 → ChatGPTが経営診断＆改善提案を自動生成
- 数分でPDF/CSV/Excelレポート出力
- **OpenAI・Google APIキーは `.streamlit/secrets.toml` に管理 → セキュア**
- Web版・ローカル版どちらもOK

---

## セットアップ手順

1. **リポジトリをClone または ZIPダウンロード**

    ```
    git clone https://github.com/xxxx/ai-keiei-gpt.git
    ```

2. **必要なライブラリをインストール**

    ```
    pip install -r requirements.txt
    ```

3. **APIキーの設定（必須！）**

    `.streamlit/secrets.toml` に以下の内容を記載してください：

    ```
    [openai]
    OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxx"

    [google]
    type = "service_account"
    project_id = "xxxxxx"
    private_key_id = "xxxxxx"
    private_key = """-----BEGIN PRIVATE KEY-----
    xxxxxxx
    -----END PRIVATE KEY-----"""
    client_email = "xxxx@xxxx.iam.gserviceaccount.com"
    client_id = "xxxxxx"
    auth_uri = "https://accounts.google.com/o/oauth2/auth"
    token_uri = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url = "https://www.googleapis.com/v1/certs"
    client_x509_cert_url = "xxxx"
    ```

    > ※ `.streamlit/secrets.toml` は **必ず .gitignore でGitHubにアップしないでください**（非公開）

4. **client_secret.json は不要です（TOML版に統一済）**

---

## 実行方法

ローカルで動かす場合：

streamlit run app.py

yaml
コピーする
編集する

---

## ディレクトリ構成例

ai-keiei-gpt/
├── .streamlit/
│ └── secrets.toml
├── app.py
├── requirements.txt
├── README.md
├── ipag.ttf
└── ...

yaml
コピーする
編集する

---

## よくある質問

- **APIキーは公開されませんか？**  
  → `.gitignore` で保護されています。自分だけが管理できます。

- **PDF日本語が文字化けします**  
  → `ipag.ttf`（IPAexゴシック）を同じフォルダに置いてください。

---

## ライセンス

MIT License

---

## お問い合わせ

要望・バグ報告は GitHub の Issue へどうぞ！
