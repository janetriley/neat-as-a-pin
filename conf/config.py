"""
Configuration settings used throughout the library and scripts.
"""

# Where to store exports and find pinboard bookmark exports
DATA_DIR = u'../data/'

DEFAULT_REDIS_DB = 0
CELERY_TASK_DB = 1

PINBOARD = {
    "api_token": 'change_me',
    "username" : 'change_me',
    "rate_limit": '15/m' # 1 per 3 seconds, but let's be polite - 15 instead of 20
}

REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db_index': DEFAULT_REDIS_DB,
    'celery_db': 1,
    'backoff_db': 2
}
