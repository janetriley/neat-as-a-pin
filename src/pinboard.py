import logging
import os

import ijson
import requests

from neat_as_a_pin.conf import config
from neat_as_a_pin.src import url_store as q
from neat_as_a_pin.src import backoff_detector
from neat_as_a_pin.src.bookmark import Bookmark


"""
pinboard_tasks is a set of celery-enabled tasks for pinboard.in related calls

"""

logging.basicConfig(filename='pinboard_tasks.log', level=logging.INFO)

API_TOKEN = os.environ.get('API_TOKEN') or config.PINBOARD['api_token']

INSPECTION_TAG = 'flagged_for_inspection'

def delete_bookmark():
    """
    Grab a bookmark from the delete queue
    and tell pinboard to delete it
    """
    item = q.pop_bookmark(q.DELETE)
    if not item:
        logging.info("Queue is empty, returning")
        return

    url = item.bookmark['href']

    if not pinboard_is_available():
        q.add(q.DELETE, item)
        return

    params = __base_request_params(url)

    result = requests.get(config.PINBOARD['api_base_url'] + "posts/delete", params=params)
    if result.status_code == requests.codes.too_many_requests: # 429 - Too many requests - give it a rest
        logging.warning("Pinboard returned error 429 - adding backoff flag")
        q.add(q.DELETE, item)
    elif result.status_code != requests.codes.ok:
        q.add(q.RETRY, item)
    return result.status_code


def pinboard_is_available():
    backoff, _ = backoff_detector.get(config.PINBOARD['pinboard_server'])
    if backoff is not None:
        logging.warning("Got a pinboard backoff signal: for {}{}".format(backoff, _))
    return backoff is None

def __base_request_params(url):
    """
    Return a dict with the parameters common to all pinboard API requests
    :param url: the Pinboard bookmark's URL, which pinboard uses as unique identifier
    :return: dict
    """
    return {'url': url,
            'auth_token': API_TOKEN,
            'format': 'json'
            }

def __full_request_params(url, bookmark):
    """
    The full set of Pinboard API requests that this script uses
    :param url: the Pinboard bookmark's URL, which pinboard uses as unique identifier
    :param bookmark: the Pinboard bookmark. Expects it started out as an export and all fields are present.
    :return: dict
    """
    params = __base_request_params(url)
    params['description'] = bookmark['description']
    params['tags'] = bookmark['tags']
    params['dt'] =  bookmark['time']
    params['shared'] = bookmark['shared']
    params['toread'] = bookmark['toread']



def update_bookmark_location():
    """
    Update a pinboard bookmark.  Create a new bookmark with the new location.
    If successful, add the old bookmark to the delete queue.
    #TODO? call the delete task in celery? will it run amok?
    """

    if not pinboard_is_available():
        logging.info("Pinboard is unavailable.")
        return

    item = q.pop_bookmark(q.UPDATE)

    if not item:
        logging.info("Queue is empty, returning")
        return

    logging.info("Starting an update")

    bookmark = item.bookmark
    params = __full_request_params(item.info['url'], bookmark)
    params['replace'] = 'no', # throw the error so we can check it out

    """
    params = {'url': item.info['url'],
              'auth_token': API_TOKEN,
              'format': 'json',
              'description': bookmark['description'],
              'tags': bookmark['tags'],
              'dt': bookmark['time'],
              'replace': 'no',  # throw the error so we can check it out
              'shared': bookmark['shared'],
              'toread': bookmark['toread']
              }
    """
    try:
        response = requests.get(config.PINBOARD['api_base_url'] + 'posts/add', params )

        if response.status_code == requests.codes.ok:
            logging.info("Got a success code, queueing for deletion")
            #old_url = bookmark['href']# item.info['old_location']
            old_bookmark = Bookmark(bookmark={'href': bookmark['href']}, info=item.info)
            q.add(q.DELETE, old_bookmark)
        else:
            logging.info("booo, got a code of {}".format(response.status_code))
            q.add(q.UPDATE, item)

    except Exception as e:
        logging.error("Failed on PB add: url: {} error: {}".format(item.bookmark, e))
        q.add(q.RETRY, item) #inspect

def tag_for_inspection():
    def update_bookmark_location():
        """
        Update a pinboard bookmark.  Create a new bookmark with the new location.
        If successful, add the old bookmark to the delete queue.
        #TODO? call the delete task in celery? will it run amok?
        """

        if not pinboard_is_available():
            logging.info("Pinboard is unavailable.")
            return

        item = q.pop_bookmark(q.INSPECT)

        if not item:
            logging.info("Queue is empty, returning")
            return

        logging.info("Starting an update")

        bookmark = item.bookmark

        if (not bookmark['tags'] or
            not INSPECTION_TAG in bookmark['tags']):
            bookmark['tags'] = INSPECTION_TAG + " " + bookmark['tags']
        params = __full_request_params(item.info['url'], bookmark)
        params['replace'] = 'yes'

        try:
            response = requests.get(config.PINBOARD['api_base_url'] + 'posts/add', params)

            if response.status_code == requests.codes.ok:
                logging.info("Successfully updated tag")
            else:
                logging.info("booo, got a code of {}".format(response.status_code))
                q.add(q.INSPECT, item)

        except Exception as e:
            logging.error("Failed on PB tag for inspection: url: {} error: {}".format(item.bookmark, e))
            q.add(q.INSPECT, item)  # inspect


def read_pinboard_exports(pinboard_bookmarks_file):
    """
    Read a pinboard_exports json file as a stream
    returns bookmarks
    See https://pinboard.in/export/  to export your bookmarks.
    :param pinboard_bookmarks_file: filepath of pinboard exports file to read from
    :return: a generator which reads one item at a time
    """
    with open(pinboard_bookmarks_file, "r") as fp:
        lines = ijson.items(fp, 'item')
        for line in lines:
            yield line
