import config
import url_store as q
import common

if __name__ == "__main__":
    is_gone = lambda x: x.status_code == 404
    q.move(q.RETRY, q.DELETE, is_gone)

