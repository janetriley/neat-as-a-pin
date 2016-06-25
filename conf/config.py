
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
    'broker_url':'redis://localhost:6379/' + str(CELERY_TASK_DB),
    'result_backend':'redis://localhost:6379/1',
    'host': 'localhost',
    'port': 6379,
    'db_index': CELERY_TASK_DB
}
BROKER_URL = 'redis://localhost:6379/0'

PINBOARD = {
    "api_token": "change_me"
}
