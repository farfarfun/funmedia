# path: funmedia/__init__.py

from importlib.metadata import PackageNotFoundError, version as _metadata_version

__author__ = "farfarfun"
try:
    # 版本号唯一来源是 pyproject.toml，运行时从已安装的包元数据读取，避免手动维护的
    # 常量与实际发布版本脱节 (Single source of truth is pyproject.toml; read it from
    # installed package metadata at runtime instead of hand-maintaining a constant)
    __version__ = _metadata_version("funmedia")
except PackageNotFoundError:  # 从源码目录直接运行、尚未安装时的兜底
    __version__ = "0.0.0.dev0"
__description_cn__ = "基于[red]异步[/red]的[green]全平台下载工具."
__description_en__ = "[yellow]Asynchronous based [/yellow]full-platform download tool."
__reponame__ = "funmedia"
__repourl__ = "https://github.com/farfarfun/funmedia"

APP_CONFIG_FILE_PATH = "conf/app.yaml"
F2_CONFIG_FILE_PATH = "conf/conf.yaml"
F2_DEFAULTS_FILE_PATH = "conf/defaults.yaml"
TEST_CONFIG_FILE_PATH = "conf/test.yaml"

BROWSER_LIST = [
    "chrome",
    "firefox",
    "edge",
    "opera",
    "opera_gx",
    "safari",
    "chromium",
    "brave",
    "vivaldi",
    "librewolf",
]

DOUYIN_MODE_LIST = [
    "one",
    "post",
    "like",
    "collection",
    "collects",
    "music",
    "mix",
    "live",
    "related",
    "friend",
]

TIKTOK_MODE_LIST = [
    "one",
    "post",
    "like",
    "collect",
    "mix",
    "search",
    "live",
]

WEIBO_MODE_LIST = [
    "one",
    "post",
    "like",
]

TWITTER_MODE_LIST = [
    "one",
    "post",
    "retweet",
    "like",
    "bookmark",
]

PYPI_URL = "https://pypi.org/pypi"
