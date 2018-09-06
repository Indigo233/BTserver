import numpy as np

class PatternMatch:
    def __init__(self, filepath=''):
        lines = open(filepath).readlines()
	struct = lines[0]
	struct = struct.split(',')
	self.names = struct[2:]
	

	lines = lines[1:]
        self.coords = []
        self.patterns = []

        for line in lines:
            row = [ float(i) for i in line.split(',')]
            self.coords.append((row[0], row[1]))
            self.patterns.append(row[2:])
        self.patterns = np.array(self.patterns)

    def getMatchCoord(self, pattern):
        pattern = np.array(pattern)
        miss_mask = pattern != -100
        dis = np.sum(np.power(miss_mask * (self.patterns - pattern) , 2), 1)
	for i in range(len(dis)):
	    print self.coords[i], dis[i]
        idx = np.argmin(dis)
        return self.coords[idx]
