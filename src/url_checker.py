# This will be used by Python 2.x and 3.x clients
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse
from common import BookmarkStatus

import requests


def check_status(bookmark):
    try:
        status = fetch(bookmark['href'])
        req_redirected = ( len(status.history) > 0) or status.is_redirect
        info = {'status_code': status.status_code,
                           'url': status.url,
                           'redirect': False
                           }
        if hasattr(status.headers, 'Last-Modified'):
            info['last_modified'] = status.headers['Last-Modified']

        if req_redirected:
            prior = status.history[0]
            info['old_location'] = prior.url
            info['old_status_code'] = prior.status_code
            info['redirect'] = prior.is_redirect
            info['permanent_redirect'] = prior.is_permanent_redirect

        return BookmarkStatus(status.status_code,
                              info['redirect'],
                              bookmark,
                              info,
                              None
                              )
    except Exception as e:
        return BookmarkStatus(0,
                              False,
                              bookmark,
                              {},
                              {'type': type(e).__name__,
                               'msg': str(e)}
                              )


def check_url_status(url):
    try:
        return requests.head(url)
    except requests.exceptions.SSLError as e:
        print("SSL error for url {}".format(url))
    except Exception as es:
        print("Error {} for url {}".format(es, url))
    return None


def fetch(url):
    __validate_protocol(url)

    # Enable automatic redirects - we may as well, while we're here
    status = requests.head(url, allow_redirects=True, timeout=5)
    return status


def __validate_protocol(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme == 'file':
        raise ValueError("file:// urls not supported")
