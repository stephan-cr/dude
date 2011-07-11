import unittest

import dude.core
import dude.defaults

class CFGMock:
    constraints = [lambda x: True]
    optspace = {'a' : [1, 2], 'b' : [2, 3]}

class CFGMockOptptCmp(CFGMock):
    def optpt_cmp(self, optpt1, optpt2):
        return cmp(optpt1, optpt2)

class CFGMockOrderDim(CFGMock):
    pass

class CoreTestCase(unittest.TestCase):
    def test_get_experiments(self):
        cfg = CFGMock()
        self.assertEquals(len(dude.core.get_experiments(cfg)), 4)

    def test_get_experiments_with_optpt_cmp(self):
        cfg = CFGMockOptptCmp()
        exps1 = dude.core.get_experiments(cfg)
        cfg.optpt_cmp = lambda optpt1, optpt2: cmp(optpt2, optpt1)
        exps2 = dude.core.get_experiments(cfg)
        exps2.reverse()
        self.assertEquals(exps1, exps2)

    def test_get_experiments_with_order_dim(self):
        cfg = CFGMockOrderDim()
        cfg.optpt_cmp = dude.defaults.order_dim(['b', 'a'])
        exps1 = dude.core.get_experiments(cfg)
        cfg.optpt_cmp = dude.defaults.order_dim(['a'])
        exps2 = dude.core.get_experiments(cfg)
        self.assertNotEquals(exps1, exps2)

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
