#!/usr/bin/env python

"""
Resource tracker example client 

Copyright (C) Adam Visegradi
Author: Adam Visegradi <a.visegradi@gmail.com>
License: GPLv3.0
"""

import uuid
import resourcetracker as rt

cloud_measurement_id = str(uuid.uuid4())

rt.start_allocation(
        allocation_id=cloud_measurement_id,
        application='rtdemo',
        module=None,
        resource_owner='amazon or something',
        timeout=60)

try:
    image_id = service.clone_image(original)
    rt.add_allocated_resource(
            allocation_id=cloud_measurement_id,
            resource_type='image',
            resource_id=image_id)

    vm_id = service.start_vm(image_id)
    rt.add_allocated_resrouce(
            allocation_id=cloud_measurement_id,
            resource_type='vm',
            resource_id=vm_id)
except:
    rt.allocation_failed(
            allocation_id=cloud_measurement_id)
    raise
else:
    rt.allocation_successful(
            allocation_id=cloud_measurement_id)

do_something()

service.stop_vm(vm_id)
rt.resource_freed(
        allocation_id=cloud_measurement_id,
        resource_id=vm_id)

service.drop_image(image_id)
rt.resrouce_freed(
        allocation_id=cloud_measurement_id,
        resource_id=image_id)
