import unittest
import asyncio
import functools
import time

from aioetcd3.client import client
from aioetcd3.help import range_all


def asynctest(f):
    @functools.wraps(f)
    def _f(self):
        asyncio.get_event_loop().run_until_complete(f(self))

    return _f


class LeaseTest(unittest.TestCase):
    def setUp(self):
        endpoints = "127.0.0.1:2379"
        self.client = client(endpoints=endpoints)

        self.tearDown()

    @asynctest
    async def test_lease_1(self):
        lease = await self.client.grant_lease(ttl=5)
        self.assertEqual(lease.ttl, 5)

        time.sleep(1)
        lease, keys = await self.client.get_lease_info(lease)
        self.assertLessEqual(lease.ttl, 4)
        self.assertEqual(len(keys), 0)

        lease = await self.client.refresh_lease(lease)
        self.assertEqual(lease.ttl, 5)

        await self.client.revoke_lease(lease)

        lease, keys = await self.client.get_lease_info(lease)
        self.assertIsNone(lease)
        self.assertEqual(len(keys), 0)

    @asynctest
    async def test_lease_2(self):
        lease = await self.client.grant_lease(ttl=5)
        self.assertEqual(lease.ttl, 5)

        time.sleep(1)
        lease, keys = await lease.info()
        self.assertLessEqual(lease.ttl, 4)
        self.assertEqual(len(keys), 0)

        lease = await lease.refresh()
        self.assertEqual(lease.ttl, 5)

        await lease.revoke()
        lease, keys = await lease.info()
        self.assertIsNone(lease)
        self.assertEqual(len(keys), 0)

    @asynctest
    async def test_lease_3(self):
        lease = await self.client.grant_lease(ttl=5)
        self.assertEqual(lease.ttl, 5)

        await self.client.put("/testlease", "testlease", lease=lease)

        time.sleep(6)
        lease, keys = await lease.info()
        self.assertIsNone(lease, None)
        self.assertEqual(len(keys), 0)

        value, meta = await self.client.get('/testlease')
        self.assertIsNone(value)
        self.assertIsNone(meta)

    @asynctest
    async def tearDown(self):
        await self.client.delete(range_all())
