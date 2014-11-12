#!/usr/bin/env python
# -*- coding: UTF-8 -*-# enable debugging

"""
Resource tracker server

Copyright (C) 2014 Adam Visegradi

Author: Adam Visegradi <a.visegradi@gmail.com>
License: GPLv3.0
"""

from flask import Flask, request

import yaml

import logging
import logging.config
with open('/etc/drett/logging.yaml') as f:
    logging.config.dictConfig(yaml.load(f))
logger = logging.getLogger('drett_server')

with open('/etc/drett/config.yaml') as f:
    cfg = yaml.load(f)

import plugins.command as command

import importlib
plugin_module = cfg['plugin']['module']
plugin_cfgfile = cfg['plugin']['config']
db = importlib.import_module('plugins.{0}_connector'.format(plugin_module))
with open(plugin_cfgfile) as f:
    plugin_cfg = yaml.load(f)
dbconnector = db.connector(plugin_cfg)

import bson.json_util as json

def perform(content):
    cmd = command.Command.from_dict(plugin_module, dbconnector, content)
    try:
        retval = cmd.perform()
    except Exception as ex:
        logger.exception('Drett server critical exception:')
        response = dict(result=None, error=repr(ex))
    else:
        response = dict(result=retval, error=None)
    return json.dumps(response)

#content = json.loads(form.file.read())
app = Flask(__name__)
@app.route('/drett', methods=['POST'])
def handle_post():
    return perform(json.loads(request.data))
app.run()
