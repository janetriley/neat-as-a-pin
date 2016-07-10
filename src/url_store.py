import json
import redis

from neat_as_a_pin.src.common import BookmarkStatus
import neat_as_a_pin.conf.config as config
from requests import codes as http_status

# QUEUES
DONE = u'DONE'
DELETE = u'DELETE'
ERROR = u'ERROR'
NEW_METHOD=u'NEW_METHOD'
INSPECT = u'INSPECT'
RETRY = u'RETRY'
TEST = u'TEST'
TEST2 = u'TEST2'
UPDATE = u'UPDATE'

VALID_QUEUES = set([DONE, UPDATE, DELETE, ERROR, RETRY, NEW_METHOD, INSPECT, TEST, TEST2])

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
    redis_conn = __get_connection()

    current = 0
    interval = 100
    max = redis_conn.llen(queue)

    while current < max:
        # Read in batches for a little more efficiency
        batch = redis_conn.lrange(queue, current, current + interval - 1)
        for item in batch:
            yield __deserialize(item)
        current += interval


def len(queue):
    """
    Return a count of elements in the queue.
    :param queue: queue name
    :return: int
    """
    __validate_queue(queue)
    return __get_connection().llen(queue)


def move(src_queue, dest_queue, conditional):
    """
    Move items from the source queue to the destination queue if conditional is true.

    :param src_queue: where to read items from
    :param dest_queue: where to move items to
    :param conditional: a lambda that returns whether the item should be moved
    """
    __validate_queue(src_queue)
    __validate_queue(dest_queue)

    max_index = (__get_connection().llen(src_queue)) - 1
    min_index = 0
    work_backwards = -1
    # Traverse in reverse order so the current index isn't affected when we move an item
    for current in range(max_index, min_index - 1, work_backwards):
        raw = __get_connection().lindex(src_queue, current)
        bookmark = BookmarkStatus(*(__deserialize(raw)))
        if conditional(bookmark):
            add(dest_queue, bookmark)
            # remove 1 matching item - search back to front, it will most likely be shorter
            num_removed = __get_connection().lrem(src_queue, work_backwards, raw)
            assert num_removed == 1


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


def save():
    """
    Triggers a save on redis.
    If save isn't called, Redis will use its default or configured save behavior.
    """
    __get_connection().save()


def status_to_queue(bookmark_status):
    status = bookmark_status.status_code

    if status == 0:
        return ERROR

    if bookmark_status.is_redirect:
        if status < 300: # redirected to something valid, update bookmark
            return UPDATE
        elif status < 400:
            return RETRY

    # 2xx statuses are successful
    # 1xx statuses are 'provisionally successful' - weird, we'll call it a win
    if status <= 299:
        return DONE

    if status >= 500:  # Server Error
        return INSPECT

    if (status == http_status.not_found or # 404 or  # Not Found
        status == http_status.gone or # 410 or  # Gone
        status == http_status.bad_request): #400):  # Bad Request
            return DELETE

    if (status == http_status.request_timeout or
        status == http_status.too_many_requests):  # Timeout or too many requests
        return RETRY

    return INSPECT

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
