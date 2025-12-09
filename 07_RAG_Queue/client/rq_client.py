from redis import Redis
from rq import Queue

queue = Queue(connection=Redis(
    host="localhost",
    port=6379,
))

'''
Fast API server POST /chat{message} => enqueue the message to RQ Queue => processor function will take this query, process it and store it in redis.
/result => user can use this route to fetch result back from redis using a job id.
'''
