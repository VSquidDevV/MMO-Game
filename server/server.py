# coding: utf-8
"""
!@ MAJOR TODO SENDING TO CLIENT!@
!@ OUTGOING REQUESTS FOR COLORED TEXT IN CONSOLE ARE LABELED AS COLOR :: !@
!@ EXAMPLE "::RED:: username ::WHITE:: joins the server"
"""
# (C) Ryan Schaefer 2016
# This is module meant to be run in conjunction with a server "handler"
# ---------------------------------------------------------------------
# .
# .
# .
# .
# GLHF implementing this

#Standars imports I don't need to explain this
import random
import socket
import pickle
import os
import console
import json
from time import sleep
#Resources class : multiple objects used for crafting
class ERROR(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)
class Resource(object):
	#every resource shares same characteristic overriden per specific resource
	name = None
	extract_time = 0
	def __init__(self):
		# each instance needs its own amount
		self.amount = 0		
class Wood(Resource):
	name = "wood"
	extract_time = 5	
class Stone(Resource):
	name = "stone"
	extract_time = 10
class Water(Resource):
	name = "water"
	extract_time = 1
class Sand(Resource):
	name = "sand"
	extract_time = 4
#Items do not stack / there is only one of them at a time
class Item(object):
	def __init__(self):
		#!@ TODO IMPLEMENT ITEM ID / NAME / AMOUNT
		self.id = 0
		self.amount = 1
		self.name = ""
#One square of a map; has resources / items / players / avialable moves from it / a position on the map
class Square(object):
	def __init__(self):
		self.items    = {}
		self.players  = {}
		self.buildings= {}
		self.moves = {}
		self.resources = []
		self.pos = None
	def describe(self):
		print "This is a basic description of a square, update it when you make a square."
	def extract(self, resource, player):
		# extraction can only be one resource at a time currently time is defined by the resource that is being extracted
		if self.resources[resource.name] > 0:
			sleep(resource.extract_time)
			self.resources[resource.name].amount -= 1
			player.add_resource(resource, 1)
			return True
		return False
	def init_resources(self):
		#changes what resources are avialable to be extracted
		self.resources = []
class Job(object):
	# for paying work
	def __init__(self, group, resource, salary):
		self.group = group
		self.salary = salary
		self.resource = resource
	def work(self, player):
		if player.name in self.group.members.keys() and player.pos.extract(self.resource, player):
			player.inventory[self.resource.name] -= 1
			self.group.resources[self.resource.name] += 1
			player.balance += self.salary
			self.group.balance -= self.salary
class Group(object):
	def __init__(self, name):
		if isinstance(name, basestring):
			self.resources = {}
			self.members = {}
			self.name = name
			self.balance = 0
		else:
			raise ERROR("Group arg must be a string")
class Player(object):
	def __init__(self, name):
		if isinstance(name, basestring):
			self.name = name
			self.inventory= {}
			self.job = None
			#!@ todo add more attributes
			self.attributes     = {"health": 100, "carry_capacity": 100, "evade": 0, "perception": 0}
			self.group          = None
			self.moves = {}
			self.balance = 0
		else:
			raise ERROR("Player arg must be string")
class Building(object):
	def __init__(self):
		self.players = {}
		self.items   = {}
	def describe(self):
		print "This is a basic description, update it when you make a building in a square"
class Swamp(Square):
	type = "swamp"
	def describe(self):
		print "You arrive in a bogged area."
		print "There appears to be a great amount of wood in this area, along with an ample water supply"
		print "You notice there are other buildings including %s" % "; ".join(self.buildings.keys())
		print "There are also %s" % "; ".join(self.items.keys())
	def init_resources(self):
		self.resources = [Water(), Wood()]
class Desert(Square):
	type = "desert"
	def describe(self):
		print "You arrive in a sprawling desert."
		print "There appears to be a great amount of sand here, there is an oasis in the middle of the desert."
		print "You notice there are other buildings including %s" % "; ".join(self.buildings.keys())
		print "There are also %s" % "; ".join(self.items.keys())
	def init_resources(self):
		self.resources = [Sand()]
class Forrest(Square):
	type = "forrest"
	def describe(self):
		print "You arrive in a wooded area."
		print "There appears to be a great amount of wood here, there is an opening in the middle."
		print "You notice there are other buildings including %s" % "; ".join(self.buildings.keys())
		print "There are also %s" % "; ".join(self.items.keys())
	def init_resources(self):
		self.resources = [Wood()]
class City(Square):
	type = "city"
	def describe(self):
		print "You arrive in a city."
		print "There are spawling skyscrapers where ever you turn."
		print "You notice there are other buildings including %s" % "; ".join(self.buildings.keys())
		print "There are also %s" % "; ".join(self.items.keys())
	def init_resources(self):
		self.resources = [Water()]
class Bank(Building):
	pass
class Fortress(Building):
	pass
class Map(object):
	def __init__(self, squares):
		self.map = {}
		self.squares = squares
	def update_moves(self, square, pos_x, pos_y):
	#called when adding to the map, when a player is on it it governs where the player can move to
		square.moves = {"left" : str(pos_x - 1) + ":" + str(pos_y), "up_left" : str(pos_x - 1) + ":" + str(pos_y - 1), "down_left" : str(pos_x - 1) + ":" + str(pos_y + 1), "right" : str(pos_x + 1) + ":" + str(pos_y), "up_right" :str(pos_x + 1) + ":" + str(pos_y - 1), "down_right":str(pos_x + 1) + ":" + str(pos_y + 1), "up": str(pos_x) + ":" + str(pos_y - 1), "down": str(pos_x) + ":" + str(pos_y + 1)}
		self.pos = str(pos_x)+ ":" +str(pos_y)
	def generate(self, size):
		#generates a map of size x size full of random squares that can be on the map
		#map is a dict full of number : number pairs naming the square
		#each square must be properly initilized
		if not isinstance(size, int) or size == 0:
			raise ERROR("Generation number must be an int > zero")
		t_size = float(size * size)
		c_size = 0.0
		cycle = 0
		for y in range(1, size + 1):
			for x in range(1, size + 1):
				name = str(x) + ":" + str(y)
				self.map.update({name : random.choice(self.squares)()})
				self.update_moves(self.map[name],x,y)
				self.map[name].init_resources()
				cycle += 1
				c_size += 1
				if cycle >= 10:
					print "Loading (%.2f%%)..." % ((c_size / t_size) * 100)
					console.clear()
					cycle = 0
class Engine(object):
	def __init__(self, map):
		self.map = map.map
		self.players = {}
		self.groups = {}
	def save(self):
		#dumps save to a pickle file
		pickle.dump(self.map, open(os.path.join("resources", "save.p"), 'wb'))
	def load(self, map):
		#loads save from a pickle file
		self.map = map
	def add_item(self, object, items):
		# engine adds items to a thing (map square or building)
		try:
			items[0]
		except:
			print "Items must be a list"
		for item in items:
			object.items.update({item.name: items})
	def add_player(self, object, player):
		# adds player to a square or building
		object.players.update({player.name: player})
	def remove_player(self, object, player):
		# removes player from square
		del object.players[player.name]
	def move(self, square, player, direction):
		#checks if move is in valid square then adds player to that square and removes them from the old square
		x, y = square.moves[direction].split(":")
		if (x != 0) and (y != 0):
			move = square.moves[direction]
			self.add_player(self.map[move], player)
			self.remove_player(square, player)
			return True
		else:
			return False
	def add_item(self, sqaure, player, item):
		# add an item to a player
		square.players[player.name].inventory.update({item.name: item})
	def use_item(self, square, player, item):
		square.players[player.name].inventory[item.name].use()
		del square.players[player.name].inventory[item.name]
	def spawn_player(self, player):
		# spawns player on random sqaure
		square = random.choice(self.map.values())
		if player not in self.players.keys():
			x = Player(player)
			square.players.update({x.name: x})
			x.pos = square.pos
			self.players.update({x.name: x})
			return True
		return False
	def destroy_player(self, square, player):
		# for when a player leaves the game
		del square.players[player.name]
	def create_group(self, group):
		x = Group(group)
		self.groups.update({x.name: x})
	def assign_group(self, group, player):
		group.members.update({player.name: player})
	def assign_job(self, group, player):
		pass
	def handout_resources(self):
		# randomly hands out resources to sqaure based on objects in dict
		for square in self.map:
			for resource in self.map[square].resources:
				resource.amount += random.randint(1, 10)
	def handout_items(self, square):
		pass
	def client_thread(self, socket):
		pass
	def create_job(self, group, resource, salary):
		#this is all we need to make america great again
		group.jobs = Job(group, resource, salary)
x = Map([City, Forrest])
x.generate(0)
main = Engine(x)
main.spawn_player("me")
main.create_group("group")
main.create_job(main.groups["group"], )