# 113-1 資料庫管理 Farmly

## 專案簡介
無法找到新鮮在地的農產品？想直接支持小農卻找不到管道？現在就上「Farmly」，購買在地新鮮食材，讓小農的心意直達您的餐桌！

「Farmly」是一個專為小農設計的銷售與交流平台，主要目的是幫助小農解決銷售渠道有限、無法直接接觸終端消費者等問題，也讓消費者可以買到最新鮮的食材。此平台讓小農能夠直接面向消費者銷售其農產品，並在固定的市集活動中展示其農產品。透過這個平台，我們希望縮短供應鏈，讓消費者能夠以更合理的價格購買到最新鮮的農產品，同時支持小農的生計與發展。

## 使用者功能
### Farmer (小農)
1. 註冊帳號
   - 小農輸入基本資訊（如：使用者名稱、密碼、手機號碼、電子郵件等），系統會分配一個 farmer_id 給每位小農。
2. 登入系統
   - 使用手機號碼與密碼登入系統。
3. 上架農產品
   - 小農可以上架農產品，輸入產品種類、單位、重量、採收日期、有效日期、數量、價格等資訊。
4. 查詢農產品上架記錄
   - 小農可以查詢自己過去的上架農產品資訊。
5. 參加農夫市集
   - 小農可以查詢開放中的市集，並登記參加。
6. 檢視獲得的評分
   - 小農可以檢視消費者給自己的評分（1-5）。

### Consumer (消費者)
1. 註冊帳號
   - 消費者輸入基本資訊（如：使用者名稱、密碼、手機號碼、電子郵件等），系統會分配一個 consumer_id 給每位消費者。
2. 登入系統
   - 使用手機號碼與密碼登入系統。
3. 查詢農產品
   - 消費者可以輸入產品種類與有效日期，查詢所有平台上的農產品。
4. 調整購物車數量
   - 加入：指定產品編號與數量，將其加入購物車。
   - 刪除：指定產品編號與數量，將從購物車中刪除。
5. 透過購物車下訂單
   - 選擇欲下單的產品編號與數量，並輸入付款資訊與配送資訊。
6. 查詢訂單歷史紀錄
   - 消費者可以查詢自己過去的訂單記錄。
7. 評價小農
   - 消費者可以對小農評分與評論。

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

4. 修改 `.env` 中的資料庫資訊，包含資料庫名稱 (DB_NAME)、使用者名稱 (DB_USER)、主機位置 (DB_HOST) 、通訊埠 (DB_PORT) 及密碼 (DB_PASSWORD)

    ```
    DB_NAME="farmly"
    DB_USER="postgres"
    DB_HOST="127.0.0.1"
    DB_PORT=5432
    DB_PASSWORD="your_password"
    ```
    
5. 預設連線通道如下，可至 server.py 及 client.py 修改

    ```
    IP = 127.0.0.1
    PORT = 8888
    ```

6. 先執行 `server.py` 啟動伺服器：
  
    ```
    python server.py
    ```

7. 再透過 `client.py` 向伺服器連線：
  
    ```
    python client.py
    ```

8. 開始使用 Farmly!

## 技術細節
- 使用 Socket 建立 client-server 連線，搭配 Multithreading 達成多人同時連線
- 資料庫使用 PostgreSQL，使用套件 Psycopg2 對資料庫進行操作
- **交易管理**
  - 消費者將商品加入購物車: 在此功能中，系統將檢查該商品庫存是否充足。若庫存不足，系統將使用 `db.rollback()` 方法撤回該次交易，避免插入不合理的購物車數據。反之，庫存充足時則將商品加入購物車，並執行 `db.commit()` 提交交易。
- **並行控制**

## 程式說明
1. `server.py`
   - 包含伺服器端的主要功能。
   - 在連接資料庫後，透過 socket 建立監聽服務，接收來自客戶端的連線請求。
   - 每當接收到一個客戶端連線，會啟動一個獨立的執行緒（thread) 處理該連線，確保伺服器能並行處理多個客戶端。
  
2. `client.py`
   - 包含客戶端的主要功能。
   - 持續從伺服器接收訊息並顯示於終端機。
   - 當訊息包含特定標籤（tag）時，根據標籤執行對應的操作，例如讀取使用者輸入、解析 CSV 檔案、關閉 socket 連線並結束程式。
    
3. `action_handler.py`
   - 處理客戶端的所有需求，決定要呼叫哪些 `db_utils.py` 中的 function，及返回哪些結果給客戶端。
    
4. `db_utils.py`
   - 封裝與資料庫相關的功能，包含資料庫連線管理與查詢操作。
    
5. `role` 資料夾
   - 為支援未來擴展更多角色類型（如 Farmer 和 Consumer 之外的角色），將角色實作為類別，並繼承基底類別 Role。
   - 每個角色類別共享基底類別的通用功能，並可擴展定義角色特有的行為與權限。

## 開發環境
- macOS 14.5
- Python: 3.11.6
  - psycopg2: 2.9.9
  - tabulate: 0.9.0
  - python-dotenv: 1.0.1
- PostgreSQL: 14.13
