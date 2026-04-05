# 好味小姐 Podcast 搜尋

全集文字稿搜尋工具，支援關鍵字搜尋與模糊比對。

## 架構

```
podcast_wiki/
├── index.html              # 搜尋網頁
├── data/
│   ├── manifest.json       # 全部集數清單 (from RSS)
│   ├── search_index.json   # 合併搜尋索引
│   └── EP*.json            # 各集結構化文字稿
├── transcripts/            # Whisper 原始輸出
├── audio/                  # 下載的音檔 (不上傳 git)
├── process_episode.py      # 單集處理腳本
├── fetch_rss.py            # 抓取 RSS 清單
└── build_search_index.py   # 建立搜尋索引
```

## 使用方式

### 處理新集數
```bash
python3 process_episode.py <mp3_url> EP1 "EP1 標題" --model tiny
```

### 重建搜尋索引
```bash
python3 build_search_index.py
```

### 本地預覽
```bash
python3 -m http.server 8080
```
