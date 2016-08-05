import pytest

from neat_as_a_pin.src import bookmark
from neat_as_a_pin.src import url_store as q


def test_pop_empty_queue():
    q.clear(q.TEST)
    q.save()
    with pytest.raises(StopIteration):
        q.pop_bookmark(q.TEST)


def test_bogus_queue_name():
    with pytest.raises(LookupError):
        q.pop_bookmark("BOGUS")


def test_iteration():
    q.clear(q.TEST)
    items = ["one", "two", "three"]
    for item in items:
        q.add(q.TEST, item)

    gen = q.iterate(q.TEST)
    results = [next(gen), next(gen), next(gen)]
    assert results == items

    with pytest.raises(StopIteration):
        results = next(gen)


def test_iteration_stops():
    q.clear(q.TEST)
    items = ["one", "two", "three"]
    for item in items:
        q.add(q.TEST, item)

    gen = q.iterate(q.TEST)
    for i in next(gen):
        pass


def test_pop():
    q.clear(q.TEST)
    b = bookmark.Bookmark(bookmark={"bookmark": "bookmark"}, info={"info": "info"}, errors={"errors": "errors"},
                          status={"status": "status"})
    q.add(q.TEST, b)

    stack = q.pop_bookmark(q.TEST)

    assert stack.bookmark == b.bookmark
    assert stack.info == b.info
    assert stack.errors == b.errors
    assert stack.status == None  #status isn't serialized

