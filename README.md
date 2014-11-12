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

Server side (server/):
- drett\_server -- Application server. Uses Flask.
- drett\_cgi\_server.py -- CGI script as server. Apache must be configured accordingly. !!! Not maintained, probably won't work.
- drett/utils/command.py -- Abstract command class
- testconfig/ -- Configuration files for testing and as example
    - config.yaml -- main configuration file
    - logging.yaml -- logging configuration
    - mongo.yaml -- MongoDB specific configuration

MongoDB Connector (drett-mongo/):
- drett/plugins/mongo/connector.py -- The MongoDB connector implementation

Client side (client/):
- drett/client/drett.py -- A single module containing all services.
- drett-client-test -- Test client; configuration is wired in.

Trying
------

Using [virtualenv](http://virtualenv.readthedocs.org/en/latest/) is highly
recommended.

You need two terminals, one for the server, one for the client.

Server side:

```bash
virtualenv dserver
source dserver/bin/activate
cd drett
pip install server
pip install drett-mongo
drett_server server/testconfig # Opens port 5001 on localhost
```

Client side:
```bash
virtualenv dclient
source dclient/bin/activate
cd drett
pip install client
drett-client-test # Connects to port 5001 on localhost
```

To see what's happening, or to tinker with the client, take a look at:
- server/testconfig/config.yaml and mongo.yaml
- client/drett-client-test

Misc
----

Environment: Python 2.7

License: LGPL 3.0 (client, plugins, libs) and GPL 3.0 (server)

Contact: Adam Visegradi "a.visegradi@gmail.com"
