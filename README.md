# 113-1 資料庫管理 Farmly

## 專案簡介
無法找到新鮮在地的農產品？想直接支持小農卻找不到管道？現在就上「Farmly」，購買在地新鮮食材，讓小農的心意直達您的餐桌！

「Farmly」是一個專為小農設計的銷售與交流平台，主要目的是幫助小農解決銷售渠道有限、無法直接接觸終端消費者等問題，也讓消費者可以買到最新鮮的食材。此平台讓小農能夠直接面向消費者銷售其農產品，並在固定的市集活動中展示其農產品。透過這個平台，我們希望縮短供應鏈，讓消費者能夠以更合理的價格購買到最新鮮的農產品，同時支持小農的生計與發展。

## 使用者功能

## 使用方式
1. 使用備份檔 `farmly.backup` 復原資料庫
2. 輸入以下指令

  ```
  pip install -r requirements.txt
  ```

3. 輸入以下指令

  ```
  cp .env.example .env
  ```

3. 修改 `.env` 中的資料庫資訊，包含資料庫名稱 (DB_NAME)、使用者名稱 (DB_USER)、主機位置 (DB_HOST) 、通訊埠 (DB_PORT) 及密碼 (DB_PASSWORD)

  ```
  DB_NAME="farmly"
  DB_USER="postgres"
  DB_HOST="127.0.0.1"
  DB_PORT=5432
  DB_PASSWORD="your_password"
  ```
4. 預設連線通道如下，可至 server.py 及 client.py 修改

  ```
  IP = 127.0.0.1
  PORT = 8888
  ```

5. 先執行 `server.py` 啟動伺服器：
  
  ```
  python server.py
  ```

6. 再透過 `client.py` 向伺服器連線：
  
  ```
  python client.py
  ```

7. 開始使用 Farmly!

## 技術細節
- 使用 Socket 建立 client-server 連線，搭配 Multithreading 達成多人同時連線
- 資料庫使用 PostgreSQL，使用套件 Psycopg2 對資料庫進行操作
- **交易管理**
- **並行控制**

## 開發環境
- macOS 14.5
- Python: 3.11.6
  - psycopg2: 2.9.9
  - tabulate: 0.9.0
  - python-dotenv: 1.0.1
- PostgreSQL: 14.13
