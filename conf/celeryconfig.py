## Broker settings.
BROKER_URL = 'redis://localhost:6379/1'

## Using the database to store task state and results.
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
