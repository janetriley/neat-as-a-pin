import os
import datetime

import neat_as_a_pin.src.pinboard
from neat_as_a_pin.conf import config
from neat_as_a_pin.src import url_store

"""
Given a pinboard export file, do an HTTP HEAD request on each link.
Save results to a redis queue based on HTTP status and next action to take.
"""

if __name__ == "__main__":
    pinboard_bookmarks_file = os.environ.get('FILE') or (config.DATA_DIR + '/pinboard_export.json')

    bookmarks = neat_as_a_pin.src.pinboard.read_pinboard_exports(pinboard_bookmarks_file)

    counter = 0

    for bookmark in bookmarks:
        url_store.add(url_store.INBOX, bookmark, autosave=False)
        counter += 1
        if counter % 100 == 0:
            url_store.save()
            break
        if counter % 400 == 0:
            print("At #{} {}".format(counter, datetime.datetime.now()))

    url_store.save()
    print("Finished at #{}, total {}".format(datetime.datetime.now(), counter))
