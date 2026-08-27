"""
Lightweight smoke tests for the ``funmedia`` package.

Scope / rationale
------------------
``funmedia`` (PyPI: funmedia) is a renamed fork of the open-source ``f2``
project.

As of farfarfun/todo-list#155, ``get_resource_path()`` in
``funmedia/utils/utils.py`` now does ``importlib_resources.files("funmedia")``
instead of the stale pre-rename ``"f2"``, which previously raised
``ModuleNotFoundError`` for every import path that touched it (i18n
``_()``, every platform's ``ClientConfManager``, and hence
``funmedia.cli.cli_commands`` / ``python -m funmedia`` entirely).

``funmedia/apps/__apps__.py`` also declared 10 platforms but only FOUR ever
had an implementation directory under ``funmedia/apps/``: **douyin, tiktok,
twitter, weibo**. The other six (youtube, instagram, bilibili, twitch,
neteasy_music, little_red_book) had no code at all and were silently
unresolvable as CLI subcommands; per #155 they've been removed from
``__apps__.py`` rather than left as dead declarations.

Now that the f2-rename bug is fixed, a *separate*, previously-masked bug
surfaced: ``funmedia/apps/tiktok/utils.py``'s ``DeviceIdManager`` class body
evaluates ``TokenManager.gen_real_msToken()`` (a real network call) as a
class attribute default at *import time*. In this sandboxed/offline test
environment that raises ``APIResponseError`` the moment
``funmedia.apps.tiktok.utils`` (and hence ``.dl``/``.cli``) is imported.
This is a genuine, pre-existing design bug (network I/O at import time) --
unrelated to the f2-rename issue #155 covers -- so it is documented and
skipped rather than fixed here. Note ``DynamicGroup.get_command`` in
``cli_commands.py`` catches ``ImportError``/``AttributeError`` around the
per-platform dynamic import, so ``python -m funmedia --help`` and the
overall CLI group still work; only the ``tiktok`` subcommand itself is
unusable until that bug is fixed.

Everything else below is a real, passing check: no network I/O is performed
(any HTTP call would need a valid session/cookie against a live platform),
we only exercise pure-Python helpers, local sqlite I/O via aiosqlite, and
plain imports/instantiation.
"""

import asyncio
import importlib
import importlib.util
import sys

import pytest

IMPLEMENTED_PLATFORMS = ["douyin", "tiktok", "twitter", "weibo"]
# tiktok has real code (it's an IMPLEMENTED_PLATFORM) but its utils module
# currently fails to import in this environment -- see
# TIKTOK_IMPORT_TIME_NETWORK_BUG_REASON below.
WORKING_PLATFORMS = ["douyin", "twitter", "weibo"]
UNIMPLEMENTED_PLATFORMS = [
    "youtube",
    "instagram",
    "bilibili",
    "twitch",
    "neteasy_music",
    "little_red_book",
]

TIKTOK_IMPORT_TIME_NETWORK_BUG_REASON = (
    "Known pre-existing bug (not fixed here, out of scope for #155 -- it's "
    "unrelated to the f2-rename that issue covers): "
    "funmedia/apps/tiktok/utils.py's DeviceIdManager class body evaluates "
    "TokenManager.gen_real_msToken(), a real network call, as a class "
    "attribute default at *import time*. This makes funmedia.apps.tiktok."
    "utils (and hence .dl/.cli) fail to import without network access. "
    "See test_known_bug_tiktok_utils_makes_network_call_at_import_time."
)


# ---------------------------------------------------------------------------
# Top-level package
# ---------------------------------------------------------------------------


def test_import_top_level_package():
    import funmedia

    assert isinstance(funmedia.__version__, str) and funmedia.__version__
    assert isinstance(funmedia.DOUYIN_MODE_LIST, list) and funmedia.DOUYIN_MODE_LIST
    assert isinstance(funmedia.TIKTOK_MODE_LIST, list)
    assert isinstance(funmedia.WEIBO_MODE_LIST, list)
    assert isinstance(funmedia.TWITTER_MODE_LIST, list)


def test_apps_declared_vs_implemented_matches_audit_finding():
    """Sanity-check the audit's own claim against the source of truth."""
    from funmedia.apps import __apps__

    declared = {name for pair in __apps__.__all__ for name in getattr(__apps__, pair)}
    # every implemented platform's short + long name should be declared
    for platform in IMPLEMENTED_PLATFORMS:
        assert platform in declared

    for platform in IMPLEMENTED_PLATFORMS:
        spec = importlib.util.find_spec(f"funmedia.apps.{platform}")
        assert spec is not None, f"{platform} should be importable"

    # #155: unimplemented platforms are no longer declared in __apps__.py
    for platform in UNIMPLEMENTED_PLATFORMS:
        assert platform not in declared
        spec = importlib.util.find_spec(f"funmedia.apps.{platform}")
        assert spec is None, f"{platform} was expected to be unimplemented"


@pytest.mark.parametrize("platform", IMPLEMENTED_PLATFORMS)
def test_platform_package_imports(platform):
    """The bare ``funmedia.apps.<platform>`` package imports cleanly."""
    module = importlib.import_module(f"funmedia.apps.{platform}")
    assert module is not None


@pytest.mark.parametrize("platform", IMPLEMENTED_PLATFORMS)
def test_platform_db_module_imports(platform):
    """DB layer modules are pure aiosqlite wrappers; safe to import."""
    module = importlib.import_module(f"funmedia.apps.{platform}.db")
    assert hasattr(module, "AsyncUserDB")


@pytest.mark.parametrize("platform", IMPLEMENTED_PLATFORMS)
def test_platform_filter_module_imports(platform):
    module = importlib.import_module(f"funmedia.apps.{platform}.filter")
    assert module is not None


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


def test_exceptions_import_and_instantiate():
    from funmedia.exceptions.api_exceptions import (
        APIError,
        APIConnectionError,
        APINotFoundError,
        APIResponseError,
        APIRateLimitError,
        APITimeoutError,
        APIUnauthorizedError,
        APIUnavailableError,
        APIRetryExhaustedError,
    )

    err = APIResponseError("boom", 500)
    assert isinstance(err, APIError)
    assert "boom" in str(err)
    assert "500" in str(err)

    # All exception subclasses should be constructible with just a message.
    for exc_cls in (
        APIConnectionError,
        APINotFoundError,
        APIRateLimitError,
        APITimeoutError,
        APIUnauthorizedError,
        APIUnavailableError,
        APIRetryExhaustedError,
    ):
        instance = exc_cls("msg")
        assert isinstance(instance, APIError)


def test_db_and_file_exceptions_import():
    import funmedia.exceptions.db_exceptions  # noqa: F401
    import funmedia.exceptions.file_exceptions  # noqa: F401


# ---------------------------------------------------------------------------
# Pure utility helpers (funmedia/utils/*.py) -- no network involved
# ---------------------------------------------------------------------------


def test_utils_gen_random_str_and_timestamp_helpers():
    from funmedia.utils.utils import (
        gen_random_str,
        get_timestamp,
        timestamp_2_str,
        num_to_base36,
        split_set_cookie,
    )

    s = gen_random_str(16)
    assert isinstance(s, str) and len(s) == 16

    ts = get_timestamp(unit="sec")
    assert isinstance(ts, int)
    assert timestamp_2_str(ts)

    assert num_to_base36(12345) != ""

    cookie = split_set_cookie("a=1; Path=/, b=2; Path=/")
    assert "a=1" in cookie and "b=2" in cookie


def test_utils_base_endpoint_manager():
    from funmedia.utils.utils import BaseEndpointManager

    endpoint = BaseEndpointManager.model_2_endpoint(
        "https://example.com/api", {"a": 1, "b": "x"}
    )
    assert endpoint == "https://example.com/api?a=1&b=x"


def test_utils_ensure_path(tmp_path):
    from funmedia.utils.utils import ensure_path

    target = tmp_path / "some" / "nested" / "dir"
    result = ensure_path(target)
    assert str(result) == str(target)


def test_get_resource_path_resolves_within_funmedia_package():
    """#155: get_resource_path() used to do
    importlib_resources.files("f2") -- the pre-rename package name -- and
    raise ModuleNotFoundError unconditionally. It now resolves against the
    real "funmedia" package."""
    from funmedia.utils.utils import get_resource_path

    path = get_resource_path("conf/conf.yaml")
    assert path.is_file()


def test_decorators_module_imports():
    import funmedia.utils.decorators  # noqa: F401


def test_json_filter_module_imports():
    from funmedia.utils.json_filter import JSONModel

    assert JSONModel is not None


def test_xbogus_can_be_constructed_without_network():
    from funmedia.utils.xbogus import XBogus

    xb = XBogus(user_agent="test-agent/1.0")
    assert xb.user_agent == "test-agent/1.0"
    # XBogus falls back to a default UA when given an empty string.
    xb_default = XBogus(user_agent="")
    assert xb_default.user_agent


def test_abogus_module_imports():
    import funmedia.utils.abogus  # noqa: F401


# ---------------------------------------------------------------------------
# Local sqlite DB layer (real file I/O, still no network)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("platform", IMPLEMENTED_PLATFORMS)
def test_platform_async_user_db_roundtrip(tmp_path, platform):
    """AsyncUserDB is a thin aiosqlite wrapper; exercise it against a temp
    sqlite file to confirm the schema creation / connect / close cycle
    works, without touching the network."""
    db_module = importlib.import_module(f"funmedia.apps.{platform}.db")
    AsyncUserDB = db_module.AsyncUserDB
    db_path = tmp_path / f"{platform}_users.db"

    async def _run():
        async with AsyncUserDB(str(db_path)) as db:
            assert db.conn is not None

    asyncio.run(_run())
    assert db_path.exists()


# ---------------------------------------------------------------------------
# Now-fixed by #155: utils / cli / downloader for the platforms whose only
# blocker was the "f2" -> "funmedia" resource-path bug.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("platform", WORKING_PLATFORMS)
def test_platform_utils_module_imports(platform):
    importlib.import_module(f"funmedia.apps.{platform}.utils")


@pytest.mark.parametrize("platform", WORKING_PLATFORMS)
def test_platform_cli_module_imports(platform):
    importlib.import_module(f"funmedia.apps.{platform}.cli")


@pytest.mark.parametrize("platform", WORKING_PLATFORMS)
def test_platform_downloader_constructs_without_network(platform):
    """Constructing ``<Platform>Downloader`` with a fake cookie, without
    making real requests."""
    dl_module = importlib.import_module(f"funmedia.apps.{platform}.dl")
    downloader_cls = getattr(dl_module, f"{platform.capitalize()}Downloader")
    kwargs = {"cookie": "test=1", "headers": {}, "proxies": {"http://": None, "https://": None}}
    downloader = downloader_cls(kwargs)
    assert downloader is not None


def test_cli_module_imports():
    import funmedia.cli.cli_commands  # noqa: F401


def test_cli_help_exits_cleanly():
    """No [project.scripts] entry point is declared for funmedia, so there is
    no installed console script to invoke; this exercises the documented
    ``python -m funmedia --help`` invocation instead.
    """
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "funmedia", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# Known bug (separate from #155, not fixed here): tiktok makes a network
# call at import time.
# ---------------------------------------------------------------------------


def test_known_bug_tiktok_utils_makes_network_call_at_import_time():
    """Pins down a real, reproducible, pre-existing bug that #155's fix
    incidentally unmasked: funmedia.apps.tiktok.utils.DeviceIdManager
    evaluates a real network call (TokenManager.gen_real_msToken()) as a
    class attribute default, at import time. Fails offline with
    APIResponseError instead of ModuleNotFoundError('f2') like it used to.
    """
    for name in list(sys.modules):
        if name.startswith("funmedia.apps.tiktok"):
            del sys.modules[name]

    from funmedia.exceptions.api_exceptions import APIResponseError

    with pytest.raises(APIResponseError):
        importlib.import_module("funmedia.apps.tiktok.utils")


@pytest.mark.skip(reason=TIKTOK_IMPORT_TIME_NETWORK_BUG_REASON)
def test_platform_downloader_constructs_without_network_tiktok():
    dl_module = importlib.import_module("funmedia.apps.tiktok.dl")
    downloader_cls = dl_module.TiktokDownloader
    kwargs = {"cookie": "test=1", "headers": {}, "proxies": {"http://": None, "https://": None}}
    downloader = downloader_cls(kwargs)
    assert downloader is not None
