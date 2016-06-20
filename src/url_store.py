import redis
import json
import json, os
from collections import defaultdict


#TODO: shift this to a file
config = {
    'redis': {
    'host':'localhost',
    'port':6379,
    'db_index': 0
    },
    'disk': {
        'output_dir': './'
    }
}


# CONSTANTS
DONE = u'DONE'
DELETE = u'DELETE'
ERROR = u'ERROR'
INSPECT = u'INSPECT'
RETRY = u'RETRY'
TEST = u'TEST'
UPDATE = u'UPDATE'

VALID_QUEUES = set([DONE, UPDATE, DELETE, ERROR, RETRY, TEST])


def add(queue, obj, autosave=True):
    __get_connection().rpush(queue, __serialize(obj))
    if autosave:
        save()


def clear(queue):
    """
    :param queue:
    :return:
    """
    __validate_queue(queue)
    __get_connection().delete(queue)


def iterate(queue):
    __validate_queue(queue)
    redis = __get_connection()

    current = 0
    interval = 100
    max = redis.llen(queue)

    while current < max:
        batch = redis.lrange(queue, current, current+interval - 1)
        results = batch
        for item in batch:
            yield __deserialize(item)
        current += interval


def save():
    """
    Triggers a save on redis.
    If save isn't called, Redis will use its default or configured save behavior.
    """
    __get_connection().save()


def pop(queue):
    """
    Remove and return the first value in a queue.

    :param queue: the queue name to pop from
    :return: an object
    :raises LookupError: if queue name is invalid
    :raises StopIteration: if queue is empty
    """

    if not queue in VALID_QUEUES:
        raise LookupError('no queue named ', queue)

    val = __get_connection().lpop(queue)
    if val is None:
        raise StopIteration('Queue {} is empty'.format(queue))

    return __deserialize(val)


def __deserialize(val):
    if val is None:
        raise ValueError("Trying to decode an empty object")
    val = val.decode('utf-8')
    return json.loads(val)


def __serialize(value):
    return json.dumps(value)


def __get_connection():
    """
    Return a connection to the redis database.  Redis manages connection pooling.
    :return: a Redis client object.
    """
    return redis.StrictRedis(host=config['redis']['host'],
                             port=config['redis']['port'],
                             db=config['redis']['db_index'],
                             encoding='utf-8')

def __validate_queue(queue):
    """
    Verifies the queue is in the list of QUEUES.  Raises an error if not.
    :param queue: Queue name to look up
    :raises LookupError: if invalid queue name
    """
    if not queue in VALID_QUEUES:
        raise LookupError('no queue named ', queue)

    return queue


