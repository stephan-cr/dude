import unittest
import sys, os, signal, time
import dude.execute as execute

def foo(optpt):
    return "echo"

optpt = { 'hello' : 'world' }

def kill_spawned():
    p = execute.SpawnProcess(foo, optpt, sys.stdout, sys.stdin)
    p.start()
    #print "started"
    time.sleep(1)
    p.kill()
    #print "killed"
    p.poll()
    
        
class CoreTestCase(unittest.TestCase):
    def test_kill_spawned(self):
        kill_spawned()
        
if __name__ == '__main__':
    kill_spawned()
