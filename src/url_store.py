import json
import redis

from pinboard_cleanup.src.common import BookmarkStatus
from pinboard_cleanup.conf import config

# QUEUES
DONE = u'DONE'
DELETE = u'DELETE'
ERROR = u'ERROR'
INSPECT = u'INSPECT'
RETRY = u'RETRY'
TEST = u'TEST'
UPDATE = u'UPDATE'

VALID_QUEUES = set([DONE, UPDATE, DELETE, ERROR, RETRY, TEST])


def add(queue, obj, autosave=True):
    """
    Add an object to a queue.
    :param queue: queue name
    :param obj: object to add
    :param autosave: save immediately, rather than Redis' default save settings
    """
    __get_connection().rpush(queue, __serialize(obj))
    if autosave:
        save()


def clear(queue):
    """
    Clear a queue.
    :param queue: queue name
    """
    __validate_queue(queue)
    __get_connection().delete(queue)


def iterate(queue):
    """
    Returns a generator for iterating over a redis queue.
    :param queue: queue name to iterate over
    :return: generator
    """
    __validate_queue(queue)
    redis = __get_connection()

    current = 0
    interval = 100
    max = redis.llen(queue)

    while current < max:
        # Read in batches for a little more efficiency
        batch = redis.lrange(queue, current, current+interval - 1)
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
    fields = __deserialize(val)
    return BookmarkStatus(*fields)


def __deserialize(value):
    """
    Convert a value back to utf-8 string, then a json object.
    :param value:
    :return:
    """
    if value is None:
        raise ValueError("Trying to decode an empty object")
    value = value.decode('utf-8')
    return json.loads(value)


def __serialize(value):
    return json.dumps(value)


def __get_connection():
    """
    Return a connection to the redis database.  Redis manages connection pooling.
    :return: a Redis client object.
    """
    return redis.StrictRedis(host=config.REDIS['host'],
                             port=config.REDIS['port'],
                             db=config.REDIS['db_index'],
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


