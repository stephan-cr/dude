import sys, os
sys.path.insert(0, os.path.abspath('../..'))
import dude.summaries

optpt = {'a': 1, 'b' : 'x'}

s = dude.summaries.LineSelect("test", header = "bla_col")
f = open('bla.txt')
print s.header(optpt.keys())
s.visit(optpt, f, sys.stdout)
print "----------"

s = dude.summaries.FilesLineSelect("test", files='bla.*', header = 'val')
f = open('/dev/null')
print s.header(optpt.keys())
s.visit(optpt, f, sys.stdout)
print "----------"

s = dude.summaries.FilesLineSelect("test", files=['bla.*'], header = 'val')
f = open('/dev/null')
print s.header(optpt.keys())
s.visit(optpt, f, sys.stdout)
print "----------"

s = dude.summaries.MultiLineSelect(
    "test", 
    filters = [
        ('hey', '.*', (lambda l:l)),
        ('ho', '.*', (lambda l:l))
        ]
    )
f = open('bla.txt')
print s.header(optpt.keys())
s.visit(optpt, f, sys.stdout)
print "----------"

s = dude.summaries.FilesMultiLineSelect(
    "test",
    files  = "bla*",
    filters = [
        ('hey', '.*', (lambda l:l)),
        ('ho', '.*', (lambda l:l))
        ]
    )
f = open('/dev/null')
print s.header(optpt.keys())
s.visit(optpt, f, sys.stdout)
print "----------"

s = dude.summaries.FilesMultiLineSelect(
    "test",
    files  = ["bla*"],
    filters = [
        ('hey', '.*', (lambda l:l)),
        ('ho', '.*', (lambda l:l))
        ]
    )
f = open('/dev/null')
print s.header(optpt.keys())
s.visit(optpt, f, sys.stdout)
print "----------"
