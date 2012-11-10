Little project using flask + redis + memcached + restmq

just a processing factory for a command line OCR
basically the http api frontend puts jobs on restmq queue
a worker is polling with a few threads to the restmq queue
pickup a job, process it, put the result in a redis key
and in a duplicates key, so when the same image come in
the worker will pick up the result without call the OCR,
and when you poll for the result from the http api it 
will look for a result on the UID based key.Memcached is 
used as counter storage.
Thats all!

You will need:
Python 2.7.x
RestMQ
Memcached and the Memcache for Python interface
Redis and Redis client for Python
and Flask.
Fire up RestMQ
Fire up memcached
Fire up Redis
and finally:
$ python servers/http_api.py

I hope you find this useful.

NOTE: This is not and doesn't include any OCR software!

*This is not too much but is released as GPL, have you heard that? yes! it's
GPL'ed!
