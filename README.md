<div align="center">

# ZaiGanMa (LiveStatus) for MCDReforged

[简体中文](/README.zh-CN.md)  |  [繁體中文](/README.zh-TW.md)

[Report an Issue](https://github.com/man8in/zaiganma-livestatus/issues)  |  [Share an Idea](https://github.com/man8in/zaiganma-livestatus/discussions)

</div>

> [!NOTE]
> **ZaiGanMa (LiveStatus)** is a lightweight MCDR plugin that allows players to set their own status tags and display them in the chat box and TAB list. Based on Minecraft's native Team mechanism.

## Installation

Run the following command in the MCDR console:

`!!MCDR plugin install zaiganma_livestatus`

Alternatively, download the `.mcdr` file from the [Releases page](https://github.com/man8in/zaiganma-livestatus/releases) and place it in your `plugins` folder.

## Usage

| Command | Description |
|---------|-------------|
| `!!zgm` | View your own status |
| `!!zgm <player>` | View another player's status |
| `!!zgm set <text>` | Set your status |
| `!!zgm clear` | Clear your status |
| `!!zgm color <color>` | Set status color |
| `!!zgm clib` | View available colors |
| `!!zgm lib` | View status library (click to use) |
| `!!zgm lib add <text>` | Add status to library |
| `!!zgm lib remove <text>` | Remove status from library |
| `!!zgm lib reload` | Reload status library from file |
| `!!zgm lib reset` | Reset status library to default (admin only) |
| `!!zgm suggest` | Get a random status suggestion |
| `!!zgm config` | View configuration panel (admin only) |

> [!TIP]
> Click on any status in `!!zgm lib`, `!!zgm clib`, `!!zgm suggest`, or `!!zgm config` to automatically fill the command into your chat bar, then press Enter to confirm.

## Configuration

The plugin generates `config.json` on first run:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `show_status` | `boolean` | `true` | Master switch for status display |
| `max_length` | `integer` | `8` | Max status text length |
| `allow_color` | `boolean` | `true` | Allow custom colors |
| `manual_status_timeout` | `integer` | `180` | Manual status timeout (minutes) |
| `library_entry_max_length` | `integer` | `8` | Max status library entry length |
| `lib_reload_permission_level` | `integer` | `3` | Permission level for reload/reset |

### Supported Colors

`black`, `dark_blue`, `dark_green`, `dark_aqua`, `dark_red`, `dark_purple`, `gold`, `gray`, `dark_gray`, `blue`, `green`, `aqua`, `red`, `light_purple`, `yellow`, `white`

Also supports hex colors like `#FF6B6B`.

## Dependencies

| Dependency | Version | Required |
|------------|---------|----------|
| MCDR | >= 2.13.0 | ✅ Yes |
| Minecraft Data API | * | ❌ Optional |

## License

GNU General Public License v3.0

## Author

man8in — [GitHub](https://github.com/man8in)