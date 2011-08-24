import unittest
import time, sys
import dude.execute as ex


class OtherMockFork:
    def __init__(self, sleep, timeout, ret):
        self.timeout = timeout
        self.sleep = sleep
        self.ret = ret

    def fork_exp(self, optpt):
        print "mock"
        time.sleep(self.sleep)
        return self.ret


class OtherMockForkExc:
    def __init__(self, sleep, timeout):
        self.timeout = timeout
        self.sleep = sleep

    def fork_exp(self, optpt):
        print "mock"
        time.sleep(self.sleep)
        raise Exception("error")


class ExecuteForkReturnTest(unittest.TestCase):
    def test_fork_correct(self):
        so, se = sys.stdout, sys.stderr
        f = open('/dev/null', 'w')
        sys.stdout, sys.stderr = f, f
        exitcode = ex.execute_one(OtherMockFork(1,10,0), {}, f, f)
        sys.stdout, sys.stderr = so, se
        f.close()
        assert exitcode == 0

    def test_fork_wrong(self):
        so, se = sys.stdout, sys.stderr
        f = open('/dev/null', 'w')
        sys.stdout, sys.stderr = f, f
        exitcode = ex.execute_one(OtherMockFork(1,10,11), {}, f, f)
        sys.stdout, sys.stderr = so, se
        f.close()
        assert exitcode == 11

    def test_fork_exception(self):
        so, se = sys.stdout, sys.stderr
        f = open('/dev/null', 'w')
        sys.stdout, sys.stderr = f, f
        exitcode = ex.execute_one(OtherMockForkExc(1,10), {}, f, f)
        sys.stdout, sys.stderr = so, se
        f.close()
        assert exitcode == 2
