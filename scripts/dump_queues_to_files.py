import json
import logging
from datetime import datetime

from pinboard_cleanup.conf import config
from pinboard_cleanup.src import url_store as q

"""
Dump all the queues to files

"""

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
