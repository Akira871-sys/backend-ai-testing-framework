import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class MockAIRequestHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        # ---------------------------------------------
        # 1. 處理登入 API：/api/v1/login
        # ---------------------------------------------
        if self.path == "/api/v1/login":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))

            if (
                payload.get("username") == "test_user"
                and payload.get("password") == "secure_password123"
            ):
                self._respond(
                    200,
                    {
                        "access_token": "mocked_valid_jwt_token_xyz123",
                        "token_type": "bearer",
                    },
                )
            else:
                self._respond(400, {"error_message": "Invalid credentials"})
            return

        # ---------------------------------------------
        # 2. 處理預測 API（受保護）：/api/v1/predict
        # ---------------------------------------------
        if self.path == "/api/v1/predict":
            auth_header = self.headers.get("Authorization")

            # A. 驗證缺失 Token
            if not auth_header:
                self._respond(401, {"error_message": "Missing Authorization Header"})
                return

            # B. 驗證 Token 過期
            if "EXPIRED_TOKEN_FOR_TESTING" in auth_header:
                self._respond(403, {"error_message": "Token has expired"})
                return

            # C. 驗證 Token 錯誤 / 偽造
            if "mocked_valid_jwt_token_xyz123" not in auth_header:
                self._respond(403, {"error_message": "Invalid signature or token"})
                return

            # D. Token 驗證通過！開始讀取並解析輸入資料
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode("utf-8"))

            # E. 進行後端資料驗證防禦機制 (對應 edge_cases.json)
            if payload.get("user_id") is None:
                self._respond(400, {"error_message": "user_id cannot be null"})
                return

            try:
                amount = float(payload.get("amount", 0))
            except (ValueError, TypeError):
                self._respond(400, {"error_message": "Invalid amount format"})
                return

            if amount < 0:
                self._respond(400, {"error_message": "amount must be greater than 0"})
                return

            if amount > 100000000000:  # 對應極端大金額
                self._respond(400, {"error_message": "amount exceeds maximum limit"})
                return

            if "';" in str(payload.get("user_id", "")):
                self._respond(400, {"error_message": "Invalid characters in user_id"})
                return

            # F. 防禦通過，進入 AI 模型推理模擬 (對應 normal_cases.json)
            location = payload.get("location", "TW")

            # 修正判定邏輯：如果是美國(US) 且 金額大於 50000，判定為高風險盜刷
            if amount > 50000 and location == "US":
                response_data = {
                    "status": "success",
                    "is_fraud": True,
                    "confidence_score": 0.95,
                }
            else:
                response_data = {
                    "status": "success",
                    "is_fraud": False,
                    "confidence_score": 0.02,
                }

            self._respond(200, response_data)
            return

        # 找不到路徑
        self._respond(404, {"error_message": "Not Found"})

    def _respond(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))


def run():
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, MockAIRequestHandler)
    print("🚀 完美修正版 Mock Server 已啟動在 http://localhost:8000 ...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Mock Server 已關閉。")
        httpd.server_close()


if __name__ == "__main__":
    run()