drett
=====

Resource tracking service for automated engines that allocate and---hopefully---
free up resources without human interaction. For example, auto-scaling, or active
monitoring (probing) of IaaS cloud infrastructures with test instances.

The problem with these is that, sometimes, resources may not be freed (need kill -9,
network problems, bugs, etc.) So the allocated resources are stuck, possibly with
a ticking accounting clock.

drett offers a simple way to track these resources. The clients can
- register the intent of allocating a resource (so if the resource is allocated, but the client side only receives an error, human intervention can fix the problem)
- register the successful allocation of the resource
- register the successful release of the resource
- do the same with batches of allocations

drett is now in pre-pre-alpha condition, but it works. Only MongoDB is supported as
a backend yet. The API may change drastically (the main goal is simplicity on
client side). Later even garbage collection will be possible running on the backend
database. 

Files
-----

Server side:
- drett\_server.py -- CGI script as server. Apache must be configured accordingly.
- config.yaml -- main configuration file
- logging.yaml -- logging configuration
- mongo.yaml -- MongoDB specific configuration
- plugins/mongo\_connector.py -- MongoDB connector
- server\_requirements.txt, plugins/mongo\_requirements.txt -- Python requirements

Client side:
- drett.py -- A single module containing all services. This file also contains
              example/test code.
- client\_requirements.py -- Client-side Python requirements. This is to be kept
                             as short as possible (currently, it uses only standard
                             libraries).

Misc
----

Environment: Python 2.7

License: LGPL 3.0 (client, plugins, libs) and GPL 3.0 (server)

Contact: Adam Visegradi "a.visegradi@gmail.com"
