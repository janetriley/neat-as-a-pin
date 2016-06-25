from datetime import datetime

from celery import Celery
import pinboard
import config
import os
import url_store as q

BROKER_URL = 'redis://localhost:6379/0'
# redis backend
CELERY_RESULT_BACKEND = config.CELERY['result_backend']
API_TOKEN = os.environ['API_TOKEN'] or config.PINBOARD['api_token']

app = Celery('pinboard_tasks', broker=config.CELERY['broker_url'], backend=config.CELERY['result_backend')

pb = pinboard.Pinboard(API_TOKEN)

@app.task(name='pinboard_tasks.timeWas',rate_limit='2/m')
def timeWas():
    print("The time is now {}".format(datetime.now()))


#@app.task
def delete_bookmark():
        bookmark = q.pop(q.DELETE)
        url = bookmark.bookmark['href']
        pb.posts.delete(url)
        q.add(q.DELETE, bookmark)



if __name__ == '__main__':
    print( API_TOKEN )
    delete_bookmark()
