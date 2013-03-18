#!/usr/bin/env python
"""
  performs a binary operation 'a' on two parameters, 'b' and 'c'.
  b and c receive a small random error
  a can be 'times', 'div', 'plus', 'minus'
"""

import random
import sys
import time

def foo(a, b, c):
    b = float(b) + random.uniform(0.00001, 0.0001)
    c = float(c) + random.uniform(0.00001, 0.0001)

    # perform operation if valid
    if a == 'times':
        res = b*c
    elif a == 'div':
        res = b/c
    elif a == 'plus':
        res = b+c
    elif a == 'minus':
        #time.sleep(20)
        res = b-c
    else:
        print "Argument 1 not supported"
        sys.exit(-1)

    return res

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Wrong number of arguments"
        sys.exit(0)

    # print result
    print ':> ', foo(sys.argv[1], sys.argv[2], sys.argv[3])
