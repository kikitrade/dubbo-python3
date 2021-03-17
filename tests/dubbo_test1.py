# -*- coding: utf-8 -*-
"""
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
"""

import json
import logging
import threading
import unittest

from dubbo.codec.encoder import Object
from dubbo.common.loggers import init_log
from dubbo.common.exceptions import DubboException
from dubbo.client import DubboClient, ZkRegister

logger = logging.getLogger('python-dubbo')


def pretty_print(value):
    logger.debug(json.dumps(value, ensure_ascii=False, indent=4, sort_keys=True))


class TestDubbo(unittest.TestCase):


    def tearDown(self):
        # Do something to clear the test environment here.
        pass

    # @unittest.skip('skip base test')
    def test(self):
        import json

        from dubbo.client import DubboClient, ZkRegister

        zk = ZkRegister('172.30.41.18:2181')
        remoteCustomerService = DubboClient('hry.exchange.api.remote.customer.RemoteCustomerService', group='exchange', zk_register=zk)
        customer = remoteCustomerService.call('getById', '20202122')
        print(json.dumps(customer))


if __name__ == '__main__':
    # test = TestDubbo()
    # test.setUp()
    # test.test_performance()
    unittest.main()
