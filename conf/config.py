
# Where to store exports and find pinboard bookmark exports
DATA_DIR = u'../data/'

DEFAULT_REDIS_DB = 0
CELERY_TASK_DB = 1

REDIS = {
        'host':'localhost',
        'port':6379,
        'db_index': DEFAULT_REDIS_DB
        }


CELERY = {
    'host': 'localhost',
    'port': 6379,
    'db_index': CELERY_TASK_DB
}

PINBOARD_API_KEY = "change_me"