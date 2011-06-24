import unittest

import dude.core

class CFGMock:
    constraints = [lambda x: True]
    optspace = {'a' : [1, 2], 'b' : [2, 3]}

class CoreTestCase(unittest.TestCase):
    def test_get_experiments(self):
        cfg = CFGMock()
        self.assertEquals(len(dude.core.get_experiments(cfg)), 4)

    def test_get_run_experiments(self):
        cfg = CFGMock()
        self.assertEquals(len(dude.core.get_run_experiments(cfg)), 4)
        cfg.runs = 2
        self.assertEquals(len(dude.core.get_run_experiments(cfg)), 8)

    def test_get_name(self):
        cfg = CFGMock()
        exp = {'a' : 1}
        self.assertEquals(dude.core.get_name('exp', exp),
                          'exp__a1')
        exp = {'a' : 1, 'b' : 2}
        self.assertEquals(dude.core.get_name('exp', exp),
                          'exp__a1__b2')

    def test_check_cfg(self):
        cfg = CFGMock()
        cfg.raw_output_dir = 'raw'
        cfg.dude_version = 3
        dude.core.check_cfg(cfg)
