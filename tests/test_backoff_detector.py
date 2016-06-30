import neat_as_a_pin.src.backoff_detector as backoff
import time

def test_set_and_get():
    backoff.set("abc", 99)

    time_remaining, interval = backoff.get("abc")
    assert interval == 99
    assert 0 < time_remaining <= 99
    backoff.clear("abc")


def test_time_remaining_decreases():
    backoff.set("abc", 99)
    time_remaining, interval = backoff.get("abc")
    time.sleep(2)
    time_remaining2, interval2 = backoff.get("abc")
    assert 0 < time_remaining2 < time_remaining
    backoff.clear("abc")

def test_none_set():
    time_remaining, interval = backoff.get("nonesuch")
    assert interval is None
    assert not time_remaining

def test_flags_expire():
    backoff.set("abc", 1)
    time.sleep(2)
    time_remaining, interval = backoff.get("abc")
    assert time_remaining is None
    assert interval is None