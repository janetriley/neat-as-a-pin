from collections import namedtuple

import ijson

# A bookmark plus data from the http status check
BookmarkStatus = namedtuple('BookmarkStatus', ['status_code', 'is_redirect', 'bookmark', 'info', 'errors'])


def get_bookmarks_from_file(fp):
    """
    Read a file of json bookmarks as a stream
    :param fp: file object to read from
    :return: a generator which reads one item at a time
    """
    lines = ijson.items(fp, 'item')
    for line in lines:
        yield BookmarkStatus(*line)
