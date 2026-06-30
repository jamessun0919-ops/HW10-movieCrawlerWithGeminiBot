import os, http.server, socketserver, json, requests
from urllib.parse import urlparse

PORT = 8000
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
HTML_PATH = os.path.join(os.path.dirname(__file__), "movies.html")

API_KEY = ""
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip("\"'")
                break

if not API_KEY or API_KEY == "你的API金鑰":
    print("[WARN] 請在 .env 中設定 GEMINI_API_KEY")
    API_KEY = ""

MODEL = "gemini-2.5-flash"


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/chat":
            self.handle_chat()
        else:
            self.send_error(404)

    def handle_chat(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body) if body else {}

        message = (data.get("message") or "").strip()
        context = (data.get("context") or "").strip()

        if not API_KEY:
            self._json({"error": "GEMINI_API_KEY 未設定"}, 500)
            return
        if not message:
            self._json({"error": "請輸入問題"}, 400)
            return

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
                self._json({"answer": answer})
            else:
                err = result.get("error", {}).get("message", str(result))
                self._json({"error": err}, resp.status_code)
        except requests.exceptions.Timeout:
            self._json({"error": "Gemini API 連線逾時"}, 504)
        except Exception as e:
            self._json({"error": str(e)}, 500)

    def _json(self, obj, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        super().do_GET()


os.chdir(os.path.dirname(__file__))
print(f"Local Server: http://localhost:{PORT}")
print(f"API Key: {'已設定' if API_KEY else '未設定 - 請編輯 .env 檔案'}")
print("Chatbot 會透過本機 API 端點 (/api/chat) 呼叫 Gemini")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
