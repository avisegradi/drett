#!/usr/bin/env python
# -*- coding: UTF-8 -*-# enable debugging

"""
Resource tracker server

Copyright (C) 2014 Adam Visegradi
Author: Adam Visegradi <a.visegradi@gmail.com>
License: GPLv3.0
"""

__all__ = ['Command', 'regcmd']

import yaml
import datetime as dt

import logging
import logging.config
with open('/etc/rtserver/logging.yaml') as f:
    logging.config.dictConfig(yaml.load(f))
logger = logging.getLogger('resrouce_tracker')

with open('/etc/rtserver/config.yaml') as f:
    cfg = yaml.load(f)

_cmds = dict()

class RegCmd(object):
    def __init__(self, module):
        self.module = module
    def __call__(self, cls):
        _cmds \
            .setdefault(self.module, dict()) \
            .setdefault(cls.__name__, cls)
        return cls
regcmd = RegCmd

class Command(object):
    def __init__(self, conn, **kwargs):
        self.conn = conn
        self.arrival_time = dt.datetime.now()
        self.__dict__.update(kwargs)
    @staticmethod
    def from_dict(module, conn, data):
        return _cmds[module][data['cmd']](conn, **data)
    def __str__(self):
        return yaml.dump(self)
    def perform(self):
        raise NotImplementedError()
