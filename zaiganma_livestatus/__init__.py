import json
import os
import time
import random
import time
import re
from typing import Dict, Optional, Tuple
from mcdreforged.api.all import *
from mcdreforged.api.types import PluginServerInterface, Info, CommandSource
from mcdreforged.minecraft.rtext.click_event import RClickAction
from mcdreforged.handler.impl import VanillaHandler
from mcdreforged.info_reactor.info_filter import InfoFilter
from mcdreforged.info_reactor.info import InfoActionFlag

class TeamMessageFilter(InfoFilter):
    def filter_server_info(self, info: 'Info') -> bool:
        content = info.content
        if info.is_player:
            return True
        team_patterns = [
            r'Removed team \[.*?\]',
            r'Created team \[.*?\]',
            r'Team prefix set to .*',
            r'Added .* to team \[.*?\]',
        ]
        for pattern in team_patterns:
            if re.search(pattern, content):
                info.action_flag = InfoActionFlag.discarded()
                return False
        return True

class ZaiGanMaHandler(VanillaHandler):
    def get_name(self) -> str:
        return 'zaiganma_handler'
    def pre_parse_server_stdout(self, text: str):
        text = super().pre_parse_server_stdout(text)
        text = re.sub(
            r'^(.*?\[[^]]+\].*?)\[[^]]+\]\s+',
            r'\1',
            text
        )
        return text
    def parse_server_stdout(self, text: str):
        info = super().parse_server_stdout(text)
        if info.player is None:
            m = re.fullmatch(r'<\[[^]]+](?P<name>[^>]+)> (?P<message>.*)', info.content)
            if m is not None:
                name = m['name'].strip()
                if self._verify_player_name(name):
                    info.player, info.content = name, m['message']
        return info

PLUGIN_METADATA = {
    'version': '1.0.2',                    
    'name': 'ZaiGanMa (LiveStatus)',       
    'dependencies': {'minecraft_data_api': '*'},
    'description': '实时显示玩家当前行为状态'
}

CONFIG_FILE = None
DATA_FILE = None
LIBRARY_FILE = None

DEFAULT_CONFIG = {
    "show_status": True,
    "chat_prefix_style": "text",
    "default_status": "在线",      
    "max_length": 8,              
    "allow_color": True,
    "manual_status_timeout": 180,  
    "library_entry_max_length": 8,  
    "lib_reset_permission_level": 3,
    "color_name_to_code": {
        "black": "§0", "dark_blue": "§1", "dark_green": "§2",
        "dark_aqua": "§3", "dark_red": "§4", "dark_purple": "§5",
        "gold": "§6", "gray": "§7", "dark_gray": "§8",
        "blue": "§9", "green": "§a", "aqua": "§b",
        "red": "§c", "light_purple": "§d", "yellow": "§e",
        "white": "§f"
    }
}
DEFAULT_LIBRARY = {
    "library": [
        {"text": "挖矿中"},
        {"text": "建筑中"},
        {"text": "摸鱼中"},
        {"text": "钓鱼中"},
        {"text": "战斗中"},
        {"text": "AFK"},
        {"text": "探索中"},
        {"text": "下矿中"},
        {"text": "飞行中"},
        {"text": "来PVP"},
        {"text": "收东西"},
        {"text": "别打扰"}
    ],
    "color_library": [
        {"name": "gold", "display": "金色"},
        {"name": "red", "display": "红色"},
        {"name": "green", "display": "绿色"},
        {"name": "aqua", "display": "青色"},
        {"name": "blue", "display": "蓝色"},
        {"name": "light_purple", "display": "浅紫"},
        {"name": "yellow", "display": "黄色"},
        {"name": "white", "display": "白色"},
        {"name": "gray", "display": "灰色"},
        {"name": "dark_green", "display": "深绿"},
        {"name": "dark_red", "display": "深红"},
        {"name": "dark_aqua", "display": "深青"},
        {"name": "dark_blue", "display": "深蓝"},
        {"name": "dark_purple", "display": "深紫"},
        {"name": "dark_gray", "display": "深灰"},
        {"name": "black", "display": "黑色"}
    ],
    "max_custom": 20,
    "allow_player_add": True,
    "allow_player_remove": True,
    "library_entry_max_length": 8
}
config = {}              # 存储当前生效的配置（从 config.json 加载）
status_data = {}         # 存储所有玩家的状态数据（从 status_data.json 加载）
server_instance = None     # 保存 MCDR 服务器实例，方便在其他函数里使用
library_data = {}


def load_config():
    global config
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if not isinstance(config, dict):
                config = DEFAULT_CONFIG.copy()
                save_config()
        except Exception:
            config = DEFAULT_CONFIG.copy()
            save_config()
    else:
        config = DEFAULT_CONFIG.copy()
        save_config()

def save_config():
    os.makedirs(os.path.dirname(CONFIG_FILE),exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            config,
            f,
            ensure_ascii=False,
            indent=4
        )


def load_data():
    global status_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
    else:
        status_data = {}
        save_data()

def save_data():
    """保存当前玩家数据到 status_data.json"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(status_data, f, indent=4, ensure_ascii=False)

def load_library():
    global library_data
    if os.path.exists(LIBRARY_FILE):
        with open(LIBRARY_FILE, 'r', encoding='utf-8') as f:
            library_data = json.load(f)
        save_library()
    else:
        library_data = DEFAULT_LIBRARY.copy()
        save_library()

def save_library(): 
    with open(LIBRARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(library_data, f, indent=4, ensure_ascii=False)


def get_player_status(player: str):
    if player not in status_data:
        status_data[player] = {
            "manual_text": "",
            "manual_color": "",
            "manual_time": 0,
            "chat_enabled": True,
        }
        save_data()
    if not isinstance(status_data[player], dict):
        status_data[player] = {
            "manual_text": "",
            "manual_color": "",
            "manual_time": 0,
            "chat_enabled": True,
        }
        save_data()
    return status_data[player]

def get_display_status(player: str) -> Tuple[str, str]:
    if player.lower().startswith("bot_"):
        return "假人", "§7"
    data = get_player_status(player)
    if not isinstance(data, dict):
        data = {
            "manual_text": "",
            "manual_color": "",
            "manual_time": 0,
            "chat_enabled": True
        }
        status_data[player] = data
        save_data()
    manual_text = data.get("manual_text", "").strip()
    if manual_text:
        timeout = (config or {}).get("manual_status_timeout", 180)
        if timeout > 0:
            set_time = data.get("manual_time", 0)
            if time.time() - set_time > timeout * 60:
                data["manual_text"] = ""
                data["manual_color"] = ""
                data["manual_time"] = 0
                status_data[player] = data
                save_data()
                return config.get("default_status", "在线"), ""
        text = manual_text
        color = data.get("manual_color", "")
        color_code = ""
        if color and config.get("allow_color", True):
            if color.startswith("#"):
                color_code = hex_to_minecraft_color(color)
            else:
                color_code = config.get("color_name_to_code", {}).get(str(color).lower(), "")
        return text, color_code
    return config.get("default_status", "在线"), ""

def hex_to_minecraft_color(hex_color: str) -> str:
    color_map = {
        "#FF0000": "§c", "#00FF00": "§a", "#0000FF": "§9",
        "#FFFF00": "§e", "#FF00FF": "§d", "#00FFFF": "§b",
        "#000000": "§0", "#FFFFFF": "§f", "#808080": "§7",
        "#FF6B6B": "§c", "#4ECDC4": "§b", "#45B7D1": "§b",
        "#96CEB4": "§a", "#FFEAA7": "§e", "#DDA0DD": "§d"
    }
    if hex_color.upper() in color_map:
        return color_map[hex_color.upper()]
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        avg = (r + g + b) // 3
        if avg > 200:
            return "§f"
        elif avg > 100:
            return "§7"
        else:
            return "§8"
    except:
        return "§f"

def get_chat_prefix(player):
    if not config.get("show_status", True):
        return ""
    status = get_player_status(player)
    if not isinstance(status, dict):
        return "未知"
    manual = status.get("manual_text", "")
    if manual:
        return manual
    return config.get("default_status", "在线")

def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    get_player_status(player)
    data = get_player_status(player)
    state = data.get("manual_text", "").strip()
    if state:
        apply_state_team(server, player, state)
    elif state and not config.get("show_status", True):
        remove_state_team(server, player)  

def on_player_left(server: PluginServerInterface, player: str):
    pass

def set_state(self, player: str, state: str) -> None:
    self._execute(f'/team leave {player}')
    self._create_state_team(player, state)
    self._join_state_team(player)

def status_list(server: PluginServerInterface) -> Dict[str, str]:
    if not config.get("show_status", True) or not config.get("show_in_tab", True):
        return {}
    result = {}
    try:
        minecraft_data_api = server.get_plugin_instance('minecraft_data_api')
        for player in minecraft_data_api.get_server_player_list():
            text, color = get_display_status(player)
            if text:
                result[player] = f"{color}{text} {player}"
            else:
                result[player] = player
    except:
        pass
    return result

def register_commands(server: PluginServerInterface):
    base_node = Literal("!!zgm")
    # --- 子指令：!!zgm（无参数）--- 
    base_node.runs(lambda src: show_self_status(src))
    # --- 子指令：!!zgm help ---
    base_node.then(
        Literal("help").runs(lambda src: show_help(src))
    )
    # --- 子指令：!!zgm <玩家名> ---
    base_node.then(
        Text("player").runs(lambda src, ctx: show_player_status(src, ctx["player"]))
    )
    # --- 子指令：!!zgm set <文字> ---
    base_node.then(
        Literal("set").then(
            GreedyText("text").runs(lambda src, ctx: set_manual_status(src, ctx["text"]))
        )
    )
    # --- 子指令：!!zgm color/col <颜色> ---
    base_node.then(
        Literal("color").then(
            Text("color").runs(lambda src, ctx: set_status_color(src, ctx["color"]))
        ).then(
        Literal("col").then(
            Text("color").runs(lambda src, ctx: set_status_color(src, ctx["color"]))
            )
        )
    )
    # --- 子指令：!!zgm clib ---
    base_node.then(
        Literal("clib").runs(lambda src, ctx: show_color_library(src))
    )
    # --- 子指令：!!zgm clear ---
    base_node.then(
        Literal("clear").runs(lambda src: clear_manual_status(src))
    )
    # --- 子指令：!!zgm suggest/sug ---
    base_node.then(
        Literal("suggest").runs(lambda src: suggest_status(src))
        ).then(
        Literal("sug").runs(lambda src: suggest_status(src))
    )
    # --- 子指令：!!zgm lib ---
    base_node.then(
        Literal("lib").runs(lambda src: show_library(src)).then(
            Literal("add").then(
                GreedyText("text").runs(lambda src, ctx: add_to_library(src, ctx["text"]))
            )
        ).then(
            Literal("remove").then(
                GreedyText("text").runs(lambda src, ctx: remove_from_library(src, ctx["text"]))
            )
            ).then(
            Literal("rem").then(
                GreedyText("text").runs(lambda src, ctx: remove_from_library(src, ctx["text"]))
            )
        ).then(
            Literal("reset").runs(lambda src, ctx: reset_library(src))
        ).then(
            Literal("reload").runs(lambda src, ctx: reload_library(src))
        )
    )
    # --- 子指令：!!zgm config ---
    base_node.then(
        Literal("config").runs(lambda src: show_config_panel(src)).then(
            Literal("panel").runs(lambda src: show_config_panel(src))
        ).then(
            Literal("show_status").then(
                Literal("true").runs(lambda src: set_config_bool(src, "show_status", True))
            ).then(
                Literal("false").runs(lambda src: set_config_bool(src, "show_status", False))
            )
        ).then(
            Literal("allow_player_toggle_chat").then(
                Literal("true").runs(lambda src: set_config_bool(src, "allow_player_toggle_chat", True))
            ).then(
                Literal("false").runs(lambda src: set_config_bool(src, "allow_player_toggle_chat", False))
            )
        ).then(
            Literal("allow_color").then(
                Literal("true").runs(lambda src: set_config_bool(src, "allow_color", True))
            ).then(
                Literal("false").runs(lambda src: set_config_bool(src, "allow_color", False))
            )
        ).then(
            # 字符串配置
            Literal("chat_prefix_style").then(
            Text("value").runs(lambda src, ctx: set_config_str(src, "chat_prefix_style", ctx["value"]))
            )
        ).then(
            Literal("default_status").then(
                GreedyText("value").runs(lambda src, ctx: set_config_str(src, "default_status", ctx["value"]))
            )
        ).then(
            # 整数配置
            Literal("max_length").then(
                Integer("value").runs(lambda src, ctx: set_config_int(src, "max_length", ctx["value"]))
            )
        ).then(
            Literal("manual_status_timeout").then(
                Integer("value").runs(lambda src, ctx: set_config_int(src, "manual_status_timeout", ctx["value"]))
            )
        ).then(
            Literal("library_entry_max_length").then(
                Integer("value").runs(lambda src, ctx: set_config_int(src, "library_entry_max_length", ctx["value"]))
            )
        ).then(
            Literal("lib_reload_permission_level").then(
                Integer("value").runs(lambda src, ctx: set_config_int(src, "lib_reload_permission_level", ctx["value"]))
            )
        )
    )
    server.register_command(base_node)


def show_help(src: CommandSource):
    """显示所有可用指令（点击使用）"""
    src.reply("§6=== §eZaiGanMa (LiveStatus) §6帮助 ===§r")
    src.reply("§7")
    src.reply("§6【基本指令】")
    cmd1 = RText("  !!zgm").set_click_event(RClickAction.suggest_command, "!!zgm")
    cmd1 += RText("  §f查看自己的状态")
    src.reply(cmd1)
    cmd2 = RText("  !!zgm <玩家名>").set_click_event(RClickAction.suggest_command, "!!zgm ")
    cmd2 += RText("  §f查看他人状态")
    src.reply(cmd2)
    cmd3 = RText("  !!zgm set <文字>").set_click_event(RClickAction.suggest_command, "!!zgm set ")
    cmd3 += RText("  §f设置手动状态")
    src.reply(cmd3)
    cmd4 = RText("  !!zgm clear/cle").set_click_event(RClickAction.suggest_command, "!!zgm clear")
    cmd4 += RText("  §f清除手动状态")
    src.reply(cmd4)
    cmd5 = RText("  !!zgm color <颜色>").set_click_event(RClickAction.suggest_command, "!!zgm color ")
    cmd5 += RText("  §f设置状态颜色")
    src.reply(cmd5)
    cmd6 = RText("  !!zgm clib <颜色>").set_click_event(RClickAction.suggest_command, "!!zgm clib ")
    cmd6 += RText("  §f查看颜色库")
    src.reply(cmd6)
    src.reply("§7")
    src.reply("§6【状态库】")
    cmd7 = RText("  !!zgm lib").set_click_event(RClickAction.suggest_command, "!!zgm lib")
    cmd7 += RText("  §f查看状态库")
    src.reply(cmd7)
    cmd8 = RText("  !!zgm lib add <文字>").set_click_event(RClickAction.suggest_command, "!!zgm lib add ")
    cmd8 += RText("  §f添加状态到库")
    src.reply(cmd8)
    cmd9 = RText("  !!zgm lib remove/rem <文字>").set_click_event(RClickAction.suggest_command, "!!zgm lib remove ")
    cmd9 += RText("  §f从库删除状态")
    src.reply(cmd9)
    cmd10 = RText("  !!zgm lib reset").set_click_event(RClickAction.suggest_command, "!!zgm lib reset")
    cmd10 += RText("  §f重置状态库")
    src.reply(cmd10)
    cmd11 = RText("  !!zgm lib reload").set_click_event(RClickAction.suggest_command, "!!zgm lib reload")
    cmd11 += RText("  §f重载状态库")
    src.reply(cmd11)
    cmd12 = RText("  !!zgm suggest/sug").set_click_event(RClickAction.suggest_command, "!!zgm suggest")
    cmd12 += RText("  §f随机推荐状态")
    src.reply(cmd12)
    src.reply("§7")
    src.reply("§6【管理员设置】")
    cmd13 = RText("  !!zgm config").set_click_event(RClickAction.suggest_command, "!!zgm config")
    cmd13 += RText("  §f查看配置面板）")
    src.reply(cmd13)

    src.reply("§6====================================§r")

def show_config_panel(src: CommandSource):
    """显示完整配置面板（可点击调整）"""
    if src.is_player and src.get_permission_level() < 3:
        src.reply("§c你没有权限执行此操作（需要管理员权限）")
        return

    is_player = src.is_player

    src.reply("§6=== §eZaiGanMa 完整设置面板 §6===§r")
    src.reply("§7")

    # 1. 状态总开关（整合了 TAB 和聊天前缀）
    src.reply("§6【状态总开关】")
    src.reply(f"§7当前: §f{'开启' if config.get('show_status', True) else '关闭'}")
    if is_player:
        line = RTextList()
        line.append(RText("[开启] ", RColor.green).set_click_event(RClickAction.suggest_command, "!!zgm config show_status true"))
        line.append(RText("[关闭] ", RColor.red).set_click_event(RClickAction.suggest_command, "!!zgm config show_status false"))
        src.reply(line)
    src.reply("§7")

    #允许自定义颜色
    src.reply("§6【允许自定义颜色】")
    src.reply(f"§7当前: §f{'开启' if config.get('allow_color', True) else '关闭'}")
    if is_player:
        line = RTextList()
        line.append(RText("[开启] ", RColor.green).set_click_event(RClickAction.suggest_command, "!!zgm config allow_color true"))
        line.append(RText("[关闭] ", RColor.red).set_click_event(RClickAction.suggest_command, "!!zgm config allow_color false"))
        src.reply(line)
    src.reply("§7")

    #默认状态
    src.reply("§6【默认状态】")
    src.reply(f"§7当前: §f{config.get('default_status', '在线')}")
    if is_player:
        line = RTextList()
        line.append(RText("[点击设置] ", RColor.green).set_click_event(RClickAction.suggest_command, "!!zgm config default_status "))
        src.reply(line)
    src.reply("§7")

    #状态最大字数
    src.reply("§6【状态最大字数】")
    src.reply(f"§7当前: §f{config.get('max_length', 8)} 字")
    if is_player:
        line = RTextList()
        line.append(RText("[点击设置] ", RColor.green).set_click_event(RClickAction.suggest_command, "!!zgm config max_length "))
        src.reply(line)
    src.reply("§7")

    #手动状态超时
    src.reply("§6【手动状态超时】")
    src.reply(f"§7当前: §f{config.get('manual_status_timeout', 180)} 分钟" + (" §7(永久)" if config.get('manual_status_timeout', 180) == 0 else ""))
    if is_player:
        line = RTextList()
        line.append(RText("[点击设置] ", RColor.green).set_click_event(RClickAction.suggest_command, "!!zgm config manual_status_timeout "))
        src.reply(line)
    src.reply("§7")

    #状态库最大字数
    src.reply("§6【状态库最大字数】")
    src.reply(f"§7当前: §f{config.get('library_entry_max_length', 8)} 字")
    if is_player:
        line = RTextList()
        line.append(RText("[点击设置] ", RColor.green).set_click_event(RClickAction.suggest_command, "!!zgm config library_entry_max_length "))
        src.reply(line)
    src.reply("§7")

    #重载/重置权限等级
    src.reply("§6【重载/重置权限等级】")
    src.reply(f"§7当前: §f{config.get('lib_reload_permission_level', 3)}")
    if is_player:
        line = RTextList()
        line.append(RText("[点击设置] ", RColor.green).set_click_event(RClickAction.suggest_command, "!!zgm config lib_reload_permission_level "))
        src.reply(line)
    src.reply("§7")

    src.reply("§7💡 点击 [点击设置] 或 [开启]/[关闭] 后，按回车确认")
    src.reply("§6================================§r")

def _get_team_name(player: str) -> str:
    clean_name = ''.join(c for c in player if c.isalnum() or c == '_')
    return f"zgm_{clean_name[:12]}"

def _execute(server, cmd: str) -> None:
    server.execute(cmd)

def apply_state_team(server: PluginServerInterface, player: str, state: str) -> None:
    team_name = _get_team_name(player)
    data = get_player_status(player)
    color = data.get("manual_color", "").strip()
    if color and color in ["black", "dark_blue", "dark_green", "dark_aqua", "dark_red", 
                           "dark_purple", "gold", "gray", "dark_gray", "blue", 
                           "green", "aqua", "red", "light_purple", "yellow", "white"]:
        prefix_json = f'{{"text":"[{state}] ","color":"{color}","bold":true}}'
    else:
        prefix_json = f'{{"text":"[{state}] ","bold":true}}'
    _execute(server, f'/team remove {team_name}')
    _execute(server, f'/team add {team_name}')
    _execute(server, f'/team modify {team_name} prefix {prefix_json}')
    _execute(server, f'/team join {team_name} {player}')

def remove_state_team(server: PluginServerInterface, player: str) -> None:
    """移除玩家的状态 Team"""
    team_name = _get_team_name(player)
    _execute(server, f'/team remove {team_name}')

def show_self_status(src: CommandSource):
    """处理 !!zgm - 显示自己的状态"""
    if not src.is_player:
        src.reply("§c此指令仅限玩家使用")
        return
    player = src.player
    data = get_player_status(player)
    text, color = get_display_status(player)
    has_manual = bool(data.get("manual_text", "").strip())
    src.reply(f"§6=== §e{player} §6的状态 ===§r")
    src.reply(f"§7显示: {color}{text}§r")
    src.reply(f"§7模式: {'§a手动设置' if has_manual else '§7自动检测'}§r")
    if has_manual and data.get("manual_color"):
        src.reply(f"§7颜色: {data['manual_color']}§r")
    
def show_player_status(src: CommandSource, player: str):
    """处理 !!zgm get <player>"""
    if player not in status_data:
        src.reply(f"§c玩家 {player} 暂无状态数据")
        return
    
    data = get_player_status(player)
    text, color = get_display_status(player)
    has_manual = bool(data.get("manual_text", "").strip())
    
    src.reply(f"§6=== §e{player} §6的状态 ===§r")
    src.reply(f"§7显示: {color}{text}§r")
    src.reply(f"§7模式: {'§a手动设置' if has_manual else '§7自动检测'}§r")
    
def set_manual_status(src: CommandSource, text: str):
    if not src.is_player:
        src.reply("§c此指令仅限玩家使用")
        return
    if not config.get("show_status", True):
        src.reply("§c状态显示已关闭，无法设置新状态")
        return
    player = src.player
    text = text.strip()
    max_len = config.get("max_length", 8)
    if len(text) > max_len:
        src.reply(f"§c状态文字不能超过 {max_len} 个字，当前 {len(text)} 个字")
        return
    data = get_player_status(player)
    data["manual_text"] = text
    data["manual_time"] = time.time()
    save_data()
    apply_state_team(src.get_server(), player, text)
    src.reply(f"§a✅ 状态已更新: [{text}]")

def set_status_color(src: CommandSource, color: str):
    """处理 !!zgm color <color>"""
    if not src.is_player:
        src.reply("§c此指令仅限玩家使用")
        return
    if not config.get("allow_color", True):
        src.reply("§c服务器已禁用自定义颜色")
        return
    player = src.player
    data = get_player_status(player)
    if not data.get("manual_text", "").strip():
        src.reply("§c请先设置状态文字 (!!zgm set <文字>)")
        return
    color_name_to_code = config.get("color_name_to_code", {})
    if str(color).lower() in color_name_to_code or str(color).startswith("#"):
        data["manual_color"] = color
        save_data()
        state = data.get("manual_text", "").strip()
        if state:
            apply_state_team(src.get_server(), player, state)
        display_text, color_code = get_display_status(player)
        src.reply(f"§a✅ 颜色已更新: {color_code}{display_text}§r")
    else:
        src.reply(f"§c不支持的颜色: {color}")
        src.reply(f"§7支持: {', '.join(list(color_name_to_code.keys())[:10])}... 或十六进制 #RRGGBB")



def clear_manual_status(src: CommandSource):
    if not src.is_player:
        src.reply("§c此指令仅限玩家使用")
        return
    player = src.player
    data = get_player_status(player)
    if not data.get("manual_text", "").strip():
        src.reply("§7你当前没有设置状态")
        return
    data["manual_text"] = ""
    data["manual_color"] = ""
    save_data()
    remove_state_team(src.get_server(), player)
    src.reply("§a✅ 已清除状态")



def suggest_status(src: CommandSource):
    """随机推荐状态（从状态库中选），可点击直接填入"""
    if not src.is_player:
        src.reply("§c此指令仅限玩家使用")
        return 
    library = library_data.get("library", [])
    if not library:
        src.reply("§c状态库为空，请联系管理员添加")
        return   
    suggestion = random.choice(library)
    text = suggestion.get("text", "")   
    src.reply("§7✨ 推荐状态：")
    if src.is_player:
        click_text = RText(f"§f[{text}]§r").set_click_event(
            RClickAction.suggest_command, f"!!zgm set {text}"
        )
    else:
        click_text = RText(f"§f[{text}]§r")
    src.reply(click_text)
    src.reply(f"§7提示: 点击上方状态后按 Enter 确认，或输入 §6!!zgm lib §7查看全部状态")

def show_library(src: CommandSource):
    """显示状态库，每个状态可点击直接设置"""
    library = library_data.get("library", [])
    if not library:
        src.reply("§7状态库为空")
        return
    is_player = src.is_player
    src.reply("§6===  状态库（点击填入聊天栏） ===§r")
    line = RTextList()
    for i, item in enumerate(library):
        text = item.get("text", "")
        if is_player:
            click_text = RText(f"§f[{text}]§r").set_click_event(
                RClickAction.suggest_command, f"!!zgm set {text}"
            )
        else:
            click_text = RText(f"§f[{text}]§r")
        line.append(click_text)
        if i < len(library) - 1:
            line.append(RText("  "))
    src.reply(line)
    src.reply("§7提示: 点击状态后按 Enter 确认，或使用 §6!!zgm suggest §7随机推荐")

def show_color_library(src: CommandSource):
    """显示所有可用颜色（可点击）"""
    color_library = library_data.get("color_library", [])
    if not color_library:
        src.reply("§7颜色库为空")
        return
    is_player = src.is_player
    src.reply("§6===  颜色库（点击填入聊天栏） ===§r")
    line = RTextList()
    for i, item in enumerate(color_library):
        name = item.get("name", "")
        display = item.get("display", name)
        if is_player:
            click_text = RText(f"§f{display}§r").set_click_event(
                RClickAction.suggest_command, f"!!zgm color {name}"
            )
        else:
            click_text = RText(f"§f{display}§r")
        line.append(click_text)
        if i < len(color_library) - 1:
            line.append(RText("  "))
    src.reply(line)
    src.reply("§7提示: 点击颜色后按 Enter 确认，颜色会应用到当前状态")    

def use_library_status(src: CommandSource, index: int):
    """使用状态库中的某条状态"""
    library = library_data.get("library", [])
    if index < 1 or index > len(library):
        src.reply(f"§c编号无效，请输入 1-{len(library)}")
        return
    item = library[index - 1]
    text = item.get("text", "")
    player = src.player
    data = get_player_status(player)
    data["manual_text"] = text
    data["manual_time"] = time.time()
    save_data()
    src.reply(f"§a✅ 已使用状态库: {text}")

def add_to_library(src: CommandSource, text: str):
    if not check_library_text_length(text):
        max_len = library_data.get("library_entry_max_length", 8)
        min_len = library_data.get("library_entry_min_length", 1)
        src.reply(f"§c状态文字长度必须在 {min_len}-{max_len} 个字之间")
        return
    library = library_data.get("library", [])
    for item in library:
        if item.get("text") == text:
            src.reply(f"§c状态「{text}」已存在于库中")
            return
    library.append({"text": text})
    save_library()
    src.reply(f"§a✅ 已添加: {text}")

def remove_from_library(src: CommandSource, text: str):
    """通过文字从状态库删除状态"""
    library = library_data.get("library", [])
    text = text.strip()
    found = None
    for item in library:
        if item.get("text") == text:
            found = item
            break
    if found is None:
        src.reply(f"§c状态「{text}」不存在于库中")
        return
    library.remove(found)
    save_library()
    src.reply(f"§a✅ 已删除: {text}")


def check_library_text_length(text: str) -> bool:
    max_len = library_data.get("library_entry_max_length", 8)
    min_len = library_data.get("library_entry_min_length", 1)
    if len(text) < min_len or len(text) > max_len:
        return False
    return True

def reset_library(src: CommandSource):
    """重置状态库为默认值（覆盖文件）"""
    required_level = config.get("lib_reload_permission_level", 3)
    if src.is_player and src.get_permission_level() < required_level:
        src.reply("§c你没有权限执行此操作（需要高级管理员权限）")
        return
    global library_data
    try:
        library_data = DEFAULT_LIBRARY.copy()
        with open(LIBRARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(library_data, f, indent=4, ensure_ascii=False)
        with open(LIBRARY_FILE, 'r', encoding='utf-8') as f:
            library_data = json.load(f)
        src.reply("§a✅ 状态库已重置为默认值")
        src.reply(f"§7共加载 {len(library_data.get('library', []))} 条状态")
    except Exception as e:
        src.reply(f"§c重置失败: {e}")
        import traceback
        traceback.print_exc()

def reload_library(src: CommandSource):
    """从文件重新加载状态库（不修改文件）"""
    global library_data
    try:
        if os.path.exists(LIBRARY_FILE):
            with open(LIBRARY_FILE, 'r', encoding='utf-8') as f:
                library_data = json.load(f)
            src.reply("§a✅ 状态库已从文件重新加载")
        else:
            library_data = DEFAULT_LIBRARY.copy()
            save_library()
            src.reply("§a✅ 状态库文件不存在，已恢复默认")
    except Exception as e:
        src.reply(f"§c重载失败: {e}")

def on_load(server: PluginServerInterface, old):
    global server_instance, CONFIG_FILE, DATA_FILE, LIBRARY_FILE
    server.register_server_handler(ZaiGanMaHandler())
    server_instance = server
    data_folder = server.get_data_folder()
    CONFIG_FILE = os.path.join(server.get_data_folder(),"config.json")
    DATA_FILE = os.path.join(data_folder, 'status_data.json')
    LIBRARY_FILE = os.path.join(data_folder, 'status_library.json')
    load_config()
    load_data()
    load_library()
    register_commands(server)
    server.register_event_listener('on_player_joined', on_player_joined)
    server.register_event_listener('on_player_left', on_player_left)
    server.register_info_filter(TeamMessageFilter())
    server.register_event_listener('on_tab_list', status_list)
    try:
        for player in server.get_plugin_instance("minecraft_data_api").get_server_player_list():
            get_player_status(player)
    except:
        pass
    server.logger.info(f"§a[ZaiGanMa] §r插件已加载 v{PLUGIN_METADATA['version']}")

def on_unload(server: PluginServerInterface):
    save_data()
    save_library()
    server.logger.info("§c[ZaiGanMa] §r插件已卸载")

def set_max_length(src: CommandSource, length: int):
    """设置状态最大字数（管理员）"""
    if src.is_player and src.get_permission_level() < 3:
        src.reply("§c你没有权限执行此操作（需要管理员权限）")
        return
    admin = src.player if src.is_player else "控制台"
    if length < 1:
        src.reply("§c字数不能小于 1")
        return
    if length > 20:
        src.reply("§c字数不能超过 20")
        return
    config["max_length"] = length
    save_config()
    server = src.get_server()
    server.broadcast(f"§a[ZaiGanMa] §e{admin} §a已将状态最大字数设为: {length} 字")
    src.reply(f"§a✅ 状态最大字数已设为: {length} 字")

def set_config_bool(src: CommandSource, key: str, value: bool):
    """设置布尔值配置（管理员）"""
    if src.is_player and src.get_permission_level() < 3:
        src.reply("§c你没有权限执行此操作（需要管理员权限）")
        return
    admin = src.player if src.is_player else "控制台"
    config[key] = value
    save_config()
    server = src.get_server()
    if key == "show_status":
        if value == False:
            try:
                players = list(status_data.keys())
                for player in players:
                    remove_state_team(server, player)
                    data = get_player_status(player)
                    data["manual_text"] = ""
                    data["manual_color"] = ""
                    save_data()
                server.broadcast(f"§c[ZaiGanMa] §e{admin} §c关闭了状态显示，已清空所有玩家状态")
            except Exception as e:
                src.reply(f"§c清空状态失败: {e}")
        else:
            server.broadcast(f"§a[ZaiGanMa] §e{admin} §a开启了状态显示")
    else:
        src.reply(f"§a✅ {key} 已设为: {value}")

def set_config_str(src: CommandSource, key: str, value: str):
    """设置字符串配置（管理员）"""
    if src.is_player and src.get_permission_level() < 3:
        src.reply("§c你没有权限执行此操作（需要管理员权限）")
        return
    admin = src.player if src.is_player else "控制台"
    config[key] = value
    save_config()
    server = src.get_server()
    server.broadcast(f"§a[ZaiGanMa] §e{admin} §a已将 {key} 设为: {value}")
    src.reply(f"§a✅ {key} 已设为: {value}")

def set_config_int(src: CommandSource, key: str, value: int):
    """设置整数配置（管理员）"""
    if src.is_player and src.get_permission_level() < 3:
        src.reply("§c你没有权限执行此操作（需要管理员权限）")
        return
    admin = src.player if src.is_player else "控制台"
    if key == "max_length" and (value < 1 or value > 20):
        src.reply("§c字数必须在 1-20 之间")
        return
    if key == "manual_status_timeout" and value < 0:
        src.reply("§c超时时间不能为负数")
        return
    if key == "library_entry_max_length" and (value < 1 or value > 20):
        src.reply("§c字数必须在 1-20 之间")
        return
    if key == "lib_reload_permission_level" and (value < 0 or value > 4):
        src.reply("§c权限等级必须在 0-4 之间")
        return
    config[key] = value
    save_config()
    server = src.get_server()
    server.broadcast(f"§a[ZaiGanMa] §e{admin} §a已将 {key} 设为: {value}")
    src.reply(f"§a✅ {key} 已设为: {value}")