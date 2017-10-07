from flask import Flask, request
from structs import *
import json
import numpy
from random import *
from astar import *

app = Flask(__name__)

dest = None

def create_action(action_type, target):
	actionContent = ActionContent(action_type, target.__dict__)
	return json.dumps(actionContent.__dict__)

def create_move_action(target):
	return create_action("MoveAction", target)

def create_attack_action(target):
	return create_action("AttackAction", target)

def create_collect_action(target):
	return create_action("CollectAction", target)

def create_steal_action(target):
	return create_action("StealAction", target)

def create_heal_action():
	return create_action("HealAction", "")

def create_purchase_action(item):
	return create_action("PurchaseAction", item)

def deserialize_map(serialized_map):
	"""
	Fonction utilitaire pour comprendre la map
	"""
	serialized_map = serialized_map[1:]
	rows = serialized_map.split('[')
	column = rows[0].split('{')
	deserialized_map = [[Tile() for x in range(40)] for y in range(40)]
	for i in range(len(rows) - 1):
		column = rows[i + 1].split('{')

		for j in range(len(column) - 1):
			infos = column[j + 1].split(',')
			end_index = infos[2].find('}')
			content = int(infos[0])
			x = int(infos[1])
			y = int(infos[2][:end_index])
			deserialized_map[i][j] = Tile(content, x, y)

	return deserialized_map



#**************************************************************NOTRE CODE******************************************************************************************

def goToActionTile(player, gameMap):
	action = randint(1,4);
	if(action == 1):
		return move(player, gameMap, Point(player.Position.X+1, player.Position.Y))#se deplacer a gauche
	if(action == 2):
		return move(player, gameMap, Point(player.Position.X-1, player.Position.Y))#a droite
	if(action == 3):
		return move(player, gameMap, Point(player.Position.X, player.Position.Y+1))# en haut
	if(action == 4):
		return move(player, gameMap, Point(player.Position.X, player.Position.Y-1))#en bas

def get_random_point(player):
	action = randint(1,4);
	if(action == 1):
		return Point(player.Position.X+1, player.Position.Y)
	if(action == 2):
		return Point(player.Position.X-1, player.Position.Y)
	if(action == 3):
		return Point(player.Position.X, player.Position.Y+1)
	if(action == 4):
		return Point(player.Position.X, player.Position.Y-1)

def get_collectable_point(player, gameMap):	
	if(gameMap[9][10].Content == TileContent.Resource):
		return Point(player.Position.X-1,player.Position.Y)
	if(gameMap[11][10].Content == TileContent.Resource):
		return Point(player.Position.X+1,player.Position.Y)
	if(gameMap[10][9].Content == TileContent.Resource):
		return Point(player.Position.X,player.Position.Y-1)
	if(gameMap[10][11].Content == TileContent.Resource):
		return Point(player.Position.X,player.Position.Y+1)
	return None

def get_closest_resource(player, gamemap):
	p = None
	for i in range(20):
		for j in range(20): 
			content = gamemap[i][j].Content  
			#print("content(" + str(i) + "," + str(j) + ") = " + str(content))
			if(content == TileContent.Resource):
				newP = Point(i,j)
				if(p == None):
					p = newP
				elif(newP.Distance(Point(10,10),newP) < p.Distance(Point(10,10),p)):
					p = newP

	return Point(player.Position.X + p.X-10, player.Position.Y + p.Y-10)

def get_house_location(player, gamemap):
	p = None
	for i in range(20):
		for j in range(20): 
			content = gamemap[i][j].Content  
			#print("content(" + str(i) + "," + str(j) + ") = " + str(content))
			if(content == TileContent.House):
				newP = Point(i,j)
				if(p == None):
					p = newP
				elif(newP.Distance(Point(10,10),newP) < p.Distance(Point(10,10),p)):
					p = newP

	return Point(player.Position.X + p.X-10, player.Position.Y + p.Y-10) 

def get_smart_move(player, dest, gamemap):
	#deltaX = dest.X - player.Position.X
	#deltaY = dest.Y - player.Position.Y

	if(player.Position.X > dest.X):
		content = gamemap[9,10].Content 	
		if(content != TileContent.Wall and content != TileContent.Lava and content != TileContent.Player):
			return create_move_action(Point(player.Position.X-1,player.Position.Y))
		else:
			return create_move_action(Point(player.Position.X,player.Position.Y-1))	
	else:
		content = gamemap[11,10].Content 	
		if(content != TileContent.Wall and content != TileContent.Lava and content != TileContent.Player):
			return create_move_action(Point(player.Position.X+1,player.Position.Y))
		else:
			return create_move_action(Point(player.Position.X,player.Position.Y+1))

	if(player.Position.Y > dest.Y):
		content = gamemap[10,9].Content 	
		if(content != TileContent.Wall and content != TileContent.Lava and content != TileContent.Player):
			return create_move_action(Point(player.Position.X,player.Position.Y-1))
		else:
			return create_move_action(Point(player.Position.X-1,player.Position.Y))
	else:
		content = gamemap[10,11].Content 	
		if(content != TileContent.Wall and content != TileContent.Lava and content != TileContent.Player):
			return create_move_action(Point(player.Position.X,player.Position.Y+1))
		else:
			return create_move_action(Point(player.Position.X+1,player.Position.Y))

def bot():
	"""
	Main de votre bot.
	"""

	map_json = request.form["map"]

	# Player info

	encoded_map = map_json.encode()
	map_json = json.loads(encoded_map)
	p = map_json["Player"]
	pos = p["Position"]
	x = pos["X"]
	y = pos["Y"]
	house = p["HouseLocation"]
	player = Player(p["Health"], p["MaxHealth"], Point(x,y),
					Point(house["X"], house["Y"]), p["Score"],
					p["CarriedResources"], p["CarryingCapacity"])

	# Map
	serialized_map = map_json["CustomSerializedMap"]
	deserialized_map = deserialize_map(serialized_map)

	otherPlayers = []

	for player_dict in map_json["OtherPlayers"]:
		for player_name in player_dict.keys():
			player_info = player_dict[player_name]
			p_pos = player_info["Position"]
			player_info = PlayerInfo(player_info["Health"],
									 player_info["MaxHealth"],
									 Point(p_pos["X"], p_pos["Y"]))

			otherPlayers.append({player_name: player_info })
	
	print("Player position: " + str(player.Position))	
	#print(map_json)

	if(player.CarriedRessources < player.CarryingCapacity):
		dest = get_closest_resource(player, deserialized_map)
	else:
		dest = get_house_location(player, deserialized_map)

	print("Target " + str(dest))
	print("Resources: " + str(player.CarriedRessources) + " (max " + str(player.CarryingCapacity) + ")")

	if(dest.Distance(dest,player.Position) == 1):
		while(player.CarriedRessources < player.CarryingCapacity):	
			return create_collect_action(dest)
	
	while(x > dest.X or x < dest.X):
		if(x > dest.X):
			return create_move_action(Point(x-1,y))
		else:
			return create_move_action(Point(x+1,y))

	while(y > dest.Y or y < dest.Y):
		if(y > dest.Y):
			return create_move_action(Point(x,y-1))
		else:
			return create_move_action(Point(x,y+1))
	
	#while(player.CarriedRessources < player.CarryingCapacity):	
	#	return create_collect_action(dest)


@app.route("/", methods=["POST"])
def reponse():
	"""
	Point d'entree appelle par le GameServer
	"""
	return bot()

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)
