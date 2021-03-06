"""
Configuration settings used throughout the library and scripts.
"""

# Where to store exports and find pinboard bookmark exports
DATA_DIR = u'../data/'

DEFAULT_REDIS_DB = 3
CELERY_TASK_DB = 1
BACKOFF_DB = 2

PINBOARD = {
    "api_token": 'change_me',
    "username" : 'change_me',
    "rate_limit": '15/m', # 1 per 3 seconds, but let's be polite - 15 instead of 20
    "pinboard_server": "api.pinboard.in",
    "api_base_url": "https://api.pinboard.in/v1/"
}

REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db_index': DEFAULT_REDIS_DB,
    'celery_db': CELERY_TASK_DB,
    'backoff_db': BACKOFF_DB
}
CELERY = {
    'broker_url': 'redis://localhost:6379/{}'.format(REDIS['celery_db']),
    'result_backend': 'redis://localhost:6379/{}'.format(REDIS['celery_db'])
}
