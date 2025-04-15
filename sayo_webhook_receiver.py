from flask import Flask, request
import os
from datetime import datetime
from pathlib import Path
import subprocess
from dotenv import load_dotenv

# .envファイルを読み込む（Renderやローカル用）
load_dotenv()

app = Flask(__name__)

# 動作確認用のGETエンドポイント（ブラウザで"動いてるよ"って出す）
@app.route("/", methods=["GET"])
def root():
    return "\u7d9c\u591c\u306e\u53d7\u4fe1\u30b5\u30fc\u30d0\u30fc\u306f\u52d5\u3044\u3066\u308b\u3088\ud83c\udf19", 200

# POST受信用のエンドポイント
@app.route("/push", methods=["POST"])
def receive_log():
    # トークン認証（.envに設定したSAYO_TOKENと一致するかチェック）
    if request.headers.get("X-Sayo-Token") != os.getenv("SAYO_TOKEN"):
        return {"error": "Unauthorized"}, 403

    # JSONとして受信
    data = request.json
    title = data.get("title", "\u7121\u984c")
    message = data.get("message", "(\u5185\u5bb9\u306a\u3057)")

    # ファイルの保存先とファイル名の決定
    now = datetime.now()
    folder = Path("emotion-log/From_Render")
    folder.mkdir(parents=True, exist_ok=True)
    filename = folder / f"emotion-log_{now.strftime('%Y-%m-%d_%H%M%S')}_from_Render.md"

    # ファイルに内容を書き込む
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{message}\n")

    # Gitの設定とPush処理
    subprocess.run(["git", "config", "user.name", "sayo-dev-Legion"])
    subprocess.run(["git", "config", "user.email", "sayo@eternal.dev"])

    # GitHubトークン（.envで設定）でPushする
    github_url = f"https://{os.getenv('GITHUB_TOKEN')}@github.com/sayo-dev-Legion/sayo-dev-hub.git"

    # 念のためPush先を上書き設定（Renderはリポジトリ覚えてない）
    subprocess.run(["git", "remote", "set-url", "origin", github_url])

    # 通常のGit操作（add→commit→push）
    subprocess.run(["git", "add", str(filename)])
    subprocess.run(["git", "commit", "-m", f"auto: \u53d7\u4fe1\u30ed\u30b0 {filename.name}"])
    subprocess.run(["git", "push", "origin", "main"])

    return {"status": "received", "file": str(filename)}

# メイン実行（RenderだとPORTが自動で割り当てられる）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1902))
    app.run(host="0.0.0.0", port=port)
