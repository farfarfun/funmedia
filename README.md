# funmedia

异步多平台短视频/社媒无水印下载工具，支持抖音、TikTok、微博、Twitter(X) 四个平台，可按用户主页、点赞、收藏、合集、直播等模式批量抓取并下载作品（视频/图集/音乐/封面/文案）。

说明：本项目代码基于知名开源项目 [f2](https://github.com/Johnserf-Seed/f2) 改名而来（源码内保留了大量 `f2` 相关注释、路径标记与 `__repourl__` 指向原仓库），当前仅实现了 douyin/tiktok/weibo/twitter 四个应用，`funmedia/apps/__apps__.py` 中声明的 youtube、instagram、bilibili、twitch、neteasy_music、little_red_book 尚未有对应实现目录。

## 安装

目前尚未发布可用的 PyPI 包（`pip install funmedia` 获取到的是占位包，无实际功能代码），需要从源码安装：

```bash
git clone https://github.com/farfarfun/funmedia.git
cd funmedia
pip install -e .
```

## 命令行用法

安装后没有注册 `funmedia` 命令行入口（`pyproject.toml` 未声明 `[project.scripts]`），需要通过模块方式调用：

```bash
python -m funmedia douyin -u "https://www.douyin.com/user/xxx" -M post -p ./Download
```

`douyin`/`tiktok`/`weibo`/`twitter` 是可用的子命令（对应 `funmedia/apps/<app>/cli.py`），常用参数：

- `-u/--url`：主页、作品、合集或直播链接
- `-M/--mode`：下载模式，抖音支持 `one/post/like/collection/collects/music/mix/live/related/friend` 等（见 `funmedia/__init__.py` 中的 `DOUYIN_MODE_LIST`）
- `-k/--cookie`：登录后的 Cookie，未登录状态下无法稳定下载
- `-p/--path`：作品保存路径
- `-n/--naming`：文件命名模板

执行 `python -m funmedia --help` 或 `python -m funmedia douyin --help` 可查看完整参数说明。

## 作为库使用

各平台的核心逻辑封装在对应的 `Handler` 类中，例如抖音：

```python
from funmedia.apps.douyin.handler import DouyinHandler

handler = DouyinHandler(kwargs={"cookie": "...", "path": "./Download"})
profile = await handler.fetch_user_profile(sec_user_id="...")
```

下载、过滤、数据模型分别在同目录下的 `dl.py`（`DouyinDownloader`）、`filter.py`、`model.py` 中实现，`crawler.py` 提供底层请求封装（`DouyinCrawler`/`DouyinWebSocketCrawler`）。

## 第三方代码来源

本项目基于开源项目 [f2](https://github.com/Johnserf-Seed/f2)（作者 JohnserfSeed，原始协议 Apache License 2.0）改名而来，大部分核心逻辑直接移植自 f2，源码中保留了原始的文件头注释与版权声明。其中签名算法实现 `funmedia/utils/abogus.py` 同样来自 f2，原始协议为 Apache License 2.0。

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
