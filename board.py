import numpy as np
#Flat White = 0 110
#Flat Black = 1 111
#Wall White = 2 010
#Wall Black = 3 011
#Caps White = 4 100
#Caps Black = 5 101

#Top is higher
#ex. (50101)8

# White (piece % 2) == 0
# Black (piece % 2) == 1

# Road worthy (piece & 0x02) == 0

# Top of stack (piece & 0x06) != 1

"""
|6|
|0|1|2|3|4|5|
________
"""

class TakBoard():
	"""docstring for TakBoard"""
	def __init__(self, size):
		self.capstone_player1 = False
		self.capstone_player2 = False

		self.player1_turn = True
		self.move_number = 0
		
		self.board_size = size
		self.max_height = 44
		self.board = [[[] for x in range(self.board_size)] for x in range(self.board_size)]

		self.encode = {"w": 1.0, "b": 2.0, "sw": 3.0, "sb": 4.0, "cw": 5.0, "cb": 6.0}

	def get_current_string_board(self):
		return self.board

	def get_numpy_board(self):
		board_array=[]
		
		for row_index, rows in enumerate(self.board):
			row_array = []
			for col_index, cols in enumerate(rows):
				cell = []
				for height in cols:
					cell.append(self.encode[height.lower()])

				#Top is lowest index
				cell = cell[::-1]
				cell = np.pad(np.array(cell, dtype=int), (0, self.max_height - len(cell)), 'constant')
				row_array.append(cell)
			board_array.append(row_array)

		return np.array(board_array)

	def get_square(self, grid_location):
		x = (ord(grid_location[0].upper()) - ord("A"))
		y =  self.board_size - int(grid_location[1:])
		return self.board[y][x]

	def get_index_from_int(self, x, y):
		index = chr(ord("A") + y)
		index += str(self.board_size - x)
		return index

	def set_square(self, grid_location, peices):
		x = (ord(grid_location[0].upper()) - ord("A"))
		y =  self.board_size - int(grid_location[1:])
		self.board[y][x] = peices

	def append_square(self, grid_location, peice):
		x = (ord(grid_location[0].upper()) - ord("A"))
		y =  self.board_size - int(grid_location[1:])
		self.board[y][x].append(peice)

	def place(self, piece, grid_location):
		#print("Place: {}, gridloc:{} square:{}".format(piece, grid_location, self.get_square(grid_location)))

		#self.pretty_print_board()

		if self.get_square(grid_location) != []:
			raise Exception("Invalid Placement Location: gridlocation={}, currentsquare={}".format(grid_location, self.get_square(grid_location)))

		if self.move_number == 0:
			color = "b"
		elif self.move_number == 1:
			color = "w"
		elif self.player1_turn == True:
			#Is White
			color = "w"
		else:
			color = "b"

		if piece == None or piece == "":
			place_peice = color

		elif piece.lower() == "w" or piece.lower() == "s":
			place_peice = "S"+ color

		elif piece.lower() == "c":
			place_peice = "C"+ color
		
		else:
			raise ValueError("Invalid piece: {}".format(piece))

		#Place on board
		x = (ord(grid_location[0].upper()) - ord("A"))
		y =  self.board_size - int(grid_location[1:])
		self.board[y][x].append(place_peice)

		#Change turn
		self.player1_turn = not self.player1_turn
		self.move_number +=1

	def check_for_wall_crush(self, current_square, pop_array):
		#If last move and pops is 1 
		#Check if has capstone in peice

		piece = pop_array[0]
		wall = self.get_square(current_square)
		if len(wall) > 0:
			wall = self.get_square(current_square)[-1]
		else:
			return
		if piece[0].lower() == 'c' and wall != None and wall[0].lower() == 's':
			#print("Capstone wall crush")
			square = self.get_square(current_square)

			if square == None:
				square.append(wall[1:])
			else:
				square = square[:-1]
				square.append(wall[1:])

			self.set_square(current_square, square)

	def move(self, start, end, move_array):
		#Valid Size
		if np.sum(move_array) > self.board_size:
			raise Exception("Moving more tiles than board size")

		#print("Move: s:{}, e:{} square:{}".format(start, end, self.get_square(start)))

		count = np.sum(move_array)
		current_square = start
		#self.pretty_print_board()

		##TODO: Add wall smash to move

		#Valid Move
		if start[0] == end[0]:
			#Up and Down
			if int(start[1:]) > int(end[1:]):
				#Down

				#Set Start
				pop_array = self.get_square(start)[-count:]
				self.set_square(start, self.get_square(start)[:-count])

				for index, pops in enumerate(move_array):
					current_square = current_square[0] + str(int(current_square[1:]) -1)

					if len(move_array) -1 == index and pops == 1:
						self.check_for_wall_crush(current_square, pop_array)

					for x in range(pops):
						self.append_square(current_square, pop_array.pop(0))

			else:
				#Up

				#Set Start
				pop_array = self.get_square(start)[-count:]
				self.set_square(start, self.get_square(start)[:-count])

				for index, pops in enumerate(move_array):
					current_square = current_square[0] + str(int(current_square[1:]) +1)

					if len(move_array) -1 == index and pops == 1:
						self.check_for_wall_crush(current_square, pop_array)

					for x in range(pops):
						self.append_square(current_square, pop_array.pop(0))

		elif start[1:] == end[1:]:
			#left and right
			if start[0] > end[0]:
				#Left
				
				#Set Start
				pop_array = self.get_square(start)[-count:]
				self.set_square(start, self.get_square(start)[:-count])

				for index, pops in enumerate(move_array):
					current_square = chr(ord(current_square[0]) - 1) + current_square[1:]

					if len(move_array) -1 == index and pops == 1:
						self.check_for_wall_crush(current_square, pop_array)

					for x in range(pops):
						self.append_square(current_square, pop_array.pop(0))

			else:
				#Right
				
				#Set Start
				pop_array = self.get_square(start)[-count:]
				self.set_square(start, self.get_square(start)[:-count])

				for index, pops in enumerate(move_array):
					current_square = chr(ord(current_square[0]) + 1) + current_square[1:]

					if len(move_array) -1 == index and pops == 1:
						self.check_for_wall_crush(current_square, pop_array)

					for x in range(pops):
						self.append_square(current_square, pop_array.pop(0))
		else:
			raise Exception("Move is not up, down, left, or right")

		#Change turn
		self.player1_turn = not self.player1_turn
		self.move_number +=1

	def get_internal_cell(self, cell):
		out_list = []
		for element in cell:
			for key, value in self.encode.items():
				if value == element:
					out_list.append(key)
					break

		return out_list[::-1]

	def set_np_game_board(self, move_board, player1_turn):
		self.player1_turn = player1_turn
		count = 0
		#Get Rows
		for x, row in enumerate(self.board):
			for y, cell in enumerate(row):
				move_cell = self.get_internal_cell(move_board[x][y])
				count += len(move_cell)
				self.board[x][y] = move_cell

		self.move_number = count

	def convert_piece_to_result(self, piece):
		return int(self.encode[piece])

	def get_x_y_from_grid(self, location):
		#X is A-E
		#Y is 1-5
		y = int(location[1:])
		x = (ord(location[0].lower()) - ord('a') )
		return [x,y]

	def convert_move_to_result(self, move):
		out = [0,0,0,0,0,0,0,0,0,0,0,0]

		if move["movetype"] == "p":
			#Move Type
			out[0] = 1

			#Piece
			out[1] = self.convert_piece_to_result(move["piece"])

			temp_move = self.get_x_y_from_grid(move["placement"])

			#X,Y placement
			out[2] = temp_move[0]
			out[3] = temp_move[1]


		elif move["movetype"] == "m":
			#Move Type
			out[0] = 2

			temp_move = self.get_x_y_from_grid(move["start"])

			#X,Y Start stack
			out[4] = temp_move[0]
			out[5] = temp_move[1]

			#Direction
			out[6] = self.get_direction_from_start_end(move["start"], move["end"])

			#Number of pieces
			for x in range(len(move["order"])):
				out[7+x] = move["order"][x]

		else:
			raise Exception("Invalid Move Type Result")

		return out

	def get_result_from_new_board(self, move_board):
		changes = self.get_move_from_new_board(move_board)

		return self.convert_move_to_result(changes)

	def get_direction_from_start_end(self, start, end):
		size = 5

		#direction lowest is bottom left
		start_int = size * int(start[1:]) + (ord('a') - ord(start[0].lower()))
		end_int = size * int(end[1:]) + (ord('a') - ord(end[0].lower())) 

		if start_int > end_int:
			# Move Down or Left
			if end_int > start_int - size:
				#Move Down
				return 3
			else:
				#Move Left
				return 4
		else:
			#Move Up or Right
			if end_int >= start_int + size:
				#Move Up
				return 1
			else:
				#Move Right
				return 2

	def get_move_from_new_board(self, move_board):
		changes = []
		#Get Rows
		for x, row in enumerate(self.board):
			for y, cell in enumerate(row):
				#Convert cell to be compared
				move_cell = self.get_internal_cell(move_board[x][y])



				if len(cell) == len(move_cell):
					if cell != move_cell:
						#print("Change in the elements at the index x:{}, y:{}".format(x, y))
						#print("MoveCell: {}".format(move_cell))
						#print("Cell: {}".format(cell))
						changes.append({'x':x,'y':y, "move_cell": move_cell, "cell": cell, "index": self.get_index_from_int(x,y), "diff": len(cell) - len(move_cell)})
				else:
					#print("Change in number of elements at index x:{}, y:{}".format(x, y))
					#print("MoveCell: {}".format(move_cell))
					#print("Cell: {}".format(cell))
					changes.append({'x':x,'y':y, "move_cell": move_cell, "cell": cell, "index": self.get_index_from_int(x,y), "diff": len(cell) - len(move_cell)})
		
		#Place 
		#print(changes)
		if len(changes) == 1:
			change = changes[0]

			if len(change["move_cell"]) == 1:
				#print("[Place] {} {}".format("", change["index"]))
				self.place("", change["index"])

			else:
				#print("[Place] {} {}".format(change["move_cell"][0], change["index"]))
				self.place(change["move_cell"][0], change["index"])

			return {"movetype": "p", "piece": change["move_cell"][0], "placement":change["index"]}

			
		else:
			#Move
			movement_array = [row for row in changes]

			start = ""
			end = ""

			reverse = False

			for index, change in enumerate(changes):
				if change["diff"] > 0:
					#print("Start is " + change["index"])

					start = change["index"]
					movement_array.pop(index)

					if index == 0:
						movement_array = movement_array[::-1] 
						end = changes[-1]["index"]
					else:
						end = changes[0]["index"]
						#print(changes[0])
					break

			count_array = []
			for elem in movement_array:
				count_array.append(abs(elem["diff"]))

			
			#print("[Move]  Start: {}, End: {}, Array: {}".format(start, end, count_array))
			self.move(start, end, count_array)

			return {"movetype": "m", "start": start, "end": end, "order": count_array}


if __name__ == '__main__':
	p= TakBoard(5)

	p.place("", "D4")
	p.place("", "C3")
	p.place("C", "D3")
	p.place("C", "C4")
	p.place("S", "D5")
	p.place("S", "B4")
	#for x in p.get_current_string_board():
	#	print(x)
	#print()
	p.move("D5", "D4", [1])
	#for x in p.get_current_string_board():
	#	print(x)
	p.move("C4", "B4", [1])
	p.place("", "C4")
	p.move("B4", "D4", [1, 1])
	for x in p.get_current_string_board():
		print(x)

"""
	p.place("", "E1")
	p.place("", "D1")
	p.place("", "D2")
	p.place("", "D3")
	p.place("", "C2")

	p.place("", "E2")
	p.place("", "E3")
	p.place("", "D4")
	p.place("", "B2")
	p.move("D3", "E3", [1])
	p.place("C", "D3")
	p.place("", "E4")
	p.move("D3", "E3", [1])
	p.place("", "A2")
	p.move("E3", "E1", [1, 2])
	test = p.get_numpy_board()
	print(test.shape)
	
	p.place("", "A3")
	p.place("", "A1")
	p.move("A2", "B2", [1])
	p.place("", "A2")
	p.move("A3", "A2", [1])
	p.place("", "C3")
	p.place("", "B3")
	p.place("", "B4")
	p.place("", "C4")
	p.place("", "B1")
	p.place("W", "C1")
	p.move("E1", "C1", [2, 1])
"""