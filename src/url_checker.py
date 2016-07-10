# This will be used by Python 2.x and 3.x clients
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse

import requests
import socket
from dns import resolver
from dns.resolver import NXDOMAIN
from neat_as_a_pin.src.common import BookmarkStatus
from neat_as_a_pin.src import backoff_detector
import logging
from requests import codes as http_status



class BadHost(Exception):
    """ Host is not resolvable """
    def __init__(self, *args):
      self.args = args

class BadUrl(Exception):
    """ Protocol isn't recognized """
    def __init__(self, *args):
      self.args = args

class ConnectionError(Exception):
    def __init__(self, *args):
        self.args = args


def check_status_and_make_bookmark(pinboard_bookmark):
    """
    Check status during initial load
    for a pinboard export
    return a bookmark
    refactor in process

    :param pinboard_bookmark:
    :return:
    """
    try:
        status, info = check_url(pinboard_bookmark['href'])

        return BookmarkStatus(status.status_code,
                              info['redirect'],
                              pinboard_bookmark,
                              info,
                              None
                              )

    except Exception as e:
        return BookmarkStatus(0,
                              False,
                              pinboard_bookmark,
                              {},
                              {'type': type(e).__name__,
                               'msg': str(e)}
                              )


def check_url(url):
    """
    refactor in progress
    do the work of checking status,
    throw exceptions as appropriate,
    return a tuple
    :param url: url to check
    :return: tuple of integer http status code and dict info about the response
    """
    try:
        status = fetch(url, method="HEAD")
        if status.status_code == http_status.method_not_allowed:
            status = fetch(url, method="GET")
    except requests.exceptions.InvalidSchema as invs:
        raise BadUrl(invs)
    #Let other exceptions bubble up

    req_redirected = (len(status.history) > 0) or status.is_redirect
    info = {'status_code': status.status_code,
            'url': status.url,
            'redirect': False
            }
    if hasattr(status.headers, 'Last-Modified'):
        info['last_modified'] = status.headers['Last-Modified']

    if req_redirected:
        prior = status.history[:-1] # sometimes there are multiples
        info['old_location'] = prior.url
        info['old_status_code'] = prior.status_code
        info['redirect'] = prior.is_redirect
        info['permanent_redirect'] = prior.is_permanent_redirect

    return (status, info)


def host_is_available(host):
    backoff, _ = backoff_detector.get(host)
    if backoff is not None:
        logging.warning("Got a pinboard backoff signal: for {}{}".format(backoff, _))
    return backoff is None


def hostname_is_resolvable(url):
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    try:
        answer = resolver.query(host)
    except Exception as e:
        return False

    try:
        address = socket.gethostbyname(host)
        return address is not None
    except socket.gaierror:
        return False


def fetch(url, method='HEAD'):

    __validate_protocol(url)

    # Enable automatic redirects - we may as well, while we're here
    try:
        if method == 'HEAD':
            status = requests.head(url, allow_redirects=True, timeout=5)
        elif method == 'GET':
            status = requests.get(url, allow_redirects=True, timeout=5)

    except requests.exceptions.ConnectionError as ce:
        if not hostname_is_resolvable(url):
            raise BadHost(ce)
        raise ConnectionError(ce)
    except Exception as e:
        pass
    return status


def __validate_protocol(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme == 'file':
        raise ValueError("file:// urls not supported")
