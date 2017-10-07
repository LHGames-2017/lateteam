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

	def addNeighbors(self):
		x = self.point.X
		y = self.point.Y
		if (x > 0):
			self.neighbors.append(Node(Point(x - 1, y)))
		if(x < 19):
			self.neighbors.append(Node(Point(x + 1, y)))
		if(y > 0):
			self.neighbors.append(Node(Point(x, y - 1)))
		if(y < 19):
			self.neighbors.append(Node(Point(x, y + 1)))
   

def astar(start, end, map):
	openSet = set()
	openSet.add(Node(start))
	closedSet = set()
	while (openSet):
		best = None   #index of node with the best f
		for x in openSet: 
			#trouve le chemin le plus court dans openSet
			if(best == None): best = x
			elif(x.f < best.f):
				best = x
		current = best
		#si le meilleur de openSet est le noeud final, on a fini
		if(current.point == end):			  
			#retrace le chemin
			path = []
			while(current.previous != None):
				path.append(current.previous.point)
				current = current.previous
			path.reverse()   #liste des movements dans l'ordre a partir de la position actuelle (exculisevement) jusqu'a la position finale.
			return path
			#return path.pop().point  #retourne que le premiere mouvement a faire du path jusqu'a end
			
		openSet.remove(current)
		closedSet.add(current)
		current.addNeighbors()
		for n in current.neighbors:
		#deja traite si dans closedSet
			if (n not in closedSet and map[n.point.X][n.point.Y].Content == TileContent.Empty):
			  	temp = current.g + 1
			   	if (n in openSet):
				  	if(temp < n.g):
						n.g = temp
						n.f = n.g + n.h
						n.previous = current
			   	else:
				   	#heuristic = distance entre le point et la fin
				   	n.h = n.point.Distance(end, n.point)
				   	n.g = temp
				   	n.f = n.g + n.h
					n.previous = current
				   	openSet.add(n)
			  
			
