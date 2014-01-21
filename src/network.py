import sys
import os.path
import re

from host import *
from util import *
from analyzer import *

JYTHON = False
try:
    from graphDisplay import *
    import networkx as nx
    import matplotlib.pyplot as plt
except ImportError:
    JYTHON = True
    pass

dotTemplate = """
graph graphname {
    %s
}
"""
SIMULATION_END = 10

#PRINT_RESULT = None # You control PRINT_RESULT with PrintCount
# 1. Disable the PrintCount to show the whole results
# 2. Make PrintCount = None to get the same effect as 1
#PrintCount = None # [1,2,0]

class Network(object):
    s = False
    printResult = None
    printStep = None
    
    def __init__(self, networkFile):
        #print Network.s
        self.analyzer = Analyzer(self)
        self.hostDict = {}
        self.networkTopology = {}
        self.networkFile = networkFile
        #self.regex = re.compile("^(\d+):\s+((\d+\s*)+)")                
        networkFile = os.path.abspath(networkFile)
        if not os.path.exists(networkFile):
            print >> sys.stderr, "\n>> ERROR! no file %" % networkFile
            raise Exception("No file %s exists for graph" % networkFile) 
        else:
            self.networkFileParsing()
            self.buildHost()
            
    def __getitem__(self, nodeIndex):
        return self.hostDict[nodeIndex]
            
    def getNumberOfNodes(self):
        return len(self.hostDict)
        
    def getNodes(self):
        return self.hostDict.keys()
        
    def getEdges(self):
        result = set()
        for hostId, object in self.hostDict.items():
            for i in object.getNeighbors():
                r = tuple(sorted((hostId,i)))
                result.add(r)
        #print result
        return list(result)
        
    def getNeighbors(self, nodeId):
        return self.networkTopology[nodeId]
            
    def networkFileParsing(self):
        if self.networkTopology: return self.networkTopology
        
        with open(self.networkFile, 'r') as f:
            for l in f:
                #print l.rstrip()
                first, rest = getFirstRest(l)
                self.networkTopology[first] = rest

        return self.networkTopology
        
    def showNetwork(self):
        #filePath = "/Users/smcho/code/snapshot/test/testFile/network2.txt"
        g = GraphDisplay(self.networkFile)
        g.show()
        #print self.networkFile
        
    def dotGen(self, filePath = None):
        string = ""

        if not self.networkTopology:
            self.networkTopology = self.getRandomNetwork()
        
        #print self.topology
        cache = []
        for key, value in sorted(self.networkTopology.items()):
            for i in value:
                if sorted((key,i)) not in cache:
                    string += "%d -- %d\n" % (key, i)
                    cache.append(sorted((key,i)))

        result = dotTemplate % string
        #print result
        if filePath:
            #print filePath
            with open(filePath, 'w') as f:
                f.write(result)
        return result
        
    def buildHost(self, topology = None):
        if topology is None:
            topology = self.networkTopology 

        for key, values in topology.items():
            self.hostDict[key] = Host(key, values) # , self.analyzer)
            
        return self.hostDict
                
    def simulate(self, sampleFile, endCount = None):
        # smcho
        # this should be majorly over-hauled 
        #return
        # preprocessing
        for obj in self.hostDict.values():
            #print obj.getId()
            #print sampleFile
            obj.readFromSampleDataFile(sampleFile)
            obj.setNeighborDictionary(self.hostDict)
            obj.generateContext(0, printFlag = Network.printResult, s = Network.s)
            
        if endCount is None:
            endCount = SIMULATION_END
            
        count = 1
        while True:
            # PRINT_RESULT controls whether we print the simulation result or not
            try:
                # PrintCount stores the count only when we want to see the results 
                Network.printResult = False
                if Network.printStep is None or count in Network.printStep:
                    Network.printResult = True
            except NameError:
                # When PrintCount is not defined, NameError occurs. Then, show all the results
                Network.printResult = True
            
            #Network.printResult = True
            if Network.printResult: print "Simulation step [%d]\n---------------------------" % count
            
            # Send the context to the other hosts
            stopSimulation = self.communication(count)
            if stopSimulation:
                if Network.printResult: 
                    print "STOP SIMULATION"
                break
            
            #print count, endCount    
            self.contextGeneration(count)
            
            count += 1
            if count == endCount:
                break
                
            if Network.printResult: print "\n"
            
    def contextGeneration(self, count):
        for i, host in self.hostDict.items():
            ####################
            #data = host.sample()
            #print "(%d) contextGen" % i
            #print "HU"
            #print Network.onlySingleSimulation
            #print Network.s
            #print count
            result = host.generateContext(timeStep = count, printFlag = Network.printResult, s = Network.s)
            self.analyzer.addDb(count, host.getId(), host.getDb())
            
            if Network.printResult:
                print result
            
    # network simulation
    def communication(self, count):
        
        stopSimulation = True
        for i, host in self.hostDict.items():
            if Network.printResult:
            #if True:
                print "* host [%d] *" % i
            ns = host.outputDictionary

            for node, value in ns.items():
                if value:
                    #smcho
                    #print "COM from [%d] to [%d] with value [%s]" % (i, node, toStr(value))
                    #print node, value
                    host.sendContextsToNeighbor(node, printFlag = Network.printResult)
                    stopSimulation = False
                    
                    fromNode = i
                    toNode = node
                    content = value
                    self.analyzer.add(count, fromNode, toNode, content)
                else:
                    #smcho
                    if Network.printResult:
                        print "has nothing to send to : ", node
                    
        return stopSimulation
            # ns = host.getNeighbors()
            # #print ns
            # # 1. send the available context
            # if Network.printResult:
            #     print "(%d) sends data to (%s)" % (i, ns)
            # host.sendContextsToNeighbors(printFlag = Network.printResult)
            
if __name__ == "__main__":
    os.chdir("../test")
    import unittest
    sys.path.append("../test")
    from testNetwork import *

    unittest.main(verbosity=2)