# SPDX-License-Identifier: MIT
import asyncio

# pytest-asyncio 1.x's _temporary_event_loop_policy captures the current loop
# via asyncio.get_event_loop(); on Python 3.12 that implicitly constructs a new
# loop the framework never closes, which trips ResourceWarning -> error under
# filterwarnings=error when GC runs later. Owning the loop here lets us close it.
_session_loop: asyncio.AbstractEventLoop | None = None


def pytest_configure(config):
    global _session_loop
    _session_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_session_loop)


def pytest_unconfigure(config):
    global _session_loop
    if _session_loop is not None and not _session_loop.is_closed():
        _session_loop.close()
    _session_loop = None
