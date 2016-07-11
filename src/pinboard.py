import logging
import os
import requests

from neat_as_a_pin.conf import config
from neat_as_a_pin.src import url_store as q
from neat_as_a_pin.src import backoff_detector
from neat_as_a_pin.src.common import BookmarkStatus, BookmarkStatus2


"""
pinboard_tasks is a set of celery-enabled tasks for pinboard.in related calls

"""

logging.basicConfig(filename='pinboard_tasks.log', level=logging.INFO)

API_TOKEN = os.environ.get('API_TOKEN') or config.PINBOARD['api_token']


def delete_bookmark():
    """
    Grab a bookmark from the delete queue
    and tell pinboard to delete it
    """
    item = q.pop(q.DELETE)
    if not item:
        logging.info("Queue is empty, returning")
        return

    url = item.bookmark['href']

    if not pinboard_is_available():
        q.add(q.DELETE, item)
        return

    params = {'url': url, 'auth_token': API_TOKEN,
              'format':'json'}
    result = requests.get(config.PINBOARD['api_base_url'] + "posts/delete", params=params)
    if result.status_code == 429: # Too many requests - give it a rest
        logging.warning("Pinboard returned error 429 - adding backoff flag")
        q.add(q.DELETE, item)
    elif result.status_code != 200:
        q.add(q.RETRY, item)
    return result.status_code


def pinboard_is_available():
    backoff, _ = backoff_detector.get(config.PINBOARD['pinboard_server'])
    if backoff is not None:
        logging.warning("Got a pinboard backoff signal: for {}{}".format(backoff, _))
    return backoff is None


def update_bookmark_location():
    """
    Update a pinboard bookmark.  Create a new bookmark with the new location.
    If successful, add the old bookmark to the delete queue.
    #TODO? call the delete task in celery? will it run amok?
    """

    if not pinboard_is_available():
        logging.info("Pinboard is unavailable.")
        return

    item = q.pop(q.UPDATE)

    if not item:
        logging.info("Queue is empty, returning")
        return

    logging.info("Starting an update")

    bookmark = item.bookmark
    params = {'url': item.info['url'],
              'auth_token': API_TOKEN,
              'format': 'json',
              'description': bookmark['description'],
              'tags': bookmark['tags'],
              'dt': bookmark['time'],
              'replace': 'no', # throw the error so we can check it out
              'shared': bookmark['shared'],
              'toread': bookmark['toread']
              }
    try:
        response = requests.get(config.PINBOARD['api_base_url'] + 'posts/add', params )

        if response.status_code == requests.codes.ok:
            logging.info("Got a success code, queueing for deletion")
            old_url = item.info['old_location']
            old_bookmark = BookmarkStatus(404, False, {'href':old_url},{},{})
            q.add(q.DELETE, old_bookmark)
        else:
            logging.info("booo, got a code of {}".format(response.status_code))
            q.add(q.UPDATE, item)

    except Exception as e:
        logging.error("Failed on PB add: url: {} error: {}".format(item.bookmark, e))
        q.add(q.RETRY, item) #inspect

