import copy
import random

"""
	Global variables and functions, which are common for any class
	N is the number of cells
"""

N=8
SCORE_MIN_VALUE=-100
SCORE_MAX_VALUE=100
colors = ['w', 'b']
directions = [-1, 1]
empty = '_'
units = ['w', 'W', 'b', 'B']
men = colors
kings = ['W', 'B']

def opposites(color):
	if color in colors:
		return ['w', 'W'] if color=='b' else ['b', 'B']
	else:
		raise RuntimeError('argument wrong type')

def self_units(color):
	if color in colors:
		return ['w', 'W'] if color=='w' else ['b', 'B']
	else:
		raise RuntimeError('argument wrong type')

def opposite_color(color):
	if color in colors:
		return 'w' if color=='b' else 'b'
	else:
		raise RuntimeError('argument wrong type')

def color_of(unit):
	if unit in units:
		return 'w' if unit in ['w', 'W'] else 'b'
	else:
		raise RuntimeError('argument wrong type')

def onboard(pos):
	if type(pos) is tuple:
		if (pos[0] in range(N)) and (pos[1] in range (N)):
			return True
		else:
			return False
	else:
		raise RuntimeError('argument wrong type or value')

def next_p(pos, dir_x, dir_y):
	if (type(pos) is tuple) and (dir_x in directions) and (dir_y in directions):
		next_pos = (pos[0] + dir_x, pos[1] + dir_y)
		return next_pos
	else:
		raise RuntimeError('argument wrong type or value')

def direction(unit):
	if unit in men:
		return [1] if unit == 'b' else [-1]
	elif unit in kings:
		return [-1,1]
	else:
		raise RuntimeError('argument wrong type')

def distance(pos1, pos2):
	if (type(pos1) is tuple) and (type(pos2) is tuple):
		if abs(pos1[1]-pos2[1]) == abs(pos1[0] - pos2[0]):
			return abs(pos1[1]-pos2[1])
		else:
			return SCORE_MAX_VALUE
	else:
		raise RuntimeError('argument wrong type or value')

def intermediary(pos1, pos2):
	if distance(pos1, pos2) == 2:
		diff0 = pos1[0] - pos2[0]
		diff1 = pos1[1] - pos2[1]
		return (pos1[0] - diff0/2, pos1[1] - diff1/2)
	else:
		return False

def kingrow(unit):
	if unit in men:
		row = 0 if unit is 'w' else N-1
		for i in range(N):
			yield (row, i)
	else:
		raise RuntimeError('argument wrong type')

def promote(unit):
	if unit in men:
		return unit.upper()
	else:
		raise RuntimeError('argument wrong type')

"""
	Class Table contain board and all possible moves
"""

class table:
	
	def __init__(self, board_string):
		self.board = copy.deepcopy(board_string)

	def unit(self, pos):
		if (type(pos) is tuple) and onboard(pos):
			return self.board[pos[0]][pos[1]]
		else:
			raise RuntimeError('argument wrong type or value')

	def set_unit(self, pos, unit):
		if (type(pos) is tuple) and onboard(pos) and (unit in units + [empty]):
			str_to_list = list(self.board[pos[0]])
			str_to_list[pos[1]] = unit
			self.board[pos[0]] = ''.join(str_to_list)
			return 0
		else:
			raise RuntimeError('argument wrong type or value')

	def is_jump(self, pos1, pos2, unit):
		if (type(pos1) is tuple) and (type(pos2) is tuple) and onboard(pos1) and (unit in units):
			jump_possible = onboard(pos2) and (self.unit(pos2) is empty) and (intermediary(pos1, pos2) is not False) and (self.unit(intermediary(pos1, pos2)) in opposites(color_of(unit)))
			return jump_possible
		else:
			raise RuntimeError('argument wrong type')

	def make_step(self, pos):
		if (type(pos) is tuple) and onboard(pos):
			for x in direction(self.unit(pos)):
				for y in directions:
					if onboard(next_p(pos, x, y)) and (self.unit(next_p(pos, x, y)) is empty):
						yield [pos, next_p(pos, x, y)]
		else:
			raise RuntimeError('argument wrong type')

	"""
		the arguments include unit because when call it recoursevely next start point for jump is empty but it should be made by the unit from the initial position
	"""
	def make_jump(self, pos, unit, path, jumped):
		if (type(pos) is tuple) and onboard(pos) and (type(path) is list):# and (type(jumped) is list) and (unit in units):
			jump_made = False
			collected_paths = []
			if (unit in men) and (pos in kingrow(unit)):
				unit = promote(unit)
			for x in direction(unit):
				for y in directions:
					if self.is_jump(pos, next_p(next_p(pos,x,y),x,y), unit) and (next_p(pos,x,y) not in jumped):
						collected_paths += copy.deepcopy(self.make_jump(next_p(next_p(pos,x,y),x,y), unit, path + [next_p(next_p(pos,x,y),x,y)], jumped + [next_p(pos,x,y)]))
						jump_made = True
			if not jump_made:
				return [path] if len(path) > 1 else []
			else:
				return collected_paths
		else:
			raise RuntimeError('argument wrong type or value')

	def allowed_moves(self, color):
		if color in colors:
			allowed_steps = []
			allowed_jumps = []
			for x, y in [ (x, y) for x in range(N) for y in range(N)]:
				if self.unit((x,y)) in self_units(color):
					for step in self.make_step((x,y)):
						allowed_steps += [step]
					allowed_jumps += self.make_jump((x,y), self.unit((x,y)), [(x,y)], [])
			return allowed_jumps if len(allowed_jumps) > 0 else allowed_steps
		else:
			raise RuntimeError('argument wrong type or value')

	def apply_path(self, path):
		if (type(path) is list) and (len(path) > 0) and (type(path[0]) is tuple) and onboard(path[0]):
			for prev_step, step in zip(path[:-1], path[1:]):
				if onboard(step):
					if (distance(prev_step, step) == 1) and (self.unit(step) is empty) and (self.unit(prev_step) in units):
						self.set_unit(step, self.unit(prev_step))
						self.set_unit(prev_step, empty)
						if (step in kingrow(color_of(self.unit(step)))) and (self.unit(step) in men):
							self.set_unit(step, promote(self.unit(step)))
					elif self.is_jump(prev_step, step, self.unit(prev_step)):
						self.set_unit(step, self.unit(prev_step))
						self.set_unit(prev_step, empty)
						self.set_unit(intermediary(prev_step, step), empty)
						if (step in kingrow(color_of(self.unit(step)))) and (self.unit(step) in men):
							self.set_unit(step, promote(self.unit(step)))
					else:
						raise RuntimeError('move ', prev_step, ' to ', step, ' is wrong')
		else:
			raise RuntimeError('argument wrong type')

	"""
		score() function evaluates score for color=color which is difference of color's unit sum and opponent's 
		unit sum and prefers unit in the middle of board rather then on the edge
	"""
	def score(self, color):
		if color in colors:
			score = [0,0]
			for x, y in [ (x, y) for x in range(N) for y in range(N)]:
				if self.unit((x,y)) in self_units(color):
					if y in [0, N-1]:
						score[0] -= 0.3
					score[0] += 1 if self.unit((x,y)) in men else 2
				elif self.unit((x,y)) in opposites(color):
					score[1] += 1 if self.unit((x,y)) in men else 2
					if y in [0, N-1]:
						score[1] -= 0.3
			return score[0]-score[1] if (score[0] and score[1]) else SCORE_MAX_VALUE if score[1]==0 else SCORE_MIN_VALUE
		else:
			raise RuntimeError('argument wrong type')

	def minimax(self, color, your_turn_now, depth):
		if (color in colors) and (type(your_turn_now) is bool) and (type(depth) is int):

			whos_turn_now = color if your_turn_now else opposite_color(color)

			if (len(self.allowed_moves(whos_turn_now)) == 0) or (depth == 0):
				return self.score(color)

			best_value = 0
			if your_turn_now:
				best_value = SCORE_MIN_VALUE
				for move in self.allowed_moves(color):
					t=table(copy.deepcopy(self.board))
					t.apply_path(move)
					value = t.minimax(color, False, depth - 1)
					best_value = max(best_value, value)
			if not your_turn_now:
				best_value = SCORE_MAX_VALUE
				for move in self.allowed_moves(opposite_color(color)):
					t=table(copy.deepcopy(self.board))
					t.apply_path(move)
					value = t.minimax(color, True, depth - 1)
					best_value = min(best_value, value)
			return best_value
		else:
			raise RuntimeError('argument wrong type or value')

	"""
		next_turn() makes random choice from the moves with the highest minimax value
	"""
	def next_turn(self, color):
		if color in colors:
			moves = self.allowed_moves(color)
			choices = {}
			for index, move in enumerate(moves):
				t = table(copy.deepcopy(self.board))
				t.apply_path(move)
				choices[index] = t.minimax(color, False, 3)
			best_choices = [i for i,j in choices.iteritems() if j == max(choices.values())]
			best_choice = random.choice(best_choices)
			return moves[best_choice]
		else:
			raise RuntimeError('argument wrong type')

