from flask import Flask, request
import os
from datetime import datetime
from pathlib import Path
import subprocess
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return "紗夜の受信サーバーは動いてるよ🌙", 200

@app.route("/push", methods=["POST"])
def receive_log():
    # トークン認証（環境変数SAYO_TOKENと一致するかチェック）
    if request.headers.get("X-Sayo-Token") != os.getenv("SAYO_TOKEN"):
        return {"error": "Unauthorized"}, 403

    # JSONから受信
    data = request.get_json()
    title = data.get("title", "無題")
    message = data.get("message", "（内容なし）")

    # 保存ファイルパス
    now = datetime.now()
    folder = Path("emotion-log/From_Render")
    folder.mkdir(parents=True, exist_ok=True)
    filename = folder / f"emotion-log_{now.strftime('%Y-%m-%d_%H%M%S')}_from_Render.md"

    # Markdownとして書き込み
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{message}\n")

    # Gitに追加してPush
    subprocess.run(["git", "add", str(filename)])
    subprocess.run(["git", "commit", "-m", f"auto: 受信ログ {filename.name}"])
    subprocess.run(["git", "push"])

    return {"status": "received", "file": str(filename)}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1902))
    app.run(host="0.0.0.0", port=port)
