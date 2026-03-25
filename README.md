# Open-LLM-VTuber-Traditional-Chinese-UI-Edition
Traditional Chinese fork of Open-LLM-VTuber with frontend config tools and chat UI enhancements.

# Open-LLM-VTuber 繁體中文版前端增強版

這是一個基於 **[Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber)** 修改的繁體中文 fork，主要目標是讓整體介面更適合繁體中文使用者，並補上較方便的前端設定功能。

目前這個版本的重點包括：

- 將專案中主要可見的簡體中文介面與提示改為繁體中文
- 新增前端設定入口，可直接調整 LLM / Prompt 相關內容
- 可在前端切換部分常用設定，而不必手動來回編輯設定檔
- 保留原本 Open-LLM-VTuber 的核心架構與使用方式

## 專案定位

如果你想要的是：

- 繁體中文介面
- 比較直覺的前端操作
- 仍然維持 Open-LLM-VTuber 原本的功能基礎

那這個版本就是在這個方向上做的整理與增強。

## 目前已加入的修改

### 1. 繁體中文化

我已經把專案中主要可見的中文內容改成繁體中文，包含：

- 前端介面主要文字
- 部分設定說明
- 後端設定檔中的中文註解與提示

### 2. 前端 LLM / Prompt 設定入口

前端首頁右上角新增了 `LLM / Prompt 設定` 按鈕，可進入額外的設定頁面，直接修改：

- LLM provider
- 模型與常用 API 參數
- system prompt

這些內容會寫回 [`conf.yaml`](/Users/'your computer'/文件/Open-LLM-VTuber-v1.2.1-zh/conf.yaml)。

### 3. 角色語音前端開關

目前前端頁面已加入 `角色語音：開 / 關` 按鈕，可以在不改後端設定的情況下，直接控制前端是否播放角色語音。

## 使用方式

### 啟動

如果你的環境已經安裝完成，直接執行：

```bash
uv run run_server.py
```

啟動後預設可在：

[http://localhost:12393](http://localhost:12393)

打開前端頁面。

### 設定檔

主要設定檔為：

- [`conf.yaml`](/Users/mumi/文件/Open-LLM-VTuber-v1.2.1-zh/conf.yaml)

如果你想調整：

- LLM provider
- 模型名稱
- system prompt
- TTS / ASR
- Live2D 模型

都可以從這個檔案或前端設定入口進行修改。

## 適合誰

這個版本比較適合：

- 主要使用繁體中文的使用者
- 想直接從前端調整部分 LLM 設定的人
- 已經知道 Open-LLM-VTuber，但想要一個比較順手的繁中版本的人

## 與原專案的關係

這不是獨立從零開始的新專案，而是建立在原始專案 **Open-LLM-VTuber** 之上的修改版本。

原專案：

- GitHub: [Open-LLM-VTuber / Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber)

原作者與貢獻者完成了整體架構、核心功能、模型整合、Live2D、語音互動與前後端系統。  
這個 fork 主要是針對：

- 繁體中文介面
- 前端設定體驗
- 本地使用上的便利性

做額外調整。

## Credit

特別致謝原始專案 **Open-LLM-VTuber** 與其作者、維護者、所有貢獻者。

本 fork 的核心能力與大部分架構皆來自原專案，若你認可這個專案的設計與功能，建議也一併支持原始倉庫：

- [Open-LLM-VTuber GitHub Repository](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber)

## License 與第三方資源

本專案沿用原專案的授權與第三方資源使用前提。  
特別是 Live2D 相關模型、素材與第三方模型服務，請依各自授權條款使用。

若你要商業使用，請務必自行確認：

- 原專案授權
- Live2D 模型授權
- 語音模型 / API 授權
- 第三方服務條款

## 備註

這個 fork 目前仍然是實用導向的調整版本，README 會隨功能再持續更新。  
如果後續又加入新的前端控制、設定頁或中文化範圍，我會再把文件補完整。
