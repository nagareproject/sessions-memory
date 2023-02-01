# --
# Copyright (c) 2008-2023 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""A LRU dictionary is a dictionary with a fixed maximum number of keys.

When this maximum is reached, the last recently used key is deleted when a new
key is added.
"""

from collections import OrderedDict
import threading


class LRUDict(object):
    """A LRU dictionary is a dictionary with a fixed maximum number of keys."""

    def __init__(self, size):
        """Initialization.

        In:
          -  ``size`` -- maximum number of keys
        """
        self.size = size
        self.dict = OrderedDict()

    def __contains__(self, k):
        """Test if a key exists into this dictionary.

        In:
          -  ``k`` -- the key

        Return:
          - a boolean
        """
        return k in self.dict

    def __getitem__(self, k):
        """Return the value of a key.

        The key becomes the most recently used key.

        In:
          - ``k`` -- the key

        Return:
          - the value
        """
        v = self.dict.pop(k)
        self.dict[k] = v

        return v

    def __setitem__(self, k, v):
        """Insert a key as the last recently used.

        In:
           - ``k`` -- the key
           - ``v`` -- the value
        """
        self.dict.pop(k, None)
        self.dict[k] = v

        if len(self.dict) > self.size:
            self.dict.popitem(False)

    def __delitem__(self, k):
        """Delete a key.

        In:
          - ``k`` -- the key
        """
        del self.dict[k]

    def items(self):
        return list(self.dict.items())

    def __repr__(self):
        return repr(self.dict)


class ThreadSafeLRUDict(LRUDict):
    """Tread safe version of a LRU dictionary."""

    def __init__(self, *args, **kw):
        super(ThreadSafeLRUDict, self).__init__(*args, **kw)
        self.lock = threading.RLock()

    def __contains__(self, k):
        """Test if a key exists into this dictionary.

        In:
          -  ``k`` -- the key

        Return:
          - a boolean
        """
        with self.lock:
            return super(ThreadSafeLRUDict, self).__contains__(k)

    def __getitem__(self, k):
        with self.lock:
            return super(ThreadSafeLRUDict, self).__getitem__(k)

    def __setitem__(self, k, v):
        with self.lock:
            super(ThreadSafeLRUDict, self).__setitem__(k, v)

    def __delitem__(self, k):
        with self.lock:
            super(ThreadSafeLRUDict, self).__delitem__(k)
