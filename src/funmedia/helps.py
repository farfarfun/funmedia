#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Description:helps.py
@Date       :2023/02/06 17:36:41
@Author     :JohnserfSeed
@version    :0.0.1.6
@License    :Apache License 2.0
@Github     :https://github.com/johnserf-seed
@Mail       :johnserf-seed@foxmail.com
-------------------------------------------------
Change Log  :
2023/02/06 17:36:41 - create output help
2024/03/11 18:23:30 - change get_help @ importlib path
-------------------------------------------------
"""

import funmedia
import importlib

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from funmedia.i18n.translator import _


def get_help(app_name: str) -> None:
    try:
        module = importlib.import_module(f"funmedia.apps.{app_name}.help")
        if hasattr(module, "help"):
            module.help()
        else:
            print(_("在 {0} 应用里没有找到帮助文件").format(app_name))
    except ImportError:
        print(_("没有找到 {0} 应用").format(app_name))


def main() -> None:
    # 真彩
    console = Console(color_system="truecolor")
    console.print(
        f"\n:rocket: [bold]funmedia {funmedia.__version__} :rocket:", justify="center"
    )
    console.print(f"\n[i]{funmedia.__description_cn__}", justify="center")
    console.print(f"[i]{funmedia.__description_en__}", justify="center")
    console.print(f"[i]GitHub {funmedia.__repourl__}\n", justify="center")

    # 使用方法
    table = Table.grid(padding=1, pad_edge=True)
    table.add_column("Usage", no_wrap=True, justify="left", style="bold")
    table.add_row("[b]python -m funmedia[/b] [magenta]<apps> [/magenta][cyan][COMMAND]")
    table.add_row(_("例：python -m funmedia douyin -h/--help 获取 douyin 的命令帮助"))
    table.add_row(
        "[b]python -m funmedia[/b] [magenta][Option] [/magenta][cyan][Args][/cyan] [magenta]<apps> [/magenta][cyan][COMMAND]"
    )
    table.add_row(_("例：python -m funmedia -d DEBUG douyin 日志级别为调试运行"))
    console.print(
        Panel(table, border_style="bold", title="使用方法 | Usage", title_align="left")
    )

    # 应用列表
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column(_("参数"), no_wrap=True, justify="left", style="bold")
    table.add_column(_("描述"), no_wrap=True, style="bold")
    table.add_column(_("状态"), no_wrap=True, justify="left", style="bold")

    table.add_row(_("weibo 或 wb"), _("- 获取微博"))
    table.add_row(
        _("douyin 或 dy"),
        _(
            "- 单个作品，主页作品，点赞作品，收藏作品，合集作品，图文，文案，封面，直播，原声。"
        ),
        _("✔"),
    )
    table.add_row(
        _("tiktok 或 tk"),
        _(
            "- 单个作品，主页作品，点赞作品，收藏作品，播放列表（合集）作品，文案，封面，原声。"
        ),
        _("✔"),
    )
    table.add_row(_("instagram 或 ig"), _("- 获取ig的作品"), _("⏳"))
    table.add_row(_("twitch 或 tv"), _("- 获取Twitch直播"))
    table.add_row(_("twitter 或 x"), _("- 获取Twitter作品"), _("⏳"))
    table.add_row(_("youtube 或 ytb"), _("- 获取YouTube的作品"))
    table.add_row(_("bilibili 或 bili"), _("- 获取BiliBili的作品"))
    table.add_row(_("neteasy_music 或 nem"), _("- 获取网易云音乐作品"))
    table.add_row(_("little_red_book 或 lrb"), _("- 获取小红书的作品"))
    table.add_row("\n")
    table.add_row(
        "python -m funmedia -d DEBUG",
        _(
            "- 记录app的调试日志到/logs下，如遇BUG提交Issue时请附带该文件并[red]删除个人敏感信息[/red]"
        ),
        _("⚠"),
    )
    (
        table.add_row(
            "Issues❓", "[link=https://github.com/farfarfun/funmedia/issues]Click Here[/]"
        ),
    )
    table.add_row(
        "Repository", "[link=https://github.com/farfarfun/funmedia]Click Here[/]"
    )
    console.print(
        Panel(
            table,
            border_style="bold",
            title="应用 | apps",
            title_align="left",
            subtitle=_("欢迎提交PR适配更多网站"),
        )
    )
