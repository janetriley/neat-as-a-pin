# neat-as-a-pin

A set of scripts to tidy up [Pinboard.in](http://pinboard.in) bookmarks.  

Read bookmarks from a Pinboard export file and get the URL's http status.  Delete the deleted, update the moved. 

## TODO:
* wire up the backoff detector - on HTTP status 429, add host to a redis hash w/timestamp; check queue for host before any requests
* dump all the deletes into the work queue, let celery go to town
* add celery task for moved urls: add new bookmark, delete old
* add celery task to tag RETRY bookmarks for human inspection
* declare victory
