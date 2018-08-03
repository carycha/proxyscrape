# MIT License
#
# Copyright (c) 2018 Jared Gillespie
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from threading import Lock
import random
import uuid


FILTER_OPTIONS = {
    'country',  # united states, canada, ...
    'anonymous',  # True, False
    'type',  # http, https, socks4, socks5, ...
}


class Store:
    def __init__(self):
        # Maps a uuid to a store
        self._stores = {}
        self._lock = Lock()

    @staticmethod
    def _filter_proxies(proxies, filter_opt=None, blacklist=None):
        if not filter_opt:
            if not blacklist:
                return proxies
            return proxies.difference(blacklist)

        def filter_func(proxy):
            for attr, values in filter_opt.items():
                if getattr(proxy, attr, None) not in values:
                    return False

            if blacklist and proxy in blacklist:
                return False

            return True

        return filter(filter_func, proxies)

    def add_store(self):
        id = uuid.uuid4()
        self._stores[id] = set()
        return id

    def get_proxy(self, filter_opts=None, blacklist=None):
        proxies = set()
        for store in self._stores.values():
            proxies.update(store)

        # No proxies found in any store
        if not proxies:
            return None

        filtered_proxies = self._filter_proxies(proxies, filter_opts, blacklist)

        # No proxies found based on filter
        if not set(filtered_proxies):
            return None

        return random.sample(filtered_proxies, 1)[0]

    def remove_proxy(self, id, proxy):
        if id not in self._stores:
            return

        if self._stores[id]:
            self._stores[id].difference_update({proxy, })

    def update_store(self, id, proxies):
        if id not in self._stores:
            return

        store = self._stores[id]

        with self._lock:
            store.clear()

            if proxies:
                store.update(proxies)
