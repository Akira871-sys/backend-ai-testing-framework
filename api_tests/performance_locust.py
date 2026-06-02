import random
from locust import HttpUser, task, between


class AIBankPressUser(HttpUser):
    """
    這個類別定義了單一虛擬使用者的行為。
    Locust 會根據設定，同時產生 500 個這樣的虛擬使用者來執行任務。
    """

    # 模擬真人行為：每個虛擬使用者執行完一個任務後，會隨機停頓 1 到 3 秒，再執行下一個任務
    wait_time = between(1, 3)

    def on_start(self):
        """
        每個虛擬使用者『誕生』時，都會先執行一次這個函式。
        我們在這裡讓它先進行登入，並取得 JWT Token，以便後續呼叫受保護的 API。
        """
        self.token = ""
        login_payload = {
            "username": "test_user",
            "password": "secure_password123",
        }

        # 發送登入請求
        with self.client.post(
            "/api/v1/login", json=login_payload, catch_response=True
        ) as response:
            if response.status_code == 200:
                # 登入成功，存下 Token
                self.token = response.json().get("access_token")
            else:
                response.failure(f"登入失敗，狀態碼: {response.status_code}")

    @task(1)
    def press_predict_api(self):
        """
        這是壓測的核心任務。Locust 會不斷重複執行帶有 @task 裝飾器的函式。
        """
        # 如果登入失敗沒拿到 Token，就無法呼叫預測 API
        if not self.token:
            return

        # 準備帶給 AI API 的 Headers (JWT Token)
        headers = {"Authorization": f"Bearer {self.token}"}

        # 隨機產生正常交易或大額交易，讓 Mock Server 的 AI 邏輯有不同的運算
        mock_amount = random.choice([150.0, 2500.0, 99999.0])
        mock_location = random.choice(["TW", "US", "JP"])

        payload = {
            "user_id": f"user_press_{random.randint(1000, 9999)}",
            "amount": mock_amount,
            "location": mock_location,
            "device_age_days": random.randint(1, 365),
        }

        # 發送預測請求，並用 name 參數把網址群組化（方便在報表上看）
        self.client.post(
            "/api/v1/predict", json=payload, headers=headers, name="/api/v1/predict"
        )