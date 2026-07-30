<div align="center">

# ZaiGanMa (LiveStatus) for MCDReforged

[English](/README.md)  |  简体中文  |  [繁體中文](/README.zh-TW.md)

[反馈问题](https://github.com/man8in/zaiganma-livestatus/issues)  |  [提供建议](https://github.com/man8in/zaiganma-livestatus/discussions)

</div>

> [!NOTE]
> **ZaiGanMa (LiveStatus)** 是一款轻量级 MCDR 插件，在 TAB 列表和聊天框中实时显示玩家状态。基于 Minecraft 原版 Team 机制，完美兼容 Chat Head。

## 安装

在 MCDR 控制台执行：

`!!MCDR plugin install zaiganma_livestatus`

---

或者从 [Releases 页面](https://github.com/man8in/zaiganma-livestatus/releases) 下载 `.mcdr` 文件放入 `plugins` 文件夹。

## 使用说明

|指令|说明|
|---|---|
|`!!zgm`|查看自己的状态|
|`!!zgm <玩家名>`|查看他人状态|
|`!!zgm set <文字>`|设置状态|
|`!!zgm clear`|清除状态|
|`!!zgm color <颜色>`|设置状态颜色|
|`!!zgm clib`|查看可用颜色|
|`!!zgm lib`|查看状态库（点击使用）|
|`!!zgm lib add <文字>`|添加状态到库|
|`!!zgm lib remove <文字>`|从库删除状态|
|`!!zgm lib reload`|从文件重载状态库|
|`!!zgm lib reset`|重置状态库为默认|
|`!!zgm suggest`|随机推荐状态|
|`!!zgm chat`|查看聊天前缀状态|
|`!!zgm chat on/off`|开关聊天前缀|

> [!TIP]
> 在 `!!zgm lib` `!!zgm clib` `!!zgm suggest` 中点击状态可自动填入指令，按回车确认即可。

## 配置说明

首次运行自动生成 `config.json`：

|配置项|类型|默认值|说明|
|---|---|---|---|
|`show_in_tab`|`boolean`|`true`|TAB 列表显示状态|
|`show_in_chat`|`boolean`|`true`|聊天前缀显示状态|
|`max_length`|`integer`|`8`|状态最大字数|
|`allow_color`|`boolean`|`true`|允许自定义颜色|
|`manual_status_timeout`|`integer`|`180`|手动状态超时（分钟）|
|`lib_reload_permission_level`|`integer`|`3`|重载/重置所需权限等级|

### 支持的颜色

`black`、`dark_blue`、`dark_green`、`dark_aqua`、`dark_red`、`dark_purple`、`gold`、`gray`、`dark_gray`、`blue`、`green`、`aqua`、`red`、`light_purple`、`yellow`、`white`

也支持十六进制颜色，如 `#FF6B6B`。

## 依赖

|依赖|版本|必要性|
|---|---|---|
|MCDR|>= 2.13.0|✅ 必须|
|Minecraft Data API|*|❌ 可选|

## 开源协议

GNU General Public License v3.0

## 作者

man8in — [GitHub](https://github.com/man8in)
