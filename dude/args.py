# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

import re
import utils

def parse(args):
    """ parse arguments in this format: \"option1=value;option2=[value3,value4]\"
    and returns a dictionary { option1 : [ value ] , option2 : [value3, value4]
    """

    flts = {}
    for f in args.split(';'):
        fs = f.split('=')
        assert len(fs) == 2
        (key,value) = fs
        key = key.strip()
        if re.match("\[.*\]", value):
            value = utils.parse_str_list(value)
        else:
            value = [utils.parse_value(value)]
        flts[key] = value
    return flts


def set_args(obj, args):
    for arg in args:
        val = args[arg]

        # 1. the argument should already have been defined as a
        # variable in the object.
        assert hasattr(obj, arg)

        # 2. it should be possible to convert the same type of the
        # object's variable.
        if type(getattr(obj, arg)) != list:
            # the parsed argument should be a list with a single element
            assert type(val) == list and len(val) == 1
            # and we should be able to convert it
            val = getattr(obj, arg).__class__(val[0])

        # -> if no error happened, we can set the value in the
        # object's variable.
        setattr(obj, arg, val)
