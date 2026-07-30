<div align="center">

# ZaiGanMa (LiveStatus) for MCDReforged

[English](/README.md)  |  [简体中文](/README.zh-CN.md)  |  繁體中文

[回報問題](https://github.com/man8in/zaiganma-livestatus/issues)  |  [提供建議](https://github.com/man8in/zaiganma-livestatus/discussions)

</div>

> [!NOTE]
> **ZaiGanMa (LiveStatus)** 是一款輕量級 MCDR 插件，在 TAB 列表和聊天框中即時顯示玩家狀態。基於 Minecraft 原版 Team 機制，完美相容 Chat Head。

## 安裝

在 MCDR 主控台執行：

`!!MCDR plugin install zaiganma_livestatus`

---

或者從 [Releases 頁面](https://github.com/man8in/zaiganma-livestatus/releases) 下載 `.mcdr` 檔案放入 `plugins` 資料夾。

## 使用說明

|指令|說明|
|---|---|
|`!!zgm`|查看自己的狀態|
|`!!zgm <玩家名>`|查看他人狀態|
|`!!zgm set <文字>`|設定狀態|
|`!!zgm clear`|清除狀態|
|`!!zgm color <顏色>`|設定狀態顏色|
|`!!zgm color list`|查看可用顏色|
|`!!zgm lib`|查看狀態庫（點擊使用）|
|`!!zgm lib add <文字>`|新增狀態到庫|
|`!!zgm lib remove <文字>`|從庫刪除狀態|
|`!!zgm lib reload`|從檔案重載狀態庫|
|`!!zgm lib reset`|重設狀態庫為預設|
|`!!zgm suggest`|隨機推薦狀態|
|`!!zgm chat`|查看聊天前綴狀態|
|`!!zgm chat on/off`|開關聊天前綴|

> [!TIP]
> 在 `!!zgm lib` 中點擊狀態可自動填入指令，按 Enter 確認即可。

## 設定說明

首次執行自動生成 `config.json`：

|設定項|類型|預設值|說明|
|---|---|---|---|
|`show_in_tab`|`boolean`|`true`|TAB 列表顯示狀態|
|`show_in_chat`|`boolean`|`true`|聊天前綴顯示狀態|
|`max_length`|`integer`|`8`|狀態最大字數|
|`allow_color`|`boolean`|`true`|允許自訂顏色|
|`manual_status_timeout`|`integer`|`180`|手動狀態超時（分鐘）|
|`lib_reload_permission_level`|`integer`|`3`|重載/重設所需權限等級|

### 支援的顏色

`black`、`dark_blue`、`dark_green`、`dark_aqua`、`dark_red`、`dark_purple`、`gold`、`gray`、`dark_gray`、`blue`、`green`、`aqua`、`red`、`light_purple`、`yellow`、`white`

也支援十六進位顏色，如 `#FF6B6B`。

## 依賴

|依賴|版本|必要性|
|---|---|---|
|MCDR|>= 2.0.0|✅ 必須|
|Minecraft Data API|*|❌ 選用|

## 開源協議

GNU General Public License v3.0

## 作者

man8in — [GitHub](https://github.com/man8in)