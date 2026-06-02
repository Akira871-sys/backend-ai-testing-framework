import os
import pytest
import requests

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
LOGIN_URL = f"{BASE_URL}/api/v1/login"
PROTECTED_API_URL = f"{BASE_URL}/api/v1/predict"


# 使用 pytest.fixture 來實作「登入並取得 Token」的自動化流程
# 這樣其他測試案例只要把 token 當成參數傳入，就能直接使用
@pytest.fixture(scope="module")
def valid_token():
    """模擬使用者登入，取得合法的 JWT Token"""
    payload = {"username": "test_user", "password": "secure_password123"}
    response = requests.post(LOGIN_URL, json=payload)

    assert (
        response.status_code == 200
    ), f"登入失敗，無法進行後續權限測試。狀態碼：{response.status_code}"

    tokens = response.json()
    return tokens["access_token"]


# ==========================================
# 測試案例 1：帶有合法 Token 的正常請求
# ==========================================
def test_auth_with_valid_token(valid_token):
    """驗證：帶上正確的 JWT Token 時，API 應允許存取 (200)"""
    headers = {"Authorization": f"Bearer {valid_token}"}
    # 帶上隨意的測試輸入資料
    mock_input = {
        "user_id": "user_123",
        "amount": 100.0,
        "location": "TW",
        "device_age_days": 10,
    }

    response = requests.post(PROTECTED_API_URL, json=mock_input, headers=headers)
    assert response.status_code == 200, "合法 Token 卻遭到拒絕存取！"


# ==========================================
# 測試案例 2：完全不帶 Token 的請求 (未授權)
# ==========================================
def test_auth_missing_token():
    """驗證：不帶 Authorization Header 時，後端應阻擋並回傳 401"""
    mock_input = {"user_id": "user_123", "amount": 100.0}

    response = requests.post(PROTECTED_API_URL, json=mock_input)  # 沒有 headers
    assert (
        response.status_code == 401
    ), f"安全漏洞！未帶 Token 竟然放行或回傳錯誤狀態碼：{response.status_code}"


# ==========================================
# 測試案例 3：帶有偽造/錯誤 Token 的請求 (禁止存取)
# ==========================================
def test_auth_invalid_token():
    """驗證：帶上無效或偽造的 Token 時，後端應拒絕並回傳 403"""
    headers = {"Authorization": "Bearer this_is_a_fake_and_invalid_jwt_token"}
    mock_input = {"user_id": "user_123", "amount": 100.0}

    response = requests.post(PROTECTED_API_URL, json=mock_input, headers=headers)
    assert (
        response.status_code == 403
    ), f"安全漏洞！偽造的 Token 未被正確阻擋：{response.status_code}"


# ==========================================
# 測試案例 4：模擬 Token 過期的情境
# ==========================================
def test_auth_expired_token():
    """驗證：當 Token 過期時，後端應識別並拒絕存取 (401 或 403)"""
    # 這裡我們利用後端的測試後門：傳送一個特製的過期 Token
    headers = {"Authorization": "Bearer EXPIRED_TOKEN_FOR_TESTING"}
    mock_input = {"user_id": "user_123", "amount": 100.0}

    response = requests.post(PROTECTED_API_URL, json=mock_input, headers=headers)
    # 根據不同公司的架構，過期可能回傳 401 或 403，這裡我們允許兩者皆可
    assert response.status_code in [
        401,
        403,
    ], f"安全漏洞！過期的 Token 未被阻擋：{response.status_code}"