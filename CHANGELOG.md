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
