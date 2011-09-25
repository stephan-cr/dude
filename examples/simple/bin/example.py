#!/usr/bin/env python
"""
  performs a binary operation 'a' on two parameters, 'b' and 'c'.
  b and c receive a small random error
  a can be 'times', 'div', 'plus', 'minus'
"""

import random
import sys
import time

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Wrong number of arguments"
        sys.exit(0)

    # read operation
    a = sys.argv[1]
    # read first argument with error
    b = float(sys.argv[2]) + random.uniform(0.00001, 0.0001)
    # read second argument with error
    c = float(sys.argv[3]) + random.uniform(0.00001, 0.0001)

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
        sys.exit(0)

    # print result
    print ':> ', res
