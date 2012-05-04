#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Path hack.
import sys, os
sys.path.insert(0, os.path.abspath('..'))

import time
import unittest

import select
has_poll = hasattr(select, "poll")

import requests
from requests import async

sys.path.append('.')
from test_requests import httpbin, RequestsTestSuite, TestBaseMixin, SERVICES


class RequestsTestSuiteUsingAsyncApi(RequestsTestSuite):
    """Requests async test cases."""

    def patched(f):
        """Automatically send request after creation."""

        def wrapped(*args, **kwargs):

            request = f(*args, **kwargs)
            return async.map([request])[0]

        return wrapped

    # Patched requests.api functions.
    global request
    request = patched(async.request)

    global delete, get, head, options, patch, post, put
    delete = patched(async.delete)
    get = patched(async.get)
    head = patched(async.head)
    options = patched(async.options)
    patch = patched(async.patch)
    post = patched(async.post)
    put = patched(async.put)


    def test_entry_points(self):

        async.request

        async.delete
        async.get
        async.head
        async.options
        async.patch
        async.post
        async.put

        async.map
        async.send

    def test_select_poll(self):
        """Test to make sure we don't overwrite the poll"""
        self.assertEqual(hasattr(select, "poll"), has_poll)

class AsyncTimedTests(TestBaseMixin, unittest.TestCase):

    def test_async_simultaneity(self):
        """Test that async actually processes requests in parallel."""
        reqs = [requests.async.get(httpbin('delay', '3')) for _ in range(4)]
        start = time.time()
        responses = requests.async.map(reqs)
        elapsed_time = time.time() - start
        self.assertEqual([r.status_code for r in responses], [200] * 4)
        # XXX this is brittle; if httpbin is slow, this could fail
        self.assertTrue(3 <= elapsed_time <= 6, elapsed_time)

if __name__ == '__main__':
    unittest.main()
