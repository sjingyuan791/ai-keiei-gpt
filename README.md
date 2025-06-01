# AI経営診断GPT

中小企業・個人事業主向けの無料AI経営診断アプリ  
（現場ヒアリング＋財務データ → AIが自動で改善レポート/PDF出力）

---

## 特徴
- 現場ヒアリング/財務データ入力 → ChatGPTが経営診断＆改善提案を自動生成
- 専門知識不要・数分でPDF/CSV/Excelレポート出力
- プライバシー・セキュリティも安心（APIキーは各自で管理）

---

## セットアップ手順

1. **リポジトリをClone or ZIPダウンロード**

    ```
    git clone https://github.com/sjingyuan791/ai-keiei-gpt.git
    ```

2. **必要なライブラリをインストール**

    ```
    pip install -r requirements.txt
    ```

3. **APIキーの設定（必須！）**
    - `.streamlit/`ディレクトリの中に`secrets.toml`を自分で作成し、以下のように書いてください

    ```
    [openai]
    OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxx"
    ```

    > ※このファイルは**絶対にGitHubにアップロードしないでください**（.gitignoreですでに保護済み）

4. **Google連携機能を使う場合**  
   `client_secret.json.example`を参考に、自分のGoogle APIキー（ServiceAccount）で`client_secret.json`を用意

---

## 実行方法

streamlit run app.py

yaml
コピーする
編集する

---

## ディレクトリ構成例

ai-keiei-gpt/
├── .streamlit/
│ └── .gitkeep
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
  → `.gitignore`で保護されています。自分だけが管理できます。

- **PDF日本語が文字化けします**  
  → `ipag.ttf`（IPAexゴシック）を同じフォルダに置いてください

---

## ライセンス

MIT License

---

## お問い合わせ

要望・バグ報告はGitHubのIssueでどうぞ！
