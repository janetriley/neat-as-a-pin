import pytest

from neat_as_a_pin.src import common
from neat_as_a_pin.src import url_store as q

from neat_as_a_pin.conf import config

"""
@pytest.skip("refactored pop, need to redo")
def test_save_and_retrieve():
    q.clear(q.TEST)
    obj = {'value': u'asdf'}
    q.add(q.TEST, obj)
    result = q.pop(q.TEST)
    assert result == obj
"""


def test_pop_empty_queue():
    q.clear(q.TEST)
    q.save()
    with pytest.raises(StopIteration):
        q.pop(q.TEST)


def test_bogus_queue_name():
    with pytest.raises(LookupError):
        q.pop("BOGUS")


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
    items = []
    with open(config.DATA_DIR + "/export_UPDATE.json", 'r') as fp:
        parser = common.get_bookmarks_from_file(fp)
        for i in range(1, 3):
            bookmark = next(parser)
            items.append(bookmark)
            q.add(q.TEST, bookmark)

    for item in items:
        stack = q.pop(q.TEST)
        assert stack == item
