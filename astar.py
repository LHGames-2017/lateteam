from structs import *
#from sets import Set

class Node(object):
    def __init__(self, point):
        self.point = point
        self.f = 0
        self.g = 0
        self.h = 0
        self.neighbors = []
        self.previous = None

    def addNeigbors(self):
        x = self.X
        y = self.Y
        if (x > 0):
            self.neighbors.append(Node(Point(x - 1, y)))
        if(x < 39):
            self.neighbors.append(Node(Point(x + 1, y)))
        if(y > 0):
            self.neighbors.append(Node(Point(x, y - 1)))
        if(y < 39):
            self.neighbors.append(Node(Point(x, y + 1)))
        return list


def astar(start, end, map):
    openSet = [start]
    closedSet = []
    while (openSet):
        best = 0
        for x in range [0, len(openSet)]:       
            #trouve le chemin le plus court dans openSet
            if(openSet[x].f < openSet[best].f):
                best = x
        current = openSet[best]
        #si le meilleur de openSet est le noeud final, on a fini
        if(current == end):              
            #retrace le chemin
            path = [current]
            while(current.previous != None):
                path.append(current.previous)
                current = current.previous
            return path
        openSet.remove(current)
        closedSet.append(current)
        current.addNeighbors()
        for n in neighbors:
            #deja traité si dans closedSet
            if (n not in closedSet and map[n.point.X][n.point.Y].Content == TileContent.Empty):
               temp = current.g + 1
               if (n in openSet):
                   if(temp < n.g):
                       n.g = temp
               else:
                   #heuristic = distance entre le point et la fin
                   n.h = n.point.Distance(end, n)
                   n.g = temp
                   openSet.append(n)
               n.previous = current
               n.f = n.g + n.h
            





