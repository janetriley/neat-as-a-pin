# neat-as-a-pin

A set of scripts to tidy up [Pinboard.in](http://pinboard.in) bookmarks.  

Read bookmarks from a Pinboard export file and get the URL's http status.  Delete the deleted, update the moved. 

## Entry Points

The cleanup process is broken into separate scripts for now. Once the steps have been tested they may be streamlined to a single pipeline. 

`scripts/check_url_http_status.py` checks the http status of each bookmark in a pinboard export file, 
    and sends them to Redis queues for further actions.  Start here. 
    
`scripts/move_retry_404s_to_delete_queue.py` Some bookmarks redirected to dead links, 
    and were added to the RETRY queue for further attention.  Move them to DELETE. \#TODO: detect this case during triage. 

`scripts/dump_queues_to_file.py` is a backup script to export the Redis queues to disk. A safety feature during development. 

pinboard_tasks.py is the entry point for celery workers.



## TODO:
* wire up the backoff detector - on HTTP status 429, add host to a redis hash w/timestamp; check queue for host before any requests
* dump all the deletes into the work queue, let celery go to town
* add celery task for moved urls: add new bookmark, delete old
* add celery task to tag RETRY bookmarks for human inspection
* declare victory
