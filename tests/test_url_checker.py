import httpretty
import pytest

from pinboard_cleanup.src import url_checker


KNOWN_200 = 'http://janetriley.net/'
KNOWN_301 = 'http://janetriley.net/about'
MOCK_301 = 'http://mock-server/301'
MOCK_200 = 'http://totally-works.com/index.html'


def test_redirects_update_url():
    status = url_checker.fetch(KNOWN_301)
    assert status.history and len(status.history) > 0
    assert status.history[0].status_code == 301
    assert status.url != KNOWN_301


@httpretty.activate
def test_fetch_mock_200():
    httpretty.register_uri(httpretty.HEAD, MOCK_200,
                           status=200,
                           confirmation="yowza!",
                           body="You did it!")

    resp = url_checker.fetch(MOCK_200)
    assert resp.url == MOCK_200
    assert resp.status_code == 200
    assert resp.headers['confirmation'] == "yowza!"


@httpretty.activate
def test_fetch_follows_redirects():
    httpretty.register_uri(httpretty.HEAD, MOCK_301,
                           status=301,
                           location=MOCK_200)

    httpretty.register_uri(httpretty.HEAD, MOCK_200,
                           status=200,
                           confirmation="yowza!",
                           body="You did it!")

    status = url_checker.fetch(MOCK_301)
    assert status.url == MOCK_200
    assert len(status.history) > 0
    redirect = status.history[0]
    assert redirect.status_code == 301
    assert redirect.url == MOCK_301
    assert status.headers['confirmation'] == "yowza!"


def test_file_protocol_filtered_out():
    with pytest.raises(ValueError):
        url_checker.fetch('file://filter_these_out')


def test_check_real_200():
    resp = url_checker.check_status(__fake_bookmark(KNOWN_200))
    assert type(resp) == url_checker.BookmarkStatus
    assert resp.is_redirect is False
    assert resp.info['url'] == KNOWN_200


def test_check_real_bookmarks_301():
    resp = url_checker.check_status(__fake_bookmark(KNOWN_301))
    assert resp.is_redirect is True
    assert resp.info['old_status_code'] == 301
    assert resp.info['old_location'] == KNOWN_301
    assert resp.info['redirect'] is True
    assert resp.info['permanent_redirect'] is True


def test_check_exception_handling():
    resp = url_checker.check_status(__fake_bookmark("fake://bad/exception"))
    assert resp.is_redirect is False
    assert resp.errors is not None
    assert resp.info == {}


def __fake_bookmark(url):
    """
    Any fakery needed for emulating a pinboard bookmark
    :param url: url to wrap
    :return: a dict with the expected 'href':url pair
    """
    return {'href': url}
