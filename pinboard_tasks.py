from datetime import datetime

from celery import Celery
import sys
sys.path.append('src')
sys.path.append('conf')

import pinboard
import config
import os
import url_store as q
import logging

PINBOARD_RATE_LIMIT = '15/m'

logging.basicConfig(filename='pinboard_tasks.log', level=logging.INFO)
"""
pinboard_tasks is a set of celery-enabled tasks for pinboard.in related calls

Note that it must be run in Python 2.7 due to a pinboard library dependency.
"""

#BROKER_URL = 'redis://localhost:6379/0'
# redis backend
#CELERY_RESULT_BACKEND = config.CELERY['result_backend']

API_TOKEN = os.environ.get('API_TOKEN') or config.PINBOARD['api_token']

app = Celery('pinboard_tasks', broker=config.CELERY['broker_url'], backend=config.CELERY['result_backend'])

pb = pinboard.Pinboard(API_TOKEN)


@app.task(name='pinboard_tasks.timeWas', rate_limit='2/m')
def timeWas():
    print("The time is now {}".format(datetime.now()))


@app.task(name='pinboard_tasks.delete', rate_limit=PINBOARD_RATE_LIMIT)
def delete_bookmark():
        bookmark = q.pop(q.DELETE)
        url = bookmark.bookmark['href']
        pb.posts.delete(url=url)
        #for now - don't remove from queue
        ##q.add(q.DELETE, bookmark)


@app.task(name='pinboard_tasks.update', rate_limit=PINBOARD_RATE_LIMIT)
def update_bookmark_location():
    item = q.pop(q.UPDATE)
    #TODO: confirm bookmark's href contains new location
    old_url = item.info['old_location']
    try:
        pb.posts.add(**(item.bookmark))
        # For now, return to queue.
        q.add(q.UPDATE, item)
        # q.add(q.DELETE, item)
    except Exception as e:
        logging.error("Failed on PB add: url: {} error: {}".format(item.bookmark, e))
        q.add(q.UPDATE, item)


if __name__ == '__main__':
    #everything getting set right?
    print(API_TOKEN)
    #delete_bookmark()
    #update_bookmark_location()
    pb.tags.delete(tag='delete_me')
