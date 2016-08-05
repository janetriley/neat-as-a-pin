import neat_as_a_pin.src.url_store as q
from requests import codes

"""

Move RETRYs and INSPECTs with status 405 to a queue.  They'll be retried with GET.
"""

if __name__ == "__main__":
    is_gone = lambda x: x.status_code == codes.method_not_allowed
    q.move(q.RETRY, q.NEW_METHOD, is_gone)
    q.move(q.INSPECT, q.NEW_METHOD, is_gone)
