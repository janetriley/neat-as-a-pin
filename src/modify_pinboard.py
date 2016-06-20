#import pinboard
import ijson
import url_checker


def get_bookmarks(fp):
    lines = ijson.items(fp, 'item')
    for line in lines:
        yield  url_checker.BookmarkStatus(*line)
