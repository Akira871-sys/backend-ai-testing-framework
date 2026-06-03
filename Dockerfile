# 1. 使用官方的 Python 輕量版作為基礎映像檔
FROM python:3.11-slim

# 2. 設定容器內的工作目錄（進容器後預設在哪個資料夾）
WORKDIR /app

# 3. 複製本地的相依套件清單到容器的 /app 目录下
COPY requirements.txt .

# 4. 在容器內安裝 Python 套件（不儲存快取以縮小映像檔體積）
RUN pip install --no-cache-dir -r requirements.txt

# 5. 複製本地所有專案程式碼到容器的 /app 資料夾內
COPY . .

# 6. 宣告這個容器運作時會監聽的連接埠（Mock Server 跑在 8000）
EXPOSE 8000

# 7. 容器啟動時，預設執行的指令：直接啟動我們的 Mock Server
CMD ["python", "mock_server.py"]