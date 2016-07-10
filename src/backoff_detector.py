import redis
from neat_as_a_pin.conf import config
import time

from urllib.parse import urlparse


"""
Backoff detector tracks whether a site has
recently signalled that requests should be throttled
"""


class RateLimitExceeded(Exception):
    """
    Signals that a host has been flagged for too many requests and is in timeout
    """
    def __init__(self, *args):
      self.args = args

DEFAULT_BACKOFF_SECONDS = 30 * 1000


def get(hostname):
    """
    Get the remaining time and interval for a hostname, if any.
    Return None, None if not set.
    :param hostname: hostname to look up
    :return: A tuple of seconds remaining until backoff is over
            and the current interval, to facilitating progressive backoff times
    """

    redis_conn = __get_connection()
    values = redis_conn.hgetall(hostname)
    if not values:
        return (None, None)

    seconds_remaining = float(values[b'next_time']) - time.time()
    if seconds_remaining <= 0:
        #remove the flag, we're done
        clear(hostname)
        return (None, None)
    return (seconds_remaining, int(values[b'interval']))


def set(hostname, interval=DEFAULT_BACKOFF_SECONDS):
    """
    Add a hostname to the backoff queue
    :param hostname: hostname for key
    :param interval: interval to wait in seconds
    """
    redis_conn = __get_connection()
    redis_conn.hmset(hostname, {'next_time': time.time() + interval, 'interval': interval})


def clear(hostname):
    """
    Remove a hostname from backoff status.
    :param hostname: the key to look for
    """
    redis_conn = __get_connection()
    redis_conn.delete(hostname)


def parse_hostname(url):
        parsed_url = urlparse(url)
        return parsed_url['hostname']


def __get_connection():
    """
    Return a connection to the redis database.  Redis manages connection pooling.
    :return: a Redis client object.
    """
    return redis.StrictRedis(host=config.REDIS['host'],
                             port=config.REDIS['port'],
                             db=config.REDIS['backoff_db'],
                             encoding='utf-8')
