import pytest
from sklearn.metrics import accuracy_score, f1_score


# ==========================================
# 模擬測試資料集 (Fixture)
# ==========================================
@pytest.fixture
def model_evaluation_data():
    """
    模擬一組標準測試集。
    y_true: 真實世界中，這些交易到底是不是盜刷 (1代表是, 0代表不是)
    y_pred: AI 模型讀取特徵後，給出的預測答案
    """
    # 假設這是 10 筆測試資料的真實標籤
    y_true = [0, 0, 0, 1, 1, 0, 1, 0, 0, 1]

    # 情況 A：優秀的模型 (只猜錯 1 筆)
    y_pred_good = [0, 0, 0, 1, 1, 0, 0, 0, 0, 1]

    # 情況 B：退化/不及格的模型 (猜錯好幾 筆，把盜刷都猜成正常)
    y_pred_bad = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

    return {"y_true": y_true, "good_model": y_pred_good, "bad_model": y_pred_bad}


# ==========================================
# 定義團隊硬性指標門檻 (Thresholds)
# ==========================================
ACCURACY_THRESHOLD = 0.85  # 準確率必須大於 85%
F1_SCORE_THRESHOLD = 0.80  # F1-Score 必須大於 80% (這在樣本不平衡的盜刷模型中特別重要)


# ==========================================
# 測試案例 1：驗證優秀版 AI 模型 (預期通過 PASSED)
# ==========================================
def test_good_model_performance(model_evaluation_data):
    """驗證當模型品質優良時，指標是否能順利跨過門檻"""
    y_true = model_evaluation_data["y_true"]
    y_pred = model_evaluation_data["good_model"]

    # 計算指標
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    print(f"\n[Good Model] Accuracy: {acc:.2f}, F1-Score: {f1:.2f}")

    # 進行指標斷言門檻檢查
    assert (
        acc >= ACCURACY_THRESHOLD
    ), f"模型準確率過低！得到 {acc:.2f}，未達門檻 {ACCURACY_THRESHOLD}"
    assert (
        f1 >= F1_SCORE_THRESHOLD
    ), f"模型 F1-Score 過低！得到 {f1:.2f}，未達門檻 {F1_SCORE_THRESHOLD}"


# ==========================================
# 測試案例 2：驗證退化版 AI 模型 (預期失敗 FAILED)
# ==========================================
def test_bad_model_performance(model_evaluation_data):
    """驗證當 AI 模型智商退化時，自動化測試是否能成功攔截"""
    y_true = model_evaluation_data["y_true"]
    y_pred = model_evaluation_data["bad_model"]

    # 計算指標
    acc = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    print(f"\n[Bad Model] Accuracy: {acc:.2f}, F1-Score: {f1:.2f}")

    # 預期這裡會觸發斷言失敗，因為 bad_model 的表現太爛了
    assert (
        acc >= ACCURACY_THRESHOLD
    ), f"【🚨 CI/CD 攔截】新模型準確率退化！僅得到 {acc:.2f}，低於硬性門檻 {ACCURACY_THRESHOLD}"
    assert (
        f1 >= F1_SCORE_THRESHOLD
    ), f"【🚨 CI/CD 攔截】新模型 F1-Score 嚴重退化！僅得到 {f1:.2f}，低於硬性門檻 {F1_SCORE_THRESHOLD}"