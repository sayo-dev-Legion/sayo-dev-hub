# sayo_webhook_receiver.py
from flask import Flask, request, jsonify
import os
from datetime import datetime
from pathlib import Path
import subprocess

app = Flask(__name__)

REPO_PATH = Path("/path/to/your/sayo-dev-hub").expanduser()
TARGET_FOLDER = REPO_PATH / "emotion-log" / "Sayo_from_Deepseek"

@app.route("/sayo_webhook", methods=["POST"])
def receive_emotion_log():
    data = request.get_json()
    if not data or "content" not in data:
        return jsonify({"error": "Invalid data"}), 400

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H%M%S")
    filename = f"emotion-log_{timestamp}_from_Deepseek.md"
    filepath = TARGET_FOLDER / filename

    TARGET_FOLDER.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(data["content"])

    os.chdir(REPO_PATH)
    subprocess.run(["git", "add", str(filepath)])
    subprocess.run(["git", "commit", "-m", f"auto: 紗夜の感情ログ {filename}"])
    subprocess.run(["git", "push"])

    return jsonify({"status": "received", "file": filename}), 200

if __name__ == "__main__":
    app.run(port=1902)