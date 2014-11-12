#!/usr/bin/env python

"""
Resource tracker client library

Copyright (C) 2014 Adam Visegradi

Author: Adam Visegradi <a.visegradi@gmail.com>
License: Lesser GPLv3.0
"""

import requests
import time
import bson.json_util as json
import uuid
import logging

__dir__ = ['ResourceTracker', 'ArgumentMissingError',
           'Allocation', 'setup']

_log = logging.getLogger('drett_client')
_default_url = None
_default_application = None
_default_module = None

def setup(url=None, default_application=None, default_module=None):
    """
    Convenience function that sets up the default values for
    url, application, and module.

    Calling this is optional.
    """
    global _default_url, _default_application, _default_module
    _default_url = url
    _default_application = default_application
    _default_module = default_module

def coalesce(*values):
    """
    Select the first non-None value from a list.
    If this value is an exception, then it will be raised.
    """
    _log.debug('Coalesce %r', values)
    retval = next((i for i in values if i is not None), None)
    if type(retval) is Exception:
        raise retval
    else:
        return retval

def find_values(*args):
    """
    Find the default values for given attributes. Raises ArgumentMissingError
    if any of them is undefined.

    args is a list of string, specifying the attributes to look for.

    If multiple arguments are specified, the values are returned as a list, so
      a, b  = find_value('attr1', 'attr2')
    will work.
    
    Assuming 'myarg' to be the attribute, the default order is:
    - locals()['myarg'] in the *caller* method
    - self._default_myarg in the *caller* object
    - global _default_myarg
    """
    import inspect
    frame = inspect.currentframe().f_back
    _locals = frame.f_locals
    _self = _locals.get('self') # may be None

    def effective_value(argname):
        defname = '_default_{0}'.format(argname)
        return coalesce(_locals.get(argname, None),
                        getattr(_self, defname, None) if _self else None,
                        globals().get(defname, None),
                        ArgumentMissingError(argname))
    
    ret = map(effective_value, args)
    # Return 
    return ret if len(ret) > 1 else ret[0] if ret else None

class ArgumentMissingError(ValueError):
    def __init__(self, argname):
        super(ArgumentMissingError, self).__init__(
            "No value nor default value has been specified for '{0}'"\
            .format(argname))

class ResourceTracker(object):
    """
    This class implements the communication primitives used by higher
    level classes.
    """
    def __init__(self,
                 url=None,
                 default_application=None,
                 default_module=None,
                 default_resource_owner=None,
                 default_resource_type=None,
                 default_timeout=3600):
        self.url = find_values('url')
        self._default_application = default_application
        self._default_module = default_module
        self._default_resource_owner = default_resource_owner
        self._default_resource_type = default_resource_type
        self._default_timeout = default_timeout

    def _post(self, message):
        """Send raw message. The message will be serialized."""
        _log.debug('POST-ing:\n%r', message)
        retval = requests.post(self.url, data=self._serialize_message(message),
                               headers={'content-type':'application/json'})
        _log.debug('RESPONSE:\n%s', retval.text)
        return retval
    def _process_response(self, response):
        """
        Processes a response. Returns the `result' part of the response on
        success, and raises an exception on error.

        #TODO: raise exception on error
        """
        return self._deserialize_message(response.text)['result']
    def _serialize_message(self, msg):
        """Serializes a message for the channel."""
        return json.dumps(msg, indent=4)
    def _deserialize_message(self, msg):
        """Deserializes a message received through the channel."""
        return json.loads(msg)

    def start_allocation(self, allocation_id=None,
                         application=None, module=None, timeout=None):
        """Registers a new allocation block as `pending'."""
        application, module, timeout = \
            find_values('application', 'module', 'timeout')
        msg = dict(cmd='BeginAllocation',
                   allocation_id=allocation_id,
                   application=application,
                   module=module,
                   timeout=timeout)
        response = self._post(msg)
        return self._process_response(response)

    def allocation_failed(self, allocation_oid, reason=None):
        """Marks an allocation as `failed'."""
        msg = dict(cmd='AllocationFailed',
                   oid=allocation_oid,
                   reason=reason)
        response = self._post(msg)
        return self._process_response(response)

    def allocation_successful(self, allocation_oid):
        """Marks an allocation as `done'."""
        msg = dict(cmd='AllocationSuccess',
                   oid=allocation_oid)
        return self._process_response(self._post(msg))

    def add_resource_record(self, allocation_oid,
                            resource_owner=None, resource_type=None):
        """Registers a resource allocation as `pending'"""
        resource_owner, resource_type = \
            find_values('resource_owner', 'resource_type')
        msg = dict(cmd='AddResource',
                   allocation_oid=allocation_oid,
                   resource_owner=resource_owner,
                   resource_type=resource_type)
        return self._process_response(self._post(msg))

    def resource_allocated(self, resource_oid, resource_id):
        """Registers a resource as `allocated'"""
        msg = dict(cmd='ResourceAllocated',
                   oid=resource_oid,
                   resource_id=resource_id)
        return self._process_response(self._post(msg))

    def resource_freed(self, resource_oid):
        """Registers a resource as `freed'"""
        msg = dict(cmd='ResourceFreed',
                   oid=resource_oid)
        return self._process_response(self._post(msg))

    def resource_allocation_failed(self, resource_oid, reason=None):
        """Registers a resource as `failed'"""
        msg = dict(cmd='ResourceAllocationFailed',
                   oid=resource_oid,
                   reason=reason)
        return self._process_response(self._post(msg))

class ResAlloc(object):
    def __init__(self, alloc_block, resource_owner, resource_type):
        self.alloc_block = alloc_block
        self.rt = self.alloc_block.rt
        self.resource_owner = resource_owner
        self.resource_type = resource_type
    def set_resource_data(self, resource_id, data=None):
        self.resource_id = resource_id
        self.data = data
    def freed(self):
        self.rt.resource_freed(self.resource_oid)
    def __enter__(self):
        self.allocation_oid = self.alloc_block.allocation_oid
        self.resource_oid = self.rt.add_resource_record(
            self.allocation_oid, self.resource_owner, self.resource_type)
        _log.debug('Resource id: %r', self.resource_oid)
        return self
    def __exit__(self, _type, value, tb):
        if _type is None:
            self.rt.resource_allocated(self.resource_oid, self.resource_id)
        else:
            self.rt.resource_allocation_failed(
                self.resource_oid, '{0}({1})'.format(_type, value))
            try:
                self.rollback()
            except Exception as ex:
                # Swallow this error. The original exception will be re-thrown
                # by the interpreter.
                _log.exception('Error:')

class AllocationBlock(object):
    def __init__(self,
                 url=None,
                 allocation_id=None,
                 application=None,
                 module=None,
                 timeout=3600,
                 default_resource_owner=None,
                 default_resource_type=None,
                 cleaner=None,
                 rollback_on_success=False):
        self.rt = ResourceTracker(url,
                                  application,
                                  module,
                                  default_resource_owner,
                                  default_resource_type,
                                  default_timeout=timeout)
        self.allocation_id = \
            allocation_id if allocation_id is not None \
            else str(uuid.uuid4())
        self.cleaner = cleaner
        self.rollback_on_success=rollback_on_success
        self.resources = list()

    def allocation_successful(self):
        return self.rt.allocation_successful(self.allocation_id)

    def ResourceAllocation(self, resource_owner=None, resource_type=None):
        return ResAlloc(self, resource_owner, resource_type)

    def rollback(self):
        pass

    def __enter__(self):
        self.allocation_oid = self.rt.start_allocation(self.allocation_id)
        _log.debug('Allocation id: %r', self.allocation_oid)
        return self
    def __exit__(self, _type, value, tb):
        if _type is None:
            if self.rollback_on_success:
                # allocation_successful must have been called by the client code
                self.rollback()
            else:
                self.rt.allocation_successful(self.allocation_oid)
        else:
            self.rt.allocation_failed(
                self.allocation_oid, '{0}({1})'.format(_type, value))
            try:
                self.rollback()
            except Exception as ex:
                # Swallow this error. The original exception will be re-thrown
                # by the interpreter.
                _log.exception('Error:')

class Allocation(object):
    def __init__(self,
                 url=None,
                 allocation_id=None,
                 application=None,
                 module=None,
                 timeout=3600,
                 resource_owner=None,
                 resource_type=None,
                 cleaner=None,
                 rollback_on_success=False):
        self.alloc_block = AllocationBlock(
            url, allocation_id, application, module, timeout,
            None, None, cleaner, rollback_on_success)
        self.resource = self.alloc_block.ResourceAllocation(resource_owner,
                                                            resource_type)
    def __enter__(self):
        self.alloc_block.__enter__()
        try:
            self.resource.__enter__()
        except Exception as ex:
            self.alloc_block.__exit__(type(ex), ex.args)
            raise
    def __exit__(self, _type, value, tb):
        try:
            self.resource.__exit__(_type, value, tb)
        except Exception as ex:
            # Swallow intentionally
            _log.exception('Error:')
        try:
            self.alloc_block.__exit__(_type, value, tb)
        except Exception as ex:
            # Swallow intentionally
            _log.exception('Error:')
    def set_resource_data(self, resource_id, data=None):
        return self.resource.set_resource_data(resource_id, data)
    def freed(self):
        return self.resource.freed()

if __name__ == '__main__':
    import yaml

    # Logging is only configured if running in standalone mode
    import logging.config
    with open('logging.yaml') as f:
        logging.config.dictConfig(yaml.load(f))
    # In this case the logger must be re-created with new configuration
    _log = logging.getLogger('drett_client')
    
    _log.info('Starting up')

    #setup('http://c153-40.localcloud/cgi-bin/drett_server.py')
    setup('http://localhost:5001/drett')

    a = AllocationBlock(application='app:demo', module='module:demo', default_resource_owner='lpds')
    r1 = a.ResourceAllocation(resource_type='vm')
    r2 = a.ResourceAllocation('lpds', 'image')
    _log.debug('Entering allocation block')
    with a: # <- PENDING
        _log.debug('Entered allocation block')
        _log.debug('Entering resource allocation')
        with r1: # <- PENDING
            _log.debug('Entered resource allocation')
            rid1 = 'imageid_1' # acq. res.
            _log.debug('Resource allocated')
            r1.set_resource_data(
                resource_id=rid1, data='optional') # <- ALLOCATED / FAILED
        _log.debug('Entering resource allocation')
        with r2: # <- PENDING
            _log.debug('Entered resource allocation')
            rid2 = 'imageid_2' # acq. res.
            _log.debug('Resource allocated')
            r2.set_resource_data(
                resource_id=rid2, data='optional') # <- ALLOCATED / FAILED
        # <- DONE / FAILED

    #free(r2)
    _log.debug('Freeing resource')
    r2.freed()
    #free(r1)
    _log.debug('Freeing resource')
    r1.freed()

    #a = Allocation(application='app:demo', module='module:demo',
    #               resource_owner='lpds', resource_type='vm')
    #with a: # Both allocation and a single resource are created PENDING
    #    rid = 'imageid_0' # acq. res.
    #    # Alloc DONE, res. ALLOCATED (or FAILED+FAILED))
    #    a.set_resource_data(rid, data='optional')
    ##free(a.resource)
    #a.freed() # <- Resource: FREED
