"""
Lightweight smoke tests for the ``funmedia`` package.

Scope / rationale
------------------
``funmedia`` (PyPI: funmedia) is a renamed fork of the open-source ``f2``
project. It declares 10 platforms in ``funmedia/apps/__apps__.py`` but only
FOUR of them actually have an implementation directory under
``funmedia/apps/``: **douyin, tiktok, twitter, weibo**. The other six
(youtube, instagram, bilibili, twitch, neteasy_music, little_red_book) have
no code at all, so they are intentionally NOT covered here.

While building this suite we discovered a real, reproducible, pre-existing
bug caused by the incomplete f2 -> funmedia rename (the package still has
``# path: f2/...`` header comments everywhere): ``get_resource_path()`` in
``funmedia/utils/utils.py`` does ``importlib_resources.files("f2")`` -- it
still points at the *old* "f2" package name instead of "funmedia". Since
"f2" is not a dependency of funmedia, this raises ``ModuleNotFoundError``
the moment it's exercised. It is reached by:

* ``funmedia.i18n.translator`` (the ``_()`` gettext helper used almost
  everywhere, including as a default argument at *import* time in
  ``funmedia/cli/cli_commands.py``)
* ``ClientConfManager`` in every platform's ``utils.py`` (evaluated at class
  body / import time)

As a result, importing any of ``<platform>.utils`` / ``.model`` (douyin,
tiktok) / ``.crawler`` / ``.dl`` / ``.handler`` / ``.cli``, or
``funmedia.cli.cli_commands`` (and hence ``python -m funmedia`` for *any*
invocation, including ``--help``), currently fails for all four implemented
platforms. This is a genuine business-logic/packaging bug, not a test
problem -- per audit scope we do not fix it here. The affected checks are
marked with ``pytest.mark.skip`` and a clear reason; ``test_known_bugs.py``-
style test below pins down the exact root cause so it's easy to notice (and
delete the skips) once someone fixes the "f2" -> "funmedia" typo upstream.

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
UNIMPLEMENTED_PLATFORMS = [
    "youtube",
    "instagram",
    "bilibili",
    "twitch",
    "neteasy_music",
    "little_red_book",
]

F2_RENAME_BUG_REASON = (
    "Known upstream bug (not fixed here, out of audit scope): "
    "funmedia/utils/utils.py:get_resource_path() still does "
    "importlib_resources.files('f2') -- a leftover from the pre-rename "
    "'f2' project -- instead of 'funmedia'. Since 'f2' is not installed, "
    "this raises ModuleNotFoundError as soon as funmedia.i18n.translator "
    "or any platform's ClientConfManager is imported, which blocks "
    "utils/model/crawler/dl/handler/cli for every implemented platform. "
    "See test_known_bug_get_resource_path_uses_stale_f2_package_name."
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

    for platform in UNIMPLEMENTED_PLATFORMS:
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
# Known bug: pre-rename "f2" resource path (documented, not fixed here)
# ---------------------------------------------------------------------------


def test_known_bug_get_resource_path_uses_stale_f2_package_name():
    """Pins down the exact root cause blocking downloader/crawler/handler/
    cli construction below. If this test starts failing, the upstream bug
    has likely been fixed and the skips further down should be revisited.
    """
    from funmedia.utils.utils import get_resource_path

    with pytest.raises(ModuleNotFoundError, match="f2"):
        get_resource_path("conf/conf.yaml")


@pytest.mark.parametrize("platform", IMPLEMENTED_PLATFORMS)
@pytest.mark.skip(reason=F2_RENAME_BUG_REASON)
def test_platform_utils_module_imports(platform):
    importlib.import_module(f"funmedia.apps.{platform}.utils")


@pytest.mark.parametrize("platform", IMPLEMENTED_PLATFORMS)
@pytest.mark.skip(reason=F2_RENAME_BUG_REASON)
def test_platform_downloader_constructs_with_mocked_network(platform, monkeypatch):
    """Would-be smoke test for the core public API: constructing
    ``<Platform>Downloader``/``<Platform>Crawler`` with a fake cookie and
    mocked httpx client, without making real requests. Currently blocked by
    the f2-rename bug documented above, so it is skipped rather than faked.
    """
    dl_module = importlib.import_module(f"funmedia.apps.{platform}.dl")
    downloader_cls = getattr(dl_module, f"{platform.capitalize()}Downloader")
    kwargs = {"cookie": "test=1", "headers": {}, "proxies": {"http://": None, "https://": None}}
    downloader = downloader_cls(kwargs)
    assert downloader is not None


@pytest.mark.skip(reason=F2_RENAME_BUG_REASON)
def test_cli_module_imports():
    import funmedia.cli.cli_commands  # noqa: F401


@pytest.mark.skip(reason=F2_RENAME_BUG_REASON)
def test_cli_help_exits_cleanly():
    """No [project.scripts] entry point is declared for funmedia, so there is
    no installed console script to invoke; this exercises the documented
    ``python -m funmedia --help`` invocation instead. Skipped: blocked by the
    f2-rename bug (funmedia/cli/cli_commands.py evaluates ``_("...")`` as a
    click option default at import time).
    """
    import subprocess

    result = subprocess.run(
        [sys.executable, "-m", "funmedia", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
