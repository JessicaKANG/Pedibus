# -*- encoding: utf-8 -*-
import os.path
import random
import math
import sys
from itertools import izip
from math import sqrt

if sys.version_info.major < 3:
      import Tkinter
else:
      import tkinter as Tkinter
      
from GA import GA


class TSP_WIN(object):
      def __init__(self, aRoot, aLifeCount = 500, aWidth = 560, aHeight = 330):
            self.root = aRoot
            self.lifeCount = aLifeCount
            self.width = aWidth
            self.height = aHeight
            self.canvas = Tkinter.Canvas(
                        self.root,
                        width = self.width,
                        height = self.height,
                  )
            self.canvas.pack(expand = Tkinter.YES, fill = Tkinter.BOTH)
            self.bindEvents()
            self.initCitys()
            self.new()
            self.title("PediBus")


      def initCitys(self):
            self.nNodes = 0
            self.alpha = 0
            self.costs = []
            
            self.coordX = []
            self.coordY = []
            self.danger = []
            datFilename = ""
            
            for arg in sys.argv[1:]:
                filename, file_extension = os.path.splitext(arg)
                basename = os.path.basename(filename)
                if (os.path.isfile(arg) and file_extension == ".dat"):
                    datFilename = basename
                    self.nNodes, self.alpha, self.costs, self.coordX, self.coordY, self.danger = readDatFile(arg)

                else:
                    if (os.path.isfile(arg)):
                        print "Wrong input file type ("+arg+")."
                    else:
                        print "Cannot read input file"+arg+"."
                    print "Usage:\n python pedibus_checker.py INSTANCE_FILE.dat "
                    sys.exit(1)
    
    
            
          
          
            self.citys = []
            for countNode in range(self.nNodes + 1):
                    self.citys.append((self.coordX[countNode],self.coordY[countNode]))

            #坐标变换
            minX, minY = self.citys[0][0], self.citys[0][1]
            maxX, maxY = minX, minY
            for city in self.citys[1:]:
                  if minX > city[0]:
                        minX = city[0]
                  if minY > city[1]:
                        minY = city[1]
                  if maxX < city[0]:
                        maxX = city[0]
                  if maxY < city[1]:
                        maxY = city[1]

            w = maxX - minX
            h = maxY - minY
            xoffset = 30
            yoffset = 30
            ww = self.width - 2 * xoffset
            hh = self.height - 2 * yoffset
            xx = ww / float(w)
            yy = hh / float(h)
            r = 5
            
            self.nodes = []
            self.nodes2 = []
            countCity = 0
            for city in self.citys:
                  x = (city[0] - minX ) * xx + xoffset
                  y = hh - (city[1] - minY) * yy + yoffset
                  self.nodes.append((x, y))
                  node = self.canvas.create_oval(x - r, y - r, x + r, y + r, # 画圆点
                        fill = "#ff0000",
                        outline = "#000000",
                        tags = "node",)
                  self.nodes2.append(node)
                  self.canvas.create_text(x-r, y-r,text=countCity,font="Times 10 bold ",tags="text")
                  countCity = countCity + 1
            self.school = self.citys[0]
            x = (self.school[0] - minX) * xx + xoffset
            y = hh - (self.school[1] - minY) * yy + yoffset
            node = self.canvas.create_oval(x - r, y -r, x + r, y + r,
                               fill = "#33ff33",
                               outline = "#000000",
                               tags = "node",)


      def matchFun(self):   # 评估适应度
          return lambda life: 1 / checkSol(life.gene, self.nNodes, self.alpha, self.costs, self.danger)
      


      def title(self, text):
            self.root.title(text)


      def line(self, order):
            self.canvas.delete("line")
            count = 0
            for i in range(self.nNodes):
                  p1 = self.nodes[count+1]
                  p2 = self.nodes[order[count]]
                  self.canvas.create_line(p1, p2, fill = "#000000", tags = "line")
                  count = count + 1

      def DFS(self, root, tree):
            order = distSort(self.costs[root])
            leaves = []
            for i in order:
                if tree[i[0]][0] == -1:
                    if (i[1] + tree[root][1]) < (self.costs[i[0]][0] * self.alpha): #feasible
                        tree[i[0]][0] = root
                        tree[i[0]][1] = i[1] + tree[root][1]
                        self.DFS(i[0],tree)
                    else :
                        leaves.append(i)
            return tree

      def bindEvents(self):
            self.root.bind("n", self.new)
            self.root.bind("g", self.start)
            self.root.bind("s", self.stop)


      def new(self, evt = None):
            self.isRunning = False
            #order = [ 0 for x in range(self.nNodes)]
            tree = [[-1,10000] for x in range(self.nNodes+1)]
            tree[0] = [0,0]
            tree = self.DFS(0,tree)
            
            tree = tree[1:]
            order = []
            for i in tree:
                order.append(i[0])
           #leaves = Leaves(order,self.nNodes)
            print order
            self.line(order)
            self.ga = GA(order, aCrossRate = 0.8,
                  aMutationRage = 0.6,
                  aLifeCount = self.lifeCount, 
                  aGeneLenght = self.nNodes,
                  aMatchFun = self.matchFun())

      def start(self, evt = None):
            self.isRunning = True
            while self.isRunning:
                  self.ga.next()
                  #distance = self.distance(self.ga.best.gene)
                  self.line(self.ga.best.gene)
                  self.title("PediBus-gen: %d" % self.ga.generation)
                  self.canvas.update()


      def stop(self, evt = None):
            print self.ga.best.gene
            self.isRunning = False


      def mainloop(self):
            self.root.mainloop()


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



def checkSol(solGene, nNodes, alpha, costs, danger):
    solValue = 0
    dangerValue = 0
    arcs = [-1] * (nNodes + 1)
    outDegree = [0] * (nNodes + 1)
    inDegree = [0] * (nNodes + 1)
    graph = dict()
    count = 0
    for cell in solGene:
        s = count + 1
        t = solGene[count]
        graph[s] = []
        graph[s].append(t)
        dangerValue += danger[s][t]
        if arcs[s] == -1:
            arcs[s] = t
        else:
            return 400
        outDegree[s] += 1
        if s > 0 and outDegree[s] > 1:
            return 400
        elif s == 0 and outDegree[s] > 0:
            return 400
        inDegree[t] += 1
        count = count + 1
    #check cycle
    if cyclic(graph):
        return 301
    #check out degree, must be equal to 1 for all note but 0 and equal to 0 for node 0
    for i in range(0, (nNodes + 1)):
        if i == 0 and outDegree[i] > 0: #redundant already checked
            
            return 301
        elif i > 0 and outDegree[i] != 1:
            
            return 301
    #check in degree, must be > 0 for node 0, solution value is equal to number of nodes with 0 in degree
    for i in range(0, (nNodes + 1)):
        if i == 0 and inDegree[i] <= 0: #redundant already checked
        
            return 301
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
            return 350
    dangerValue = float("{0:.4f}".format(dangerValue))
    beta = 0.1
    if(nNodes>10 and nNodes <= 100):
        beta = 0.01
    elif(nNodes>100 and nNodes <= 1000):
        beta = 0.001
    elif (nNodes > 1000):
        beta = 0.0001
    return solValue+(dangerValue*beta)


def cyclic(graph):
    """Return True if the directed graph has a cycle.
        The graph must be represented as a dictionary mapping vertices to
        iterables of neighbouring vertices. For example:
        
        >>> cyclic({1: (2,), 2: (3,), 3: (1,)})
        True
        >>> cyclic({1: (2,), 2: (3,), 3: (4,)})
        False
        
        """
    visited = set()
    path = [object()]
    path_set = set(path)
    stack = [iter(graph)]
    while stack:
        for v in stack[-1]:
            if v in path_set:
                return True
            elif v not in visited:
                visited.add(v)
                path.append(v)
                path_set.add(v)
                stack.append(iter(graph.get(v, ())))
                break
        else:
            path_set.remove(path.pop())
            stack.pop()
    return False



def distSort(arr):
    b=sorted(enumerate(arr), key=lambda x:x[1])
    return b






def main():
    #tsp = TSP()
    #tsp.run(10000)
    
    tsp = TSP_WIN(Tkinter.Tk())
    tsp.mainloop()


if __name__ == '__main__':
    if len(sys.argv)!=2:
        print "Usage:\n python pedibus_solver.py <instance.dat>"
        sys.exit(0)
    else:
        main()