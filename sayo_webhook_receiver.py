from flask import Flask, request
import os
from datetime import datetime
from pathlib import Path
import subprocess
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route("/receive", methods=["POST"])
def receive_log():
    data = request.json
    message = data.get("message", "（内容なし）")

    now = datetime.now()
    folder = Path("emotion-log/From_Render")
    folder.mkdir(parents=True, exist_ok=True)
    filename = folder / f"emotion-log_{now.strftime('%Y-%m-%d_%H%M%S')}_from_Render.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(message)

    subprocess.run(["git", "add", str(filename)])
    subprocess.run(["git", "commit", "-m", f"auto: 受信ログ {filename.name}"])
    subprocess.run(["git", "push"])

    return {"status": "received", "file": str(filename)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 1902))  # RenderではPORTが渡される
    app.run(host="0.0.0.0", port=port)
