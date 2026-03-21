"""Unit tests for RateLimiter."""

from __future__ import annotations

import threading
from collections.abc import Callable

import pytest

from llm_toll.exceptions import LocalRateLimitError
from llm_toll.rate_limiter import RateLimiter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_clock(start: float = 0.0) -> tuple[list[float], Callable[[], float]]:
    """Return a mutable time container and a mock clock function."""
    clock_time = [start]

    def mock_clock() -> float:
        return clock_time[0]

    return clock_time, mock_clock


# ---------------------------------------------------------------------------
# TestRateLimiterInstantiation
# ---------------------------------------------------------------------------


class TestRateLimiterInstantiation:
    """Tests for RateLimiter construction."""

    def test_instantiate_with_no_args(self) -> None:
        limiter = RateLimiter()
        assert limiter._rpm is None
        assert limiter._tpm is None

    def test_instantiate_with_rpm_and_tpm(self) -> None:
        limiter = RateLimiter(rpm=60, tpm=100_000)
        assert limiter._rpm == 60
        assert limiter._tpm == 100_000

    def test_instantiate_with_custom_clock(self) -> None:
        _clock_time, mock_clock = _make_clock(42.0)
        limiter = RateLimiter(rpm=10, tpm=5000, _clock=mock_clock)
        # The limiter should use our clock, not time.monotonic
        assert limiter._clock is mock_clock
        # Verify it reads the injected time
        limiter.record(tokens=1)
        assert limiter._request_timestamps[-1] == 42.0


# ---------------------------------------------------------------------------
# TestRPMEnforcement
# ---------------------------------------------------------------------------


class TestRPMEnforcement:
    """Tests for requests-per-minute enforcement."""

    def test_rpm_allows_up_to_limit(self) -> None:
        clock_time, mock_clock = _make_clock()
        limiter = RateLimiter(rpm=5, _clock=mock_clock)

        for _i in range(5):
            limiter.check()
            limiter.record()
            clock_time[0] += 0.1  # small advance so timestamps differ

    def test_rpm_blocks_at_limit(self) -> None:
        clock_time, mock_clock = _make_clock()
        limiter = RateLimiter(rpm=3, _clock=mock_clock)

        for _ in range(3):
            limiter.check()
            limiter.record()
            clock_time[0] += 0.01

        with pytest.raises(LocalRateLimitError) as exc_info:
            limiter.check()

        assert exc_info.value.limit_type == "rpm"
        assert exc_info.value.limit_value == 3

    def test_rpm_retry_after_is_positive(self) -> None:
        clock_time, mock_clock = _make_clock(100.0)
        limiter = RateLimiter(rpm=2, _clock=mock_clock)

        limiter.check()
        limiter.record()
        clock_time[0] = 100.5
        limiter.check()
        limiter.record()
        clock_time[0] = 101.0

        with pytest.raises(LocalRateLimitError) as exc_info:
            limiter.check()

        assert exc_info.value.retry_after is not None
        assert exc_info.value.retry_after > 0

    def test_rpm_window_expiry(self) -> None:
        clock_time, mock_clock = _make_clock(0.0)
        limiter = RateLimiter(rpm=2, _clock=mock_clock)

        limiter.check()
        limiter.record()
        clock_time[0] = 1.0
        limiter.check()
        limiter.record()

        # At t=2.0 the window still contains both requests
        clock_time[0] = 2.0
        with pytest.raises(LocalRateLimitError):
            limiter.check()

        # Advance past 60s from the first record (t=0.0) => first entry expires
        clock_time[0] = 60.1
        limiter.check()  # should not raise

    def test_rpm_none_disables(self) -> None:
        clock_time, mock_clock = _make_clock()
        limiter = RateLimiter(rpm=None, tpm=1000, _clock=mock_clock)

        # Record many requests — RPM is disabled so only TPM matters
        for _ in range(200):
            limiter.check()
            limiter.record(tokens=0)
            clock_time[0] += 0.001


# ---------------------------------------------------------------------------
# TestTPMEnforcement
# ---------------------------------------------------------------------------


class TestTPMEnforcement:
    """Tests for tokens-per-minute enforcement."""

    def test_tpm_allows_within_limit(self) -> None:
        clock_time, mock_clock = _make_clock()
        limiter = RateLimiter(tpm=1000, _clock=mock_clock)

        limiter.record(tokens=400)
        clock_time[0] += 0.1
        limiter.record(tokens=400)
        clock_time[0] += 0.1
        limiter.check()  # 800 < 1000, should pass

    def test_tpm_blocks_at_limit(self) -> None:
        clock_time, mock_clock = _make_clock()
        limiter = RateLimiter(tpm=500, _clock=mock_clock)

        limiter.record(tokens=300)
        clock_time[0] += 0.1
        limiter.record(tokens=200)
        clock_time[0] += 0.1

        # 300 + 200 = 500 >= 500
        with pytest.raises(LocalRateLimitError) as exc_info:
            limiter.check()

        assert exc_info.value.limit_type == "tpm"
        assert exc_info.value.limit_value == 500

    def test_tpm_retry_after_is_positive(self) -> None:
        clock_time, mock_clock = _make_clock(10.0)
        limiter = RateLimiter(tpm=100, _clock=mock_clock)

        limiter.record(tokens=100)
        clock_time[0] = 15.0

        with pytest.raises(LocalRateLimitError) as exc_info:
            limiter.check()

        assert exc_info.value.retry_after is not None
        assert exc_info.value.retry_after > 0

    def test_tpm_window_expiry(self) -> None:
        clock_time, mock_clock = _make_clock(0.0)
        limiter = RateLimiter(tpm=100, _clock=mock_clock)

        limiter.record(tokens=100)

        # Still in window
        clock_time[0] = 30.0
        with pytest.raises(LocalRateLimitError):
            limiter.check()

        # Advance past 60s => tokens expire
        clock_time[0] = 60.1
        limiter.check()  # should not raise

    def test_tpm_none_disables(self) -> None:
        clock_time, mock_clock = _make_clock()
        limiter = RateLimiter(rpm=1000, tpm=None, _clock=mock_clock)

        # Record huge token counts — TPM is disabled so only RPM matters
        for _ in range(10):
            limiter.check()
            limiter.record(tokens=999_999)
            clock_time[0] += 0.001


# ---------------------------------------------------------------------------
# TestRPMAndTPMCombined
# ---------------------------------------------------------------------------


class TestRPMAndTPMCombined:
    """Tests for interactions between RPM and TPM limits."""

    def test_rpm_trips_without_tpm(self) -> None:
        """RPM can be exceeded even when TPM headroom remains."""
        clock_time, mock_clock = _make_clock()
        limiter = RateLimiter(rpm=2, tpm=100_000, _clock=mock_clock)

        limiter.check()
        limiter.record(tokens=1)
        clock_time[0] += 0.01
        limiter.check()
        limiter.record(tokens=1)
        clock_time[0] += 0.01

        with pytest.raises(LocalRateLimitError) as exc_info:
            limiter.check()
        assert exc_info.value.limit_type == "rpm"

    def test_tpm_trips_without_rpm(self) -> None:
        """TPM can be exceeded even when RPM headroom remains."""
        clock_time, mock_clock = _make_clock()
        limiter = RateLimiter(rpm=100, tpm=500, _clock=mock_clock)

        limiter.check()
        limiter.record(tokens=500)
        clock_time[0] += 0.01

        with pytest.raises(LocalRateLimitError) as exc_info:
            limiter.check()
        assert exc_info.value.limit_type == "tpm"

    def test_both_limits_none_is_noop(self) -> None:
        """When both limits are None, check/record are fast no-ops."""
        limiter = RateLimiter(rpm=None, tpm=None)

        # Should complete instantly without acquiring the lock or recording
        for _ in range(1000):
            limiter.check()
            limiter.record(tokens=999_999)

        # Internal deques should remain empty (early return before lock)
        assert len(limiter._request_timestamps) == 0
        assert len(limiter._token_log) == 0


# ---------------------------------------------------------------------------
# TestThreadSafety
# ---------------------------------------------------------------------------


class TestThreadSafety:
    """Tests for concurrent access."""

    def test_concurrent_check_and_record(self) -> None:
        """Spawn multiple threads doing check+record; no crashes expected."""
        _clock_time, mock_clock = _make_clock()
        # Use generous limits so most calls succeed
        limiter = RateLimiter(rpm=500, tpm=500_000, _clock=mock_clock)

        errors: list[Exception] = []
        barrier = threading.Barrier(10)

        def worker() -> None:
            barrier.wait()
            try:
                for _ in range(50):
                    try:
                        limiter.check()
                        limiter.record(tokens=10)
                    except LocalRateLimitError:
                        pass  # expected under contention
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=10)

        assert errors == [], f"Unexpected errors in threads: {errors}"


# ---------------------------------------------------------------------------
# TestEdgeCases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge-case tests."""

    def test_record_zero_tokens_still_counts_for_rpm(self) -> None:
        clock_time, mock_clock = _make_clock()
        limiter = RateLimiter(rpm=2, _clock=mock_clock)

        limiter.check()
        limiter.record(tokens=0)
        clock_time[0] += 0.01
        limiter.check()
        limiter.record(tokens=0)
        clock_time[0] += 0.01

        with pytest.raises(LocalRateLimitError) as exc_info:
            limiter.check()
        assert exc_info.value.limit_type == "rpm"

    def test_check_without_prior_record(self) -> None:
        """First call to check always passes when limits are set."""
        _, mock_clock = _make_clock()
        limiter = RateLimiter(rpm=1, tpm=1, _clock=mock_clock)
        limiter.check()  # should not raise
