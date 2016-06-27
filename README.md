# neat-as-a-pin

A set of scripts to tidy up Pinboard.in bookmarks.  

## TODO:
* add a backoff mechanism - on HTTP status 429, add host to a redis hash w/timestamp; check queue for host before any requests
* dump all the deletes in the queue, let celery go to town
* add celery task for moved urls:  add new bookmark, delete old
* add celery task to tag RETRY bookmarks for human inspection
* declare victory