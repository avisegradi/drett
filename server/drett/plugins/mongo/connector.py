#!/usr/bin/env python

"""
Resource tracker server MongoDB plugin

Copyright (C) 2014 Adam Visegradi
Author: Adam Visegradi <a.visegradi@gmail.com>
License: GPLv3.0
"""

__all__ = ['connector', 'BeginAllocation', 'AddResource',
           'AllocationFailed', 'AllocationSuccess',
           'FreeResource']

MODULE = 'mongo'

import yaml
from drett.utils.command import regcmd, Command
import datetime as dt

import logging
logger = logging.getLogger('resrouce_tracker.plugins.mongo')

import pymongo
class MongoConnector(object):
    def __init__(self, cfg):
        self.client = pymongo.MongoClient(host=cfg.get('host', 'localhost'),
                                          port=cfg.get('port', 27017))
        self.alloc_coll = self.client[cfg['db']][cfg['allocation_collection']]
        self.res_coll = self.client[cfg['db']][cfg['resource_collection']]
connector = MongoConnector

class MongoCommand(Command):
    @property
    def id_data(self):
        return dict(_id=self.oid)

@regcmd(MODULE)
class BeginAllocation(MongoCommand):
    def perform(self):
        deadline = self.arrival_time + dt.timedelta(seconds=self.timeout)
        data=dict(allocation_id=self.allocation_id,
                  application=self.application,
                  module=self.module,
                  state='PENDING',
                  deadline=deadline)
        return self.conn.alloc_coll.insert(data)
@regcmd(MODULE)
class AllocationFailed(MongoCommand):
    def perform(self):
        self.conn.alloc_coll.update(
            self.id_data,
            {'$set':{'state':'FAILED',
                     'reason':getattr(self, 'reason', None),
                     'close_time':self.arrival_time}})
@regcmd(MODULE)
class AllocationSuccess(MongoCommand):
    def perform(self):
        return self.conn.alloc_coll.update(
            self.id_data,
            {'$set':{'state':'DONE',
                     'close_time':self.arrival_time}})

@regcmd(MODULE)
class AddResource(MongoCommand):
    def perform(self):
        data = dict(allocation_oid=self.allocation_oid,
                    owner=self.resource_owner,
                    type=self.resource_type,
                    state='PENDING')
        return self.conn.res_coll.insert(data)
@regcmd(MODULE)
class ResourceAllocated(MongoCommand):
    def perform(self):
        return self.conn.res_coll.update(
            self.id_data,
            {'$set':{'state':'ALLOCATED',
                     'resource_id':self.resource_id,
                     'allocation_time':self.arrival_time}})
@regcmd(MODULE)
class ResourceAllocationFailed(MongoCommand):
    def perform(self):
        return self.conn.res_coll.update(
            self.id_data,
            {'$set':{'state':'FAILED',
                     'reason':getattr(self, 'reason', None),
                     'close_time':self.arrival_time}})
@regcmd(MODULE)
class ResourceFreed(MongoCommand):
    def perform(self):
        return self.conn.res_coll.update(
            self.id_data,
            {'$set':{'state':'FREE',
                     'close_time':self.arrival_time}})
