import pytest
import url_store as q


def test_save_and_retrieve():
    q.clear(q.TEST)
    obj = {'value': u'asdf'}
    q.add(q.TEST, obj)
    result = q.pop(q.TEST)
    assert result == obj


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
    items = ["one","two","three"]
    for item in items:
        q.add(q.TEST, item)

    gen = q.iterate(q.TEST)
    results = [next(gen), next(gen), next(gen)]
    assert results == items

    with pytest.raises(StopIteration):
        results = next(gen)



def test_iteration_stops():
    q.clear(q.TEST)
    items = ["one","two","three"]
    for item in items:
        q.add(q.TEST, item)

    gen = q.iterate(q.TEST)
    for i in next(gen):
        pass
