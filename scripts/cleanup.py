import datetime

import common
import url_checker
import url_store
from config import DATA_DIR


def pick_queue(bookmark_status):

    status = bookmark_status.status_code

    if status == 0:
        return url_store.ERROR

    if bookmark_status.is_redirect:
        if status < 300:
            return url_store.UPDATE
        elif status >= 300:
            return url_store.RETRY

    # 2xx statuses are successful
    # 1xx statuses are provisionally successful - weird, haven't seen any, we'll call it a win
    if status <= 299:
        return url_store.DONE

    if status >= 500: # Server Error
        return url_store.INSPECT

    if( status == 404 or # Not Found
        status == 410 or # Gone
        status == 400 ): # Bad Request
        return url_store.DELETE

    if status == 408 or status == 429 : # Timeout or too many requests
        return url_store.RETRY

    return url_store.INSPECT



if __name__ == "__main__":
    print("Woot!")

    DATA_FILE = DATA_DIR + '/pinboard_export.json'
    #prefix, event, value = pb.parse()
    bookmarks = common.get_bookmarks_from_file(DATA_FILE)

    counter = 1
    for bookmark in bookmarks:
        status = url_checker.check_status(bookmark)
        queue = pick_queue(status)
        url_store.add(queue, status, autosave=False)

        counter += 1
        #if counter > 100:
        #    break
        if counter % 100 == 0:
            url_store.save()
        if counter % 400 == 0:
            print("At #{} {}".format(counter, datetime.datetime.now()))

    #writer.close_all()
