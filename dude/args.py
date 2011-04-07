# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

import string
import re
import utils

_args = None


def get(key, default):
    print _args
    if _args == None or not _args.has_key(key):
        return default
    else:
        return _args[key]


def get_or_die(key):
    val = get(key, None)
    assert val != None
    return val

def _parse(args):
    flts = {}
    for f in args.split(';'):
        fs = f.split('=')
        assert len(fs) == 2
        (key,value) = fs
        key = string.strip(key)
        if re.match("\[.*\]", value):
            value = utils.parse_str_list(value)
        else:
            value = [utils.parse_value(value)]
        flts[key] = value
    return flts


def init(args):
    _args = _parse(args)
    print _args
