# 更新日志

## [1.2.12] - 未发布

### 变更

- 源码迁移至 `src/funmedia/` 标准布局
- 日志改用组织统一的 `farlog.getLogger`，不再在 import 时自动创建 `./logs` 目录和配置 handler
- `requires-python` 由 `>=3.11` 调整为 `>=3.10`
- `typing.List`/`typing.Dict` 迁移为内置泛型 `list[...]`/`dict[...]`
- `pyproject.toml` 补充 `license = "MIT"` 与 `license-files`
- 项目描述由模板占位文案改为准确的一句话说明
- README 补充第三方代码来源说明（[f2](https://github.com/Johnserf-Seed/f2)，Apache License 2.0）及「关于 farfarfun」区块

### 修复

- 移除 `funmedia/conf/test.yaml`、`funmedia/conf/conf.yaml` 中提交的真实 cookie/token，改为占位值
- `_signal.py` 清理阶段不再用 `except Exception: pass` 静默吞掉异常
- `tiktok/model.py`、`utils/utils.py` 中的 `print` 诊断输出改用 `farlog` 记录，并对可能包含敏感内容的原始响应不再直接打印
- `douyin/model.py`、`tiktok/model.py` 中 `BaseRequestModel.msToken` 的裸 `except:`/`except APIError` 改为 `Field(default_factory=...)`，避免在模块导入时发起网络请求、失败时降级为虚假 token
- `douyin/crawler.py` 的 `handle_wss_message` 按 protobuf 解码、发送 ack、回调执行三类边界分别捕获具体异常，不再用一个 `except Exception` 吞掉所有错误
- `utils/_dl.py` 连接超时日志不再打印完整 `headers`/`proxies`（可能含 Cookie/token），改为只记录 header 键名
- 新增 `utils/utils.py:mask_sensitive_url`，对 douyin/tiktok/twitter/weibo 四个 crawler 的接口地址调试日志中的 token/signature/cookie 等查询参数做脱敏
- `conf_manager.py` 写入 Cookie 到本地明文配置文件前输出警告提示；`douyin/tiktok/twitter/weibo` 的 `--cookie` 选项新增 `envvar`（如 `FUNMEDIA_DOUYIN_COOKIE`），支持免落盘传入
- `__init__.py` 的 `__version__` 由手写常量改为从已安装包元数据读取，以 `pyproject.toml` 为唯一版本来源，避免像之前 `0.0.1.6` 与实际发布版本 `1.2.12` 长期脱节
- `cli_commands.py` 的 `check_version` 修复：误查 PyPI 上的 `f2` 包而非 `funmedia`、版本号按字符串比较导致新旧判断及升级提示文案错误
- `typing.Optional`/`Union`/`List`/`Dict` 在全仓库迁移为内置泛型写法（`X | None`、`list[...]`、`dict[...]`）
