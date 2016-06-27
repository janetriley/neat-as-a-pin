"""
Configuration settings used throughout the library and scripts.
"""

# Where to store exports and find pinboard bookmark exports
DATA_DIR = u'../data/'

DEFAULT_REDIS_DB = 0
CELERY_TASK_DB = 1

PINBOARD = {
    "api_token": "change_me",
    "username" : "change_me"
}

REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db_index': DEFAULT_REDIS_DB
}
