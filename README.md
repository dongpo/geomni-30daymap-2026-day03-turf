# Geomni · 改變分析範圍，瀏覽器如何即時計算行政區交集？

[操作地圖](https://dongpo.github.io/geomni-30daymap-2026-day03-turf/)

## 這張地圖要回答什麼？

以指定位置為中心，建立距離緩衝區，計算與哪些行政區相交、各自相交多少面積。調整半徑或點選地圖移動中心，觀察交集形狀與面積如何改變。

## 地圖怎麼看？

灰藍色是原行政區，青綠色是行政區與緩衝區的交集，金色虛線是分析邊界。初始中心為 121.5170°E、25.0478°N，半徑 30 公里；與新北、桃園、台北、基隆及宜蘭相交，交集面積合計約 2,396.3 平方公里。

## 資料來源與處理

使用 geoBoundaries TWN ADM1，來源為 OpenStreetMap／Wambacher，代表年份為 2017。選出台北、新北、桃園、基隆、宜蘭、新竹市及新竹縣共 7 個行政區，保留原始幾何並整理顯示名稱。固定來源版本與 metadata 可由下方證據連結查核。

## 每次操作如何計算？

Turf.js 依中心與半徑執行 buffer（steps=128），以 booleanIntersects 篩選相交行政區，再用 intersect 產生交集多邊形，以 area 計算面積。MapLibre 更新交集圖層與數值。可下載結果 JSON，檢查中心、半徑、各區面積與輸出幾何。

## 網頁用了什麼架構？

GitHub Pages 提供 HTML、JavaScript 與行政區資料。載入後，Turf.js 7.4.0 在瀏覽器內執行幾何運算；MapLibre GL JS 5.24.0 以 WebGL 的面、線與點圖層呈現結果。每次改變半徑不需呼叫後端分析 API。

## 面積代表什麼？

數值是行政區落在緩衝區內的交集面積，不是整個行政區面積。30 公里緩衝區總面積約 2,827.4 平方公里，部分範圍不落在輸入行政區面內，因此與交集合計不同；不能未經分類就把差額全當作海域。

## 這次實作的界線

2017 年資料不是現行法定界線。距離緩衝區不是行車時間或實際服務範圍，Turf 面積是球面近似值。本次只有 7 個行政區，未做大規模效能測試或 Web Worker 分工，不能推論任意資料量都能流暢處理。

## 資料與技術來源

- [固定版行政區 GeoJSON](https://github.com/wmgeolab/geoBoundaries/blob/9469f09/releaseData/gbOpen/TWN/ADM1/geoBoundaries-TWN-ADM1.geojson)
- [Turf buffer](https://turfjs.org/docs/api/buffer)
- [Turf intersect](https://turfjs.org/docs/api/intersect)
- [Turf area](https://turfjs.org/docs/api/area)

## 本機執行

```sh
python3 -m http.server 8000
```

開啟 http://localhost:8000。各 repo 資產獨立，不需要 API key。Points／Lines 需要支援 WebGL 與 DecompressionStream 的現代瀏覽器。

## 證據與授權

查詢 SQL、核對表或結果見 `evidence/`；資料授權與歸屬見 `LICENSE-DATA.txt`，第三方程式授權保留於 `vendor/`。SQL 中的輸出路徑記錄原分析工作目錄，可依重現環境調整。內容更新：2026-11-03。
