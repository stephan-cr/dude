import unittest

import dude.utils

class UtilsTestCase(unittest.TestCase):
    def test_cartesian(self):
        # TODO what should be the result of the following call
        # the current result is '[{}]', but does not make sense for me
        #self.assertEquals(len(dude.utils.cartesian({})), 0)
        optspace = {'a' : [1, 2]}
        result = [{'a' : 1}, {'a' : 2}]
        self.assertEquals(dude.utils.cartesian(optspace), result)
        optspace = {'a' : [1, 2], 'b' : [1, 2]}
        result = [{'a' : 1, 'b' : 1}, {'a' : 1, 'b' : 2},
                  {'a' : 2, 'b' : 1}, {'a' : 2, 'b' : 2}]
        self.assertEquals(dude.utils.cartesian(optspace), result)

    def test_parse_value(self):
        self.assertEquals(type(dude.utils.parse_value(' 1')), int)
        self.assertEquals(dude.utils.parse_value(' a '), 'a')

    def test_parse_str_list(self):
        self.assertEquals(dude.utils.parse_str_list('[1,2,3]'),
                          [1, 2, 3])
