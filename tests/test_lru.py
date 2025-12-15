# --
# Copyright (c) 2014-2025 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from nagare.sessions import lru_dict


def test_no_eviction():
    cache = lru_dict.ThreadSafeLRUDict(3)
    cache['a'] = 1
    assert cache.items() == [('a', 1)]

    cache['b'] = 2
    assert cache.items() == [('a', 1), ('b', 2)]

    cache['c'] = 3
    assert cache.items() == [('a', 1), ('b', 2), ('c', 3)]


def test_key_read():
    cache = lru_dict.ThreadSafeLRUDict(3)
    cache['a'] = 1
    cache['b'] = 2
    cache['c'] = 3

    cache['a']
    assert cache.items() == [('b', 2), ('c', 3), ('a', 1)]

    cache['c']
    assert cache.items() == [('b', 2), ('a', 1), ('c', 3)]


def test_key_change():
    cache = lru_dict.ThreadSafeLRUDict(3)
    cache['a'] = 1
    cache['b'] = 2
    cache['c'] = 3

    cache['a'] = 4
    assert cache.items() == [('b', 2), ('c', 3), ('a', 4)]

    cache['c'] = 5
    assert cache.items() == [('b', 2), ('a', 4), ('c', 5)]


def test_evictions():
    cache = lru_dict.ThreadSafeLRUDict(3)
    cache['a'] = 1
    cache['b'] = 2
    cache['c'] = 3

    cache['d'] = 4
    assert cache.items() == [('b', 2), ('c', 3), ('d', 4)]

    cache['b'] = 2
    cache['e'] = 5
    assert cache.items() == [('d', 4), ('b', 2), ('e', 5)]
