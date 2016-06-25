from celery import Celery
from pinboard import Pinboard
from datetime import datetime
BROKER_URL = 'redis://localhost:6379/0'
# redis backend
CELERY_RESULT_BACKEND = 'redis://'
API_TOKEN = 'move_to_config'

app = Celery('pinboard_tasks', broker='redis://localhost:6379/1', backend='redis://localhost:6379/1')


@app.task(name='pinboard_tasks.timeWas',rate_limit='2/m')
def timeWas():
    print("The time is now {}".format(datetime.now()))


#@app.task
def delete_bookmark():
        pb = Pinboard(API_TOKEN)
        url = u'nonesuch'
        pb.posts.delete()
        # pop one from delete
        # call pinboard.delete
        # sleep

"""
if __name__ == '__main__':
    app.worker_main()
"""