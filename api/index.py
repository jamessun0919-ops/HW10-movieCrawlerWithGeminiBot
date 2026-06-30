import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("GEMINI_API_KEY", "")
MODEL = "gemini-2.5-flash"


@app.route("/api/chat", methods=["POST"])
def chat():
    if not API_KEY:
        return jsonify({"error": "GEMINI_API_KEY 未設定"}), 500

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "無效的請求"}), 400

    message = data.get("message", "").strip()
    context = data.get("context", "").strip()

    if not message:
        return jsonify({"error": "請輸入問題"}), 400

    prompt = f"{context}\n\n使用者問題：{message}\n\n請用繁體中文回答。"

    try:
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30,
        )

        result = resp.json()

        if resp.status_code == 200:
            answer = (
                result.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            return jsonify({"answer": answer})

        error_msg = result.get("error", {}).get("message", str(result))
        return jsonify({"error": error_msg}), resp.status_code

    except requests.exceptions.Timeout:
        return jsonify({"error": "Gemini API 連線逾時"}), 504
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "HW10 Movie Crawler API",
        "endpoints": {
            "/health": "GET - 健康檢查",
            "/api/chat": "POST - 聊天機器人"
        },
        "frontend": "https://hw10-moviecrawlerwithgeminibot.vercel.app"
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8001)))
