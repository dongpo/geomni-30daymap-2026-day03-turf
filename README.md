# Geomni · Day 03 · 行政區交集 × Turf.js

[Open demo](https://dongpo.github.io/geomni-30daymap-2026-day03-turf/)

這個 demo 實際在瀏覽器執行 Turf.js buffer、intersect 與 area，再由 MapLibre GL JS 顯示結果。

操作：調整半徑，或點選地圖移動分析中心。幾何運算在載入資料後於瀏覽器完成。

中心初值 121.5170°E、25.0478°N。30 公里情境與 5 個行政區相交，交集面積合計約 2,396.3 km²。

行政區資料代表 2017 年，不是現行法定界線。半徑為示範參數，不是交通時間或服務範圍；面積是 Turf 球面近似值。

## Run locally

```sh
python3 -m http.server 8000
```

Open http://localhost:8000. Static site; no API keys. Each repository contains its own assets and does not depend on the other demos. Modern browser with WebGL and DecompressionStream required for Points/Lines.

## Evidence and licensing

See `evidence/`, `LICENSE-DATA.txt` and vendor notices. Prepared 2026-11-03. Original release query SQL records the analysis workflow; local file paths in SQL refer to the original analysis workspace. This is a geographic technology demonstration, not navigation or a legal boundary service.
