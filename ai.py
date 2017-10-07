from flask import Flask, request
from structs import *
import json
import numpy
from random import *

app = Flask(__name__)

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


def validMove(gameMap, nextMove):	#informe si la tile sur laquelle on veut se deplacer est vide
	return (gameMap[nextMove.X][nextMove.Y].Content == TileContent.Empty)

def move(player, gameMap, point): #fct qui fait bouger le personnage si la tile est empty
	if(validMove(gameMap, point)):
		return create_move_action(point)

def findActionTile(player, gameMap):  #signale si le personnage est sur une case voisine d'une tile sur laquelle on peut faire une aciton (pressource, shop, player)
	position = player.Position
	if((gameMap[position.X + 1][position.Y].Content  == TileContent.Resource) or (gameMap[position.X + 1][position.Y].Content  == TileContent.Player) or (gameMap[position.X + 1][position.Y].Content  == TileContent.Shop)):
		return Point(position.X + 1, position.Y);
	if((gameMap[position.X - 1][position.Y].Content  == TileContent.Resource) or (gameMap[position.X - 1][position.Y].Content  == TileContent.Player) or (gameMap[position.X - 1][position.Y].Content  == TileContent.Shop)):
		return Point(position.X - 1, position.Y);
	if((gameMap[position.X][position.Y + 1].Content  == TileContent.Resource) or (gameMap[position.X][position.Y + 1].Content  == TileContent.Player) or (gameMap[position.X][position.Y + 1].Content  == TileContent.Shop)):
		return Point(position.X, position.Y + 1);
	if((gameMap[position.X][position.Y - 1].Content == TileContent.Resource) or (gameMap[position.X][position.Y - 1].Content == TileContent.Player) or (gameMap[position.X][position.Y - 1].Content == TileContent.Shop)):
		return Point(position.X, position.Y - 1);

	return None

def goToActionTile(player, gameMap):
	#while(findActionTile(player, map) == None): #tant qu'on est pas a cote d'une ressource
	#	action = randint(1,4);
	#	if(action == 1):
	#		return move(player, map, Point(player.Position.X+1, player.Position.Y))#se deplacer a gauche
	#	if(action == 2):
	#		return move(player, map, Point(player.Position.X-1, player.Position.Y))#a droite
	#	if(action == 3):
	#		return move(player, map, Point(player.Position.X, player.Position.Y+1))# en haut
	#	if(action == 4):
	#		return move(player, map, Point(player.Position.X, player.Position.Y-1))#en bas
	

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
	if(gameMap[player.Position.X+1][player.Position.Y].Content == TileContent.Resource):
		return Point(player.Position.X+1,player.Position.Y)
	if(gameMap[player.Position.X-1][player.Position.Y].Content == TileContent.Resource):
		return Point(player.Position.X-1,player.Position.Y)
	if(gameMap[player.Position.X][player.Position.Y+1].Content == TileContent.Resource):
		return Point(player.Position.X,player.Position.Y+1)
	if(gameMap[player.Position.X][player.Position.Y-1].Content == TileContent.Resource):
		return Point(player.Position.X,player.Position.Y-1)
	return None

def MAIN_FUNCTION(player, gameMap): #fct de deplacement du AI pour miner des ressources	
	if(findActionTile(player, gameMap) == None):
		#return goToActionTile(player, gameMap) #on se rend a une action tile
		return create_move_action(get_random_point(player))
	else:
		return create_collect_action(findActionTile(player, gameMap))
		
	# le personnage va faire une action tant que son sac n'est pas vide
	#while(player.CarriedRessources <= (player.CarryingCapacity - 100)): #100 est la valeur de combien on peut ramasser de mineraux par action
	#	create_move_action(findActionTile(player, map))

	#fct de retour a la maison..



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
					Point(house["X"], house["Y"]),
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
	
	print("Player position: " + str(x) + "," + str(y))	

	p = get_collectable_point(player,deserialized_map)  
	if(p != None):
		print("Resource located at " + str(p.X) + "," + str(p.Y))
		return create_collect_action(p)
	else:
		return create_move_action(get_random_point(player))
	

@app.route("/", methods=["POST"])
def reponse():
	"""
	Point d'entree appelle par le GameServer
	"""
	return bot()

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080)
