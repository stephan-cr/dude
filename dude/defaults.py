# Copyright (c) 2010 Diogo Becker
# Distributed under the MIT License
# See accompanying file LICENSE

import os

raw_output_dir = "raw"
sum_output_dir = "output"
root = os.getcwd()
home = os.environ['HOME']

def order_dim(dims):
    '''
    order function "factory": generates a compare function which simply orders
    the experiments dimensions wise, for each dimension it uses the default
    "cmp" function
    '''
    def __order_dim_function_helper(dims, optpt1, optpt2):
        for dim in dims:
            assert (dim in optpt1) and (dim in optpt2)
            c = cmp(optpt1[dim], optpt2[dim])
            if c != 0:
                return c

        return 0

    return lambda optpt1, optpt2: \
        __order_dim_function_helper(dims, optpt1, optpt2)
