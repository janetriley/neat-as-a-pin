from neat_as_a_pin.src.bookmark import Bookmark
from neat_as_a_pin.src import url_checker


KNOWN_200 = 'http://janetriley.net/'
KNOWN_301 = 'http://janetriley.net/about'
MOCK_301 = 'http://mock-server/301'
MOCK_200 = 'http://totally-works.com/index.html'


def test_redirects_update_url():
    status = url_checker.fetch(KNOWN_301)
    assert status.history and len(status.history) > 0
    assert status.history[0].status_code == 301
    assert status.url != KNOWN_301


def test_check_real_200():
    resp = url_checker.check_status_and_make_bookmark(__fake_bookmark(KNOWN_200))
    assert type(resp) == url_checker.Bookmark
    assert resp.is_redirect is False
    assert resp.info['url'] == KNOWN_200

"""
def test_check_real_bookmarks_301():
    resp = url_checker.check_status_and_make_bookmark(__fake_bookmark(KNOWN_301))
    assert resp.is_redirect is True
    assert resp.info['old_status_code'] == 301
    assert resp.info['old_location'] == KNOWN_301
    assert resp.info['redirect'] is True
    assert resp.info['permanent_redirect'] is True
"""

def test_new_model_works():
    b = Bookmark(bookmark=__fake_bookmark(KNOWN_200), info={'key': 'info', 'redirect': True}, errors={'key': 'errors'},
                 status={'status_code': 200})
    assert b.status_code is 200
    assert b.is_redirect is True
    assert b.bookmark['href'] is KNOWN_200
    #assert b.info['key'] == 'info'
    assert b.errors['key'] == 'errors'


def test_check_exception_handling():
    resp = url_checker.check_status_and_make_bookmark(__fake_bookmark("fake://bad/exception"))
    assert resp.is_redirect is False
    assert resp.errors is not None



def __fake_bookmark(url):
    """
    Any fakery needed for emulating a pinboard bookmark
    :param url: url to wrap
    :return: a dict with the expected 'href':url pair
    """
    return {'href': url, 'tags': ""}
