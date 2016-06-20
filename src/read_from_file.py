import os
import modify_pinboard as pb

if __name__ == "__main__":
    with open("./DONE.json", 'r') as fp:
        parser = pb.get_bookmarks(fp)
        for i in range(1,10):
            item = next(parser)
            print(item)