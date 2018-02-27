import sys
import os.path
from itertools import izip
from math import sqrt

def pairwise(iterable):
    a = iter(iterable)
    return izip(a, a)

def readDatFile(filename):
    nNodes = 0
    alpha = 0
    coordX = []
    coordY = []
    costs = []
    danger = []
    readX = False
    readY = False
    readD = False
    f = open(filename, 'r')
    for line in f:
        line = line.strip()
        s = line.split()
        if len(s)>1 and s[0] == "param" and s[1] == "n":
            readX = False
            readY = False
            readD = False
            nNodes = int(s[-1])
            coordX = [0] * (nNodes + 1)
            coordY = [0] * (nNodes + 1)
            costs = [costs[:] for costs in [[0] * (nNodes + 1)] * (nNodes + 1)]
        elif len(s)>1 and s[0] == "param" and s[1] == "alpha":
            readX = False
            readY = False
            readD = False
            alpha = float(s[-1])
        elif len(s)>1 and s[0] == "param" and s[1] == "coordX":
            readX = True
            readY = False
            readD = False
        elif len(s)>1 and s[0] == "param" and s[1] == "coordY":
            readX = False
            readY = True
            readD = False
        elif len(s) > 1 and s[0] == "param" and s[1] == "d":
            readX = False
            readY = False
            readD = True
        elif (len(s)>0 and s[0] == ";") or len(s) <= 0:
            readX = False
            readY = False
            readD = False
        else:
            if readX:
                for i, j in pairwise(s):
                    coordX[int(i)] = int(j)
            elif readY:
                for i, j in pairwise(s):
                    coordY[int(i)] = int(j)
            elif readD:
                if s[-1] != ':=':
                    row = []
                    for col in s[1:]:
                        row.append(float(col))
                    danger.append(row)
    f.close()
    for i in range(0, (nNodes + 1)):
        for j in range(0, (nNodes + 1)):
            costs[i][j] = float("{0:.4f}".format(sqrt((coordX[i]-coordX[j])**2 + (coordY[i]-coordY[j])**2)))
    return nNodes, alpha, costs, coordX, coordY, danger

def readSolFile(filename, nNodes, alpha, costs, danger):
    solList = []
    solValue = 0
    dangerValue = 0
    arcs = [-1] * (nNodes + 1)
    outDegree = [0] * (nNodes + 1)
    inDegree = [0] * (nNodes + 1)
    f = open(filename, 'r')
    for line in f:
        line = line.strip()
        ls = line.split()
        s = int(ls[0])
        t = int(ls[1])
        dangerValue += danger[s][t]

        if arcs[s] == -1:
            arcs[s] = t
        else:
            print "Not feasible: multiple outgoing arcs from", s,"."
            sys.exit(1)
        outDegree[s] += 1
        if s > 0 and outDegree[s] > 1:
            print "Not feasible: out degree for node", s,"is not equal to 1."
            sys.exit(1)
        elif s == 0 and outDegree[s] > 0:
            print "Not feasible: out degree for node", s,"is not equal to 0."
            sys.exit(1)
        inDegree[t] += 1
        solList.append((s,t))
    f.close()
    #check out degree, must be equal to 1 for all note but 0 and equal to 0 for node 0
    for i in range(0, (nNodes + 1)):
        if i == 0 and outDegree[i] > 0: #redundant already checked
            print "Not feasible: out degree for node", i,"is not equal to 0."
            sys.exit(1)
        elif i > 0 and outDegree[i] != 1:
            print "Not feasible: out degree for node", i, "is not equal to 1."
            sys.exit(1)
    #check indegree, must be > 0 for node 0, solution value is equal to number of nodes with 0 in degree
    for i in range(0, (nNodes + 1)):
        if i == 0 and inDegree[i] <= 0: #redundant already checked
            print "Not feasible: in degree for node", i,"is not > 0."
            sys.exit(1)
        elif i > 0 and inDegree[i] == 0:
            solValue += 1
    #check alpha limitation
    for i in range(1, (nNodes + 1)):
        j = arcs[i]
        c = costs[i][j]
        while j != 0:
            c += costs[j][arcs[j]]
            j = arcs[j]
        if c > alpha*costs[i][0]:
            print "Not feasible: path from", i, "to 0 is longer than",alpha,"times the shortest path from", i, "to 0 ("\
                ,c,">", alpha*costs[i][0],")."
            sys.exit(1)
    dangerValue = float("{0:.4f}".format(dangerValue))
    return solValue, dangerValue, solList

if __name__ == "__main__":

    if len(sys.argv)!=3:
        print "Usage:\n python pedibus_checker.py <instance.dat> <solution.sol> "
        sys.exit(0)
    else:
        nNodes = 0
        alpha = 0
        costs = []
        solValue = 0
        coordX = []
        coordY = []
        danger = []
        datFilename = ""
        solFilename = ""
        for arg in sys.argv[1:]:
            filename, file_extension = os.path.splitext(arg)
            basename = os.path.basename(filename)
            if (os.path.isfile(arg) and file_extension == ".dat"):
                datFilename = basename
                nNodes, alpha, costs, coordX, coordY, danger = readDatFile(arg)

            elif (os.path.isfile(arg) and file_extension == ".sol"):
                solFilename = basename
                if(solFilename != datFilename):
                    print "Error: solution filename and data filename are not the same."
                    sys.exit(1)
                else:
                    solValue, dangerValue, solList = readSolFile(arg, nNodes, alpha, costs, danger)
                    print "Feasible solution, leafs:", solValue, "danger:",dangerValue
                    beta = 0.1
                    if(nNodes>10 and nNodes <= 100):
                        beta = 0.01
                    elif(nNodes>100 and nNodes <= 1000):
                        beta = 0.001
                    elif (nNodes > 1000):
                        beta = 0.0001
                    print "Value for the challenge:", str(round(solValue+(dangerValue*beta),4))
            else:
                if (os.path.isfile(arg)):
                    print "Wrong input file type ("+arg+")."
                else:
                    print "Cannot read input file"+arg+"."
                print "Usage:\n python pedibus_checker.py INSTANCE_FILE.dat SOLUTION_FILE.sol "
                sys.exit(1)

