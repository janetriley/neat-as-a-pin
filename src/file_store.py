import json
import os
from collections import defaultdict


class ResultsLogger:

    def __init__(self):
        self.fps = defaultdict(None)

    def __del__(self):
        self.close_all()

    def close_all(self):
        for fp in self.fps.values():
            if not fp:
                continue
            os.close(fp)

    def status_bucket(self, queue):
        fp = self.fps.get(queue, None)
        if not fp:
            fp = open(str(queue) + '.json', 'w')
            self.fps[queue] = fp
        return fp

    def add(self, bookmark, status):
        fp = self.status_bucket(status)
        fp.writelines(json.dumps(bookmark) + "\n")
        fp.flush()
