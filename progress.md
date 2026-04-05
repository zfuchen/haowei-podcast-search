# 好味小姐 Podcast Wiki 進度

更新日期：2026-04-05

## 目前狀態
- 已完成集數：1（EP1）
- 待處理：EP2 ~ EP304

## 集數狀態

| 集數 | 標題 | 轉錄 | Diarization | 人工確認 | 備註 |
|------|------|------|-------------|----------|------|
| EP1  | 當Youtuber幹嘛唸工業設計？ | ✅ tiny | ✅ 完成 | ⏳ 待試聽 | 說話者：很煩/脆脆/阿斷 |

## 說話者對應表
`data/speaker_mapping.json`
- SPEAKER_00 → 很煩（攝影師）
- SPEAKER_01 → 阿斷（剪輯師）
- SPEAKER_02 → 脆脆
⚠️ 注意：每集的 SPEAKER 編號不一定相同，每集 diarization 後需重新確認

## 工作流程（每一集）
1. 下載音檔 + 轉錄：`python3 process_episode.py <url> <ep_id> "<title>"`
2. 轉 WAV：`ffmpeg -i audio/<ep_id>.mp3 -ar 16000 -ac 1 audio/<ep_id>.wav -y`
3. Diarization（背景）：`nohup python3 diarize_episode.py <ep_id> > /tmp/diarize_<ep_id>.log 2>&1 &`
4. 等 Telegram 通知，填寫 speaker_mapping.json 人名
5. 套用人名：`python3 apply_speakers.py <ep_id>`
6. 重建索引：`python3 build_search_index.py`
7. 刪除音檔：`rm audio/<ep_id>.mp3 audio/<ep_id>.wav`
8. git commit & push

## GitHub Pages
- Repo：https://github.com/zfuchen/haowei-podcast-search
- URL：https://zfuchen.github.io/haowei-podcast-search/
