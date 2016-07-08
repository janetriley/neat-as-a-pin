import logging
import os
from datetime import datetime

import requests
from celery import Celery

from neat_as_a_pin.conf import config
from neat_as_a_pin.src import url_store as q

"""
pinboard_tasks is a set of celery-enabled tasks for pinboard.in related calls

"""

PINBOARD_RATE_LIMIT = '15/m'

logging.basicConfig(filename='pinboard_tasks.log', level=logging.INFO)

API_TOKEN = os.environ.get('API_TOKEN') or config.PINBOARD['api_token']
USERNAME = os.environ.get('USERNAME') or config.PINBOARD['username']
AUTH_TOKEN = API_TOKEN#"{}:{}".format(USERNAME, API_TOKEN)
PINBOARD_API_BASE = "https://api.pinboard.in/v1/"

#app = Celery('pinboard_tasks', broker=config.CELERY['broker_url'], backend=config.CELERY['result_backend'])
app = Celery()
app.config_from_object('conf.celeryconfig')


@app.task(name='pinboard_tasks.timeWas', rate_limit='2/m')
def timeWas():
    print("The time is now {}".format(datetime.now()))


@app.task(name='pinboard_tasks.delete', rate_limit=config.PINBOARD['rate_limit'])
def delete_bookmark():
        item = q.pop(q.DELETE)
        if not item:
            return

        url = item.bookmark['href']
        params = {'url': url, 'auth_token': AUTH_TOKEN,
                  'format':'json'}
        result = requests.get(PINBOARD_API_BASE + "posts/delete", params=params)
        if result.status_code != 200:
            q.add(q.RETRY, item)


@app.task(name='pinboard_tasks.update', rate_limit=config.PINBOARD['rate_limit'])
def update_bookmark_location():
    item = q.pop(q.UPDATE)
    if not item:
        return

    old_url = item.info['old_location']
    try:
        #pb.posts.add(**(item.bookmark))
        # For now, return to queue.
        q.add(q.UPDATE, item)
        # q.add(q.DELETE, item)
    except Exception as e:
        logging.error("Failed on PB add: url: {} error: {}".format(item.bookmark, e))
        q.add(q.UPDATE, item)


if __name__ == '__main__':
    print(API_TOKEN)
    #delete_bookmark()
    #app.worker_main()
    #timeWas.delay(4,4)
    #pass


