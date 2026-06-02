import json
import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
LOGIN_URL = f"{BASE_URL}/api/v1/login"
PREDICT_API_URL = f"{BASE_URL}/api/v1/predict"


def load_test_data(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "../test_data", file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# 新增一個 pytest fixture：讓預測測試也能自動獲取 Token
@pytest.fixture(scope="module")
def auth_headers():
    """自動登入並回傳帶有 Token 的 Headers"""
    payload = {"username": "test_user", "password": "secure_password123"}
    try:
        response = requests.post(LOGIN_URL, json=payload)
        tokens = response.json()
        return {"Authorization": f"Bearer {tokens['access_token']}"}
    except Exception as e:
        pytest.fail(f"預測測試初始化登入失敗: {e}")


# ==========================================
# 測試情境一：正常測資測試 (Normal Cases)
# ==========================================
# 這裡把 auth_headers 傳進測試函式中
@pytest.mark.parametrize("case", load_test_data("normal_cases.json"))
def test_predict_api_normal_cases(case, auth_headers):
    """測試正常輸入時，AI 預測 API 是否能正確回傳 200"""
    print(f"\n執行正常測試案例: {case['case_id']}")

    # 加上 headers=auth_headers 傳送 Token 過去
    response = requests.post(PREDICT_API_URL, json=case["input"], headers=auth_headers)

    assert (
        response.status_code == 200
    ), f"預期狀態碼 200，但得到 {response.status_code}。回應內容：{response.text}"

    response_data = response.json()
    assert response_data["status"] == case["expected"]["status"]
    assert response_data["is_fraud"] == case["expected"]["is_fraud"]
    assert (
        abs(response_data["confidence_score"] - case["expected"]["confidence_score"])
        < 0.05
    )


# ==========================================
# 測試情境二：異常邊界測試 (Edge Cases)
# ==========================================
# 這裡同樣要把 auth_headers 傳進測試函式中
@pytest.mark.parametrize("case", load_test_data("edge_cases.json"))
def test_predict_api_edge_cases(case, auth_headers):
    """測試髒資料時，後端防禦機制是否正常 (應回傳 400，而非 401 或 500)"""
    print(f"\n執行邊界測試案例: {case['case_id']}")

    # 加上 headers=auth_headers
    response = requests.post(PREDICT_API_URL, json=case["input"], headers=auth_headers)

    assert (
        response.status_code == case["expected"]["status_code"]
    ), f"防禦機制失效！預期狀態碼 {case['expected']['status_code']}，但得到 {response.status_code}。回應：{response.text}"

    response_data = response.json()
    assert (
        case["expected"]["error_message"] in response_data["error_message"]
    ), f"預期錯誤訊息應包含 '{case['expected']['error_message']}'，但得到 '{response_data['error_message']}'"