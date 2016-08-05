from collections import namedtuple, defaultdict

import ijson

# A bookmark plus data from the http status check

class Bookmark:
    def __init__(self, bookmark=None, info=defaultdict(None), errors=None, status=None):
        self.bookmark = bookmark
        self.info = info
        self.errors = errors
        self.status = status

    def __eq__(self,other):
        return (self.bookmark == other.bookmark and
                self.status == other.status and  # omit?
                self.info == other.info and
                self.errors == other.errors)

    def to_json(self):
        return {
            'bookmark':self.bookmark,
            'info': self.info,
            # status is ommitted, http.request.Response doesn't serialize to json
            'errors': self.errors #omit? they're volatile
        }

    @staticmethod
    def from_json(values):
        b = Bookmark()
        if 'bookmark' in values:
            b.bookmark = values['bookmark']
        if 'info' in values:
            b.info = values['info']
        if 'errors' in values:
            b.errors = values['errors']
        return b

    @property
    def status_code(self):
        if self._status:
            return self._status.get('status_code')
        return None

    @property
    def is_redirect(self):
        return self._info.get('redirect', False)

    @property
    def bookmark(self):
        return self._bookmark

    @bookmark.setter
    def bookmark(self, value):
        self._bookmark = value

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, value):
        self._errors = value

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value):
        self._info = defaultdict(lambda:None, value)
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def current_url(self):
        return self._info['url'] if self._info['url'] else self._bookmark['href']
