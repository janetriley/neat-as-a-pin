import json
import redis

from neat_as_a_pin.src.bookmark import Bookmark
import neat_as_a_pin.conf.config as config
from requests import codes as http_status_codes

# QUEUES
DONE = u'DONE'
DELETE = u'DELETE'
ERROR = u'ERROR'
NEW_METHOD=u'NEW_METHOD'
INBOX=u'INBOX'
INSPECT = u'INSPECT'
RETRY = u'RETRY'
TEST = u'TEST'
TEST2 = u'TEST2'
UPDATE = u'UPDATE'


VALID_QUEUES = set([INBOX, DONE, UPDATE, DELETE, ERROR, RETRY, NEW_METHOD, INSPECT, TEST, TEST2])

def add(queue, obj, autosave=True):
    """
    Add an object to a queue.
    :param queue: queue name
    :param obj: object to add
    :param autosave: save immediately, rather than Redis' default save settings
    """
    if hasattr(obj, 'to_json'):
        values = obj.to_json()
    else:
        values = obj
    __get_connection().rpush(queue, __serialize(values))

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
        fields=__deserialize(raw)
        bookmark= Bookmark.from_json(fields)

        if conditional(bookmark):
            add(dest_queue, bookmark)
            # remove 1 matching item - search back to front, it will most likely be shorter
            num_removed = __get_connection().lrem(src_queue, work_backwards, raw)
            assert num_removed == 1


def pop_bookmark(queue):
    """
    Remove and return the first value in a queue.
    :param queue: the queue name to pop from
    :return: a Bookmark object
    """

    fields = pop_json(queue)
    return Bookmark.from_json(fields)


def pop_json(queue):
    """
    Remove and return the first value in a queue.

    :param queue: the queue name to pop from
    :return: a JSON object
    :raises LookupError: if queue name is invalid
    :raises StopIteration: if queue is empty
    """

    if not queue in VALID_QUEUES:
        raise LookupError('no queue named ', queue)
    val = __get_connection().lpop(queue)
    if val is None:
        raise StopIteration('Queue {} is empty'.format(queue))
    fields = __deserialize(val)
    return fields


def save():
    """
    Triggers a save on redis.
    If save isn't called, Redis will use its default or configured save behavior.
    """
    __get_connection().save()


def status_to_queue(query_response):
    """
    :param query_response: an http.request.Response
    :return: a destination queue
    """

    if not query_response or not hasattr(query_response, 'status_code'):
        return ERROR

    status_code = query_response.status_code

    if not status_code:
        return ERROR

    if query_response.is_redirect:
        # Responses that followed redirects will show the http status of the final request
        # Check if it's a redirect first; the bookmark will need to be updated.
        if status_code < 300: # redirected to something valid, update bookmark
            return UPDATE
        elif status_code < 400: # redirected to another redirect, retry
            return RETRY

    # 2xx statuses are successful
    # 1xx statuses are 'provisionally successful' - we'll call that a yes
    if status_code <= 299:
        return DONE

    if status_code < 400:  # redirected to another redirect, retry
        return RETRY

    if (status_code == http_status_codes.not_found or  # http status 404
        status_code == http_status_codes.gone or       # http status 410
        status_code == http_status_codes.bad_request): # http status 400
            return DELETE

    if (status_code == http_status_codes.request_timeout or
        status_code == http_status_codes.too_many_requests):  # Timeout or too many requests
        return RETRY

    if status_code >= 500:  # Server Error
        return INSPECT

    return INSPECT

def __deserialize(value):
    """
    Convert a bookmark back to a json object. utf-8 string, then a json object.
    :param value: the value to decode
    :return: a json object
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
