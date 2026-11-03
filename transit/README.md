# Geomni：台北任意起點的大眾運輸時間地圖

GitHub Pages 展示三組預先運算的 15／30／45／60 分鐘可達格網，可切換情境與下載 GeoJSON。公開頁不連線分析 API、不提供任意點查詢。這是班表模型，不是即時到站或導航服務。

## 架構與資料

MapLibre + Turf（市界檢查）→ FastAPI → r5py 1.1.7 / R5 7.5.1 → OSM 步行路網與 GTFS → 300 m 格網中心旅行時間 → 合併格網的 GeoJSON。

- TDX 全國 GTFS（2026-11-03 下載）：抽取 TPE、NWT 市區公車 2,625 個 route IDs、79,220 個 trip IDs。不是 2,625 條不重複公車路線，方向及路線變體可能分開編碼。
- 台北捷運獨立 GTFS：feed_version 20260906，服務有效至 2026-12-31。
- 公車 calendar 有效 2026-11-03 至 2026-12-03，因此介面限制此日期範圍。
- OSM Geofabrik 台灣 2026-11-02 摘錄，路網裁切至 121.20,24.75,121.95,25.35。
- 畫面參考道路為 Overture 2026-10-21；不參與旅行時間運算。
- 起點市界參考 geoBoundaries 2017，不是法定界線。

## 如何解讀

總旅行時間包含步行接駁、候車、乘車與轉乘。使用 5 分鐘出發視窗及第 50 百分位；班距型服務仍有候車不確定性。步行上限參數 20 分鐘，最多搭乘 3 次的預設表示最多轉乘 2 次。

**公車 2,816,115 筆 stop_times 中，2,657,675 筆中間站時間留白**；首末站具時間，R5 依資料補估中途時間。因此成果不能解讀為逐站精確時刻。沒有即時交通、誤點、票價、無障礙或道路坡度分析。未含臺鐵、高鐵、機場捷運、環狀線及公路客運。暫不支援 05:00 前跨服務日查詢。

可達格網代表中心點，不保證整格每棟建築均可到達。目的地範圍固定為 121.35–121.75°E、24.90–25.25°N；範圍之外未計算，不能解讀為無法到達。

## 啟動

需要 Python 3.12、Java 21 以上、約 6 GB Java heap 與額外系統記憶體。首次建立路網需數分鐘及磁碟快取空間。

1. 安裝 `requirements.txt`。
2. 在 `GEOMNI_TRANSIT_DATA` 指向的目錄放入 `taipei.osm.pbf`、`taipei-bus.gtfs.zip`、`trtc.gtfs.zip`。
3. 公車子集以 `python backend/prepare_gtfs.py 原始全國.zip taipei-bus.gtfs.zip` 製作。OSM 可用 osmium extract 的 complete_ways 策略裁切上述範圍。
4. 設定 `XDG_CACHE_HOME` 至可寫快取目錄，執行 `python backend/server.py --max-memory 6G`。
5. API 位於 http://127.0.0.1:8773/api/isochrone；目前隨附 web/ 為預先運算展示介面，不會提交新查詢。原互動介面保留於提交 65dcfd8 的 transit/web/，本機工作目錄的完整版亦保留。

`web/` 不含 TDX 憑證或原始 GTFS。只部署靜態檔至 GitHub Pages 無法提供任意點分析，另需運行後端。本地服務預設僅監聽 127.0.0.1；公開前須配置 HTTPS、存取與用量控制、資料授權及資源限制。

## 資料與方法來源

- https://tdx.transportdata.tw/data-service/gtfs
- https://r5py.readthedocs.io/stable/
- https://download.geofabrik.de/asia/taiwan.html
- https://www.openstreetmap.org/copyright （OSM：ODbL）
- https://overturemaps.org/ （底圖各來源授權見原 Day 02 專案）

TDX 原始檔與登入資料不納入此程式交付；資料再散布須依所取得服務條款辦理。`evidence/` 保留資料品質檢查及實際運算輸出。
