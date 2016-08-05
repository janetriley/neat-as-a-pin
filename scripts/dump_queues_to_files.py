import json
import logging
from datetime import datetime

from neat_as_a_pin.conf import config
from neat_as_a_pin.src import url_store as q
from neat_as_a_pin.src.bookmark import Bookmark
from collections import namedtuple
import ijson
"""
Dump all the queues to files

"""

# Deprecated - update to reflect current format
BookmarkStatusTuple = namedtuple('BookmarkStatus', ['status_code', 'is_redirect', 'bookmark', 'info', 'errors'])


def get_bookmarks_from_file(fp):
    """
    Read a file of json bookmarks as a stream
    :param fp: file object to read from
    :return: a generator which reads one item at a time
    """
    lines = ijson.items(fp, 'item')
    for line in lines:
        fields = BookmarkStatusTuple(*line)
        yield Bookmark(bookmark=fields.bookmark, info=fields.info, errors=fields.errors)


if __name__ == "__main__":

    logging.basicConfig(filename='dump_to_queue.log', level=logging.INFO)

    counter = 0
    print("Starting at ", datetime.now())
    for queue in q.VALID_QUEUES:
        with open('{}/export_{}.json'.format(config.DATA_DIR, str(queue)), 'w') as fp:
            logging.info("Exporting queue {}".format(queue))

            bookmarks = q.iterate(queue)
            # Make it valid JSON - surround content with [ ] , add comma between entries
            fp.write("[")

            for bookmark in bookmarks:
                counter = 0
                try:
                    fp.writelines(json.dumps(bookmark) + ",\n")
                    if counter % 100 == 0:
                        fp.flush()
                except Exception as e:
                    logging.error("Error writing: {}\nfor bookmark:{}".format(e, json.dumps(bookmark)))

                counter += 1

                if counter % 500 == 0:
                    print("Finished {} at {}".format(counter, datetime.now()))

            fp.write("]\n")

    logging.info("Done.")
