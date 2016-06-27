import neat_as_a_pin.src.url_store as q

"""
It's dead, Jim.
Move RETRYs with status 404 to the DELETE queue.
"""

if __name__ == "__main__":
    is_gone = lambda x: x.status_code == 404
    q.move(q.RETRY, q.DELETE, is_gone)
