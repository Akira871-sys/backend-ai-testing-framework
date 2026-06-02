# backend-ai-testing-framework
# AI 系統自動化測試與模型品質保證專案 (AI System Automation & Model QA)

本專案針對結合 AI 模型的後端服務，打造了一套完整的自動化測試與品質保證（QA）解決方案。涵蓋範圍從**後端 API 驗證、高併發壓力測試、資料品質檢驗（Data QA）**，到**模型表現門檻測試（Model QA）**，並整合 **GitHub Actions CI 流程**，實現每次程式碼變更時的自動化迴歸測試。

---

## 🚀 核心功能與測試範疇

### 1. 後端 API 自動化與壓力測試 (`api_tests/`)
* **權限與安全驗證 (`test_auth.py`)**：自動化驗證使用者登入機制、JWT Token 權限控管與過期機制。
* **AI 預測接口測試 (`test_predict_api.py`)**：針對 AI 推理 API 進行正常與異常輸入測試，確保後端吞吐與防禦機制正常。
* **高併發壓力測試 (`performance_locust.py`)**：使用 **Locust** 模擬 500 位使用者同時呼叫 AI 預測接口，評估系統在高負載下的回應時間（Response Time）與錯誤率（Error Rate）。

### 2. AI 模型品質保證 (`ai_model_tests/`)
* **資料品質測試 (`test_data_quality.py`)**：在模型推理前，自動檢查特徵欄位是否缺失、空值（Null Value）處理、極端值與髒資料過濾。
* **模型指標門檻測試 (`test_model_metrics.py`)**：自動化載入測試集，驗證最新模型的 `Accuracy` 與 `F1-Score` 是否達到上線標準，防止模型效能衰退（Model Drift）。

### 3. CI/CD 持續整合 (`.github/workflows/`)
* **自動化測試流水線 (`ci-test.yml`)**：整合 GitHub Actions，當開發者提交（Push）或建立 Pull Request 時，自動觸發測試環境、安裝套件並執行全套測試，確保程式碼品質。

---

## 📂 專案架構

```text
ai-system-automation-qa/
├── .github/workflows/
│   └── ci-test.yml           # GitHub Actions: CI 自動化測試流水線
├── api_tests/                # 第一部分：後端 API 自動化與壓力測試
│   ├── test_auth.py          # 權限、Token 與登入驗證
│   ├── test_predict_api.py   # AI 預測接口核心測試
│   └── performance_locust.py # Locust 壓力測試腳本 (模擬 500+ 併發)
├── ai_model_tests/           # 第二部分：AI 模型品質保證 (Model QA)
│   ├── test_data_quality.py  # 資料品質、特徵欄位與髒資料檢驗
│   └── test_model_metrics.py # 模型門檻驗證 (Accuracy / F1-Score)
├── test_data/                # 測試資料集 (Mock Data)
│   ├── normal_cases.json     # 正常測試情境
│   └── edge_cases.json       # 惡意與極端邊界測試情境
├── requirements.txt          # 專案相依套件
└── README.md                 # 專案說明文件
