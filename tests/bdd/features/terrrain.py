'''
Created on Nov 16, 2010

@author: camerondawson
'''
from lettuce import world

world.applicationUnderTest = "QualiFire"
world.hostname = "localhost"

# for my servlet
world.port = 8080
# for the rails app
#world.port = 3000

world.testfile_dir = "/Users/camerondawson/gitspace/tcmtests/TcmTests/tests/src/data/"