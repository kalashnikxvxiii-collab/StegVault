"""
Pytest configuration and fixtures for memory-efficient testing.

Provides cleanup hooks to reduce RAM usage during test execution.
"""

import gc
import asyncio
import pytest


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """
    Automatically cleanup after each test.

    Runs garbage collection to release memory from:
    - Textual Screen instances
    - Async event loops
    - Mock objects
    """
    yield
    # Force garbage collection to release unreferenced objects
    gc.collect()


@pytest.fixture(autouse=True, scope="session")
def session_cleanup():
    """
    Cleanup at session start and end.

    Ensures clean state for entire test suite.
    """
    # Initial cleanup before tests
    gc.collect()
    yield
    # Final cleanup after all tests
    gc.collect()


@pytest.fixture
def event_loop():
    """
    Create and cleanup event loop for async tests.

    Explicitly closes event loop after each test to prevent memory leaks.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    # Cleanup: close all pending tasks
    try:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    except Exception:
        pass
    finally:
        loop.close()
        gc.collect()
