import common

if __name__ == "__main__":
    with open("../data/export_DONE.json", 'r') as fp:
        parser = common.get_bookmarks_from_file(fp)
        for i in range(1,10):
            item = next(parser)
            print(item)