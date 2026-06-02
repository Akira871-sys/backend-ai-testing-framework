import requests

# 測試案例一：測試獲利產品列表 API 是否正常運作 (正向測試)
def test_get_all_products_should_return_200():
    # 1. 安排 (Arrange)：設定我們要測試的 API 網址
    url = "https://fakestoreapi.com/products"
    
    # 2. 執行 (Act)：用 requests 去對網址發出 GET 請求
    response = requests.get(url)
    
    # 3. 斷言 (Assert)：檢查回傳的結果。這行是自動化測試的靈魂！
    # 我們預期正常的 API 應該要回傳 HTTP 狀態碼 200 (代表成功)
    assert response.status_code == 200
    
    # 我們還可以順便檢查，回傳的資料是不是一個陣列（清單）
    assert isinstance(response.json(), list)


# 修正後的測試案例二
def test_get_invalid_product_id_should_return_empty_or_error():
    url = "https://fakestoreapi.com/products/9999"
    
    response = requests.get(url)
    
    # 根據我們剛剛抓到的實際狀況：
    # 這家 API 找不到東西時，會回傳空字串 '' 且狀態碼是 200
    # 我們把斷言修改成符合它實際的邏輯，或者寫得更有包容性：
    assert response.text == "" and response.status_code == 200