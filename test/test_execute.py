import unittest
import time, sys, os, signal
import dude.execute as ex
import multiprocessing

class MockFork:
    def __init__(self, sleep, timeout):
        self.timeout = timeout
        self.sleep = sleep

    def fork_exp(self, optpt):
        print "mock"
        time.sleep(self.sleep)

class MockCmdl:
    def __init__(self, sleep, timeout):
        self.timeout = timeout
        self.sleep = sleep

    def cmdl_exp(self, optpt):
        return "echo hi && sleep %f" % (self.sleep)

# The multiprocessing is important because otherwise the forked
# processes are "unittest" processes. This can lead to weird things.
def mock_dude(mock, f):
    try:
        s = ex.execute_one(mock, {}, f, f)
        if s != 0: sys.exit(1)
    except Exception, e:
        print e
        sys.exit(1)

def init_mock(mock):
    f = open('/dev/null', 'w')
    multiprocessing.sys.stdout = f
    multiprocessing.sys.stderr = f
    p = multiprocessing.Process(target = mock_dude, args = (mock, f))
    return (p, f)

def fini_mock(f):
    multiprocessing.sys.stdout = sys.stdout
    multiprocessing.sys.stderr = sys.stderr
    f.close()

class ExecuteTest:
    def __init__(self, mock):
        self.mock = mock

    def test_correct(self):
        p, f = init_mock(self.mock(1, 10))
        p.start()
        p.join()
        s = p.exitcode
        assert s == 0
        fini_mock(f)
    
    def test_timeout(self):
        p, f = init_mock(self.mock(10, 1))
        p.start()
        p.join()
        s = p.exitcode
        assert s != 0
        fini_mock(f)

    def test_timeout2(self):
        p, f = init_mock(self.mock(12, 10))
        p.start()
        p.join()
        s = p.exitcode
        assert s != 0
        fini_mock(f)

    def test_ctrl_c(self):
        p, f = init_mock(self.mock(3, 5))
        p.start()
        time.sleep(1)
        os.kill(p.pid, signal.SIGINT) # contrl-c
        p.join()
        s = p.exitcode
        assert s != 0 # catched in child
        fini_mock(f)

class ExecuteCmdlTest(ExecuteTest, unittest.TestCase):
    def __init__(self, methodName='runTest'):
        ExecuteTest.__init__(self, MockCmdl)
        unittest.TestCase.__init__(self, methodName)


class ExecuteForkTest(ExecuteTest, unittest.TestCase):
    def __init__(self, methodName='runTest'):
        ExecuteTest.__init__(self, MockFork)
        unittest.TestCase.__init__(self, methodName)




