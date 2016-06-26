from collections import namedtuple

import ijson

BookmarkStatus = namedtuple('BookmarkStatus', ['status_code', 'is_redirect', 'bookmark', 'info', 'errors'])


def get_bookmarks_from_file(fp):
    lines = ijson.items(fp, 'item')
    for line in lines:
        yield BookmarkStatus(*line)
