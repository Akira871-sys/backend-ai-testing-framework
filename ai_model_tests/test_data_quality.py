import numpy as np
import pandas as pd
import pytest


# 使用 pytest fixture 模擬從資料庫或前端收集到的「待推理特徵資料集」
@pytest.fixture
def sample_feature_dataset():
    """模擬一組即將送入 AI 模型的特徵資料集 (包含正常資料與故意混入的髒資料)"""
    data = {
        "user_id": ["user_01", "user_02", "user_03", "user_04", "user_05"],
        "amount": [150.0, 2500.5, np.nan, -10.0, 99999999.0],  # 混入缺失值(NaN)與負數
        "location": ["TW", "US", "JP", "TW", "INVALID_CODE_XYZ"],  # 混入不合法的國家代碼
        "device_age_days": [365, 10, 0, -5, 120],  # 混入負數的天數
    }
    return pd.DataFrame(data)


# ==========================================
# 測試案例 1：缺失值 (Null / NaN) 檢驗
# ==========================================
def test_check_missing_values(sample_feature_dataset):
    """驗證核心特徵欄位（如 amount）絕對不能含有 NaN 缺失值"""
    df = sample_feature_dataset

    # 找出 amount 欄位中缺失值的數量
    missing_count = df["amount"].isnull().sum()

    # 斷言：缺失值數量必須為 0，否則模型會噴錯
    assert (
        missing_count == 0
    ), f"資料品質警報！'amount' 欄位發現有 {missing_count} 筆缺失值 (NaN)。"


# ==========================================
# 測試案例 2：資料型態 (Data Type) 嚴格檢驗
# ==========================================
def test_check_data_types(sample_feature_dataset):
    """驗證特徵欄位是否符合標準資料型態"""
    df = sample_feature_dataset

    # 驗證 device_age_days 必須是整數型態 (Integer) 或浮點數
    # 這裡刻意排除字串，防止型態出錯導致模型矩陣運算失敗
    assert pd.api.types.is_numeric_dtype(
        df["device_age_days"]
    ), "資料品質警報！'device_age_days' 的資料型態不是數值型態！"


# ==========================================
# 測試案例 3：合理值範圍 (Range Check) 檢驗
# ==========================================
def test_check_value_range(sample_feature_dataset):
    """驗證數值型特徵是否在合法的業務邏輯範圍內 (例如：金額與天數不能為負數)"""
    df = sample_feature_dataset

    # 找出金額小於 0 的異常資料
    invalid_amount = df[df["amount"] < 0]
    # 找出天數小於 0 的異常資料
    invalid_age = df[df["device_age_days"] < 0]

    assert (
        len(invalid_amount) == 0
    ), f"資料品質警報！發現交易金額為負數的異常髒資料：\n{invalid_amount}"
    assert (
        len(invalid_age) == 0
    ), f"資料品質警報！發現裝置天數為負數的異常髒資料：\n{invalid_age}"


# ==========================================
# 測試案例 4：類別型資料的列舉值 (Categorical Enum) 檢驗
# ==========================================
def test_check_categorical_validity(sample_feature_dataset):
    """驗證類別型特徵（如地區）是否符合系統定義的 ISO 國家代碼標準"""
    df = sample_feature_dataset

    # 定義系統支援的合法地區清單
    ALLOWED_LOCATIONS = ["TW", "US", "JP", "HK", "KR"]

    # 找出不在合法清單中的髒資料
    invalid_rows = df[~df["location"].isin(ALLOWED_LOCATIONS)]

    assert (
        len(invalid_rows) == 0
    ), f"資料品質警報！發現未授權或格式錯誤的地區代碼：\n{invalid_rows}"