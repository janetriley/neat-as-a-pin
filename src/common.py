from collections import namedtuple, defaultdict

import ijson

# A bookmark plus data from the http status check
BookmarkStatus = namedtuple('BookmarkStatus', ['status_code', 'is_redirect', 'bookmark', 'info', 'errors'])

class BookmarkStatus2:
    def __init__(self, status_code, is_redirect, bookmark,
                 info=defaultdict(None), errors=None, status=None):
        self.__legacy_bookmark = BookmarkStatus(status_code, is_redirect, bookmark, info, errors)
        self.bookmark = bookmark
        self.info = info
        self.errors = errors
        self._status = status or defaultdict(None)

    @property
    def status_code(self):
        if self._status:
            return self._status['status_code']
        return None
        #return self.__legacy_bookmark.status_code

    @property
    def is_redirect(self):
        return self._status['is_redirect']
        """
        if not self.status:
            return False
        return self.status.is_redirect or (self.status.history and len(self.status.history) > 0)
        """

    @property
    def bookmark(self):
        return self._bookmark

    @bookmark.setter
    def bookmark(self, value):
        self._bookmark = value

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value):
        self._info = value



    @property
    def errors(self):
        return self._errors
        #return self.__legacy_bookmark.errors

    @errors.setter
    def errors(self, value):
        self._errors = value


def get_bookmarks_from_file(fp):
    """
    Read a file of json bookmarks as a stream
    :param fp: file object to read from
    :return: a generator which reads one item at a time
    """
    lines = ijson.items(fp, 'item')
    for line in lines:
        yield BookmarkStatus(*line)
