import pytest
import allure
from sklearn.metrics import accuracy_score, f1_score

# ==========================================
# 定義團隊硬性指標門檻 (Thresholds)
# ==========================================
ACCURACY_THRESHOLD = 0.85  # 準確率必須大於 85%
F1_SCORE_THRESHOLD = 0.80  # F1-Score 必須大於 80%


# 用 Epic 和 Feature 幫 Allure 報告做大分類（對應到系統模組架構）
@allure.epic("AI 模型品質保證 (Model QA)")
@allure.feature("模型評估指標門檻測試")
class TestModelMetrics:

    @pytest.fixture
    def model_evaluation_data(self):
        """
        模擬一組標準測試集。
        y_true: 真實世界中，這些交易到底是不是盜刷 (1代表是, 0代表不是)
        y_pred: AI 模型讀取特徵後，給出的預測答案
        """
        y_true = [0, 0, 0, 1, 1, 0, 1, 0, 0, 1]

        # 情況 A：優秀的模型 (只猜錯 1 筆，準確度極高)
        y_pred_good = [0, 0, 0, 1, 1, 0, 0, 0, 0, 1]

        # 情況 B：嚴重退化的模型 (猜錯好幾筆，無法辨識盜刷風險)
        y_pred_bad = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

        return {"y_true": y_true, "good_model": y_pred_good, "bad_model": y_pred_bad}

    # ==========================================
    # 測試案例 1：驗證優秀版 AI 模型 (預期通過 PASSED)
    # ==========================================
    @allure.story("驗證正常訓練的高智商模型性能")
    @allure.severity(allure.severity_level.CRITICAL)  # 設定重要程度
    @allure.description("此測試會模擬正常優良的模型，驗證其 Accuracy 與 F1-score 是否能順利跨過團隊設定的硬性門檻。")
    def test_good_model_performance(self, model_evaluation_data):
        """驗證當模型品質優良時，指標是否能順利跨過門檻"""
        y_true = model_evaluation_data["y_true"]
        y_pred = model_evaluation_data["good_model"]

        # 使用 allure.step 拆解測試步驟，報告中會像摺疊選單一樣一條一條清晰顯示
        with allure.step("步驟 1：調用 scikit-learn 計算模型 Accuracy (準確率)"):
            acc = accuracy_score(y_true, y_pred)
            allure.attach(f"當前模型 Accuracy 結果: {acc:.2f}", name="Accuracy 數值")
            
        with allure.step("步驟 2：調用 scikit-learn 計算模型 F1-Score (綜合指標)"):
            f1 = f1_score(y_true, y_pred)
            allure.attach(f"當前模型 F1-Score 結果: {f1:.2f}", name="F1-Score 數值")
            
        with allure.step("步驟 3：執行門檻斷言檢查"):
            print(f"\n[Good Model] Accuracy: {acc:.2f}, F1-Score: {f1:.2f}")
            assert (
                acc >= ACCURACY_THRESHOLD
            ), f"模型準確率過低！得到 {acc:.2f}，未達門檻 {ACCURACY_THRESHOLD}"
            assert (
                f1 >= F1_SCORE_THRESHOLD
            ), f"模型 F1-Score 過低！得到 {f1:.2f}，未達門檻 {F1_SCORE_THRESHOLD}"

    # ==========================================
    # 測試案例 2：驗證退化版 AI 模型 (預期失敗 FAILED)
    # ==========================================
    @allure.story("攔截嚴重退化或被污染的不及格模型")
    @allure.severity(allure.severity_level.BLOCKER)  # 這是阻斷級別的嚴重錯誤
    @allure.description("此測試會模擬異常退化的模型，驗證自動化測試是否能成功在 CI/CD 階段精準攔截，阻止其上線。")
    def test_bad_model_performance(self, model_evaluation_data):
        """驗證當 AI 模型智商退化時，自動化測試是否能成功攔截"""
        y_true = model_evaluation_data["y_true"]
        y_pred = model_evaluation_data["bad_model"]

        with allure.step("步驟 1：調用 scikit-learn 計算退化模型 Accuracy"):
            acc = accuracy_score(y_true, y_pred)
            allure.attach(f"異常模型 Accuracy 結果: {acc:.2f}", name="Accuracy 數值")
            
        with allure.step("步驟 2：調用 scikit-learn 計算退化模型 F1-Score"):
            f1 = f1_score(y_true, y_pred)
            allure.attach(f"異常模型 F1-Score 結果: {f1:.2f}", name="F1-Score 數值")

        with allure.step("步驟 3：執行硬性門檻攔截，預期會觸發 AssertionError 報警"):
            print(f"\n[Bad Model] Accuracy: {acc:.2f}, F1-Score: {f1:.2f}")
            assert (
                acc >= ACCURACY_THRESHOLD
            ), f"【🚨 CI/CD 攔截】新模型準確率退化！僅得到 {acc:.2f}，低於硬性門檻 {ACCURACY_THRESHOLD}"
            assert (
                f1 >= F1_SCORE_THRESHOLD
            ), f"【🚨 CI/CD 攔斥】新模型 F1-Score 嚴重退化！僅得到 {f1:.2f}，低於硬性門檻 {F1_SCORE_THRESHOLD}"