# Welcome to SimPool!
# Written by Hunter Tidwell, 2013

# Pitch sheet: https://i.imgur.com/CqLnbJL.jpg

###############################################################################
#   UPDATE HISTORY   #
###############################################################################

# Updates after submitted version:
#
# Wall collision sound now proportional to ball speed
# Physics now backtracks balls before calculating bounce
#     (means more accurate angles of collision)
# Physics timer delay increased
#     (means less change in play speed as balls decrease)
# Highscores are working
# Improved button and text label colors
# 8ball mode starts by placing the cue ball
# Improved sound volumes
# New image and sound links, no longer from my dropbox
# Corrected game-over image for 8ball mode
# Further improved sound levels
# Added soundtrack
# Added alternate soundtrack
# Improved soundtrack reliability (load sound only once, switch between sound
#     objects)
# Improved soundtrack volume when transitioning between schemes; removed delay
#     at beginning of default soundtrack

###############################################################################
#   IMPORT MODULES   #
###############################################################################

import simplegui
import random
import math
import time

###############################################################################
#   INITIALIZE GLOBAL VARIABLES   #
###############################################################################

# Pixels per inch
PPI = 10

game_states = ['menu', '8ball', 'arcade',
               'highscores', 'settings', 'how2'
               ]
game_state = 'menu'

soundtrack_url = \
'https://s1.vocaroo.com/media/download_temp/Vocaroo_s14kDrIbIZgu.mp3'
soundtrack = simplegui.load_sound(soundtrack_url)
soundtrack_vol = 0.5
soundtrack_max_vol = 0.5
soundtrack_time = (5 * 60 + 54) * 1000

alt_soundtrack_url = \
'https://s1.vocaroo.com/media/download_temp/Vocaroo_s1AZW8DJNBY5.mp3'
alt_soundtrack = simplegui.load_sound(alt_soundtrack_url)
alt_soundtrack_vol = 0.3
alt_soundtrack_max_vol = 0.3
alt_soundtrack_time = (3 * 60 + 26) * 1000

current_soundtrack = soundtrack
current_soundtrack_vol = soundtrack_vol
current_soundtrack_max_vol = soundtrack_max_vol
current_soundtrack_time = soundtrack_time

ball_collide_sound_url = \
'https://s1.vocaroo.com/media/download_temp/Vocaroo_s1oxOTANn8gt.mp3'
ball_collide_sound = simplegui.load_sound(ball_collide_sound_url)
ball_vol_max = 0.75
ball_vol_min = 0.15

wall_collide_sound_url = \
'https://s1.vocaroo.com/media/download_temp/Vocaroo_s1fHXHyzB1v9.mp3'
wall_collide_sound = simplegui.load_sound(wall_collide_sound_url)
wall_vol_max = 1.0
wall_vol_min = 0.2

pocketed_sound_url = \
'https://s1.vocaroo.com/media/download_temp/Vocaroo_s1DE7fLehKB0.mp3'
pocketed_sound = simplegui.load_sound(pocketed_sound_url)
pocketed_vol_max = 0.75
pocketed_vol_min = 0.15


###############################################################################
#   DEFINE HELPER FUNCTIONS   #
###############################################################################

def add(u, v):
	return [u[0] + v[0], u[1] + v[1]]

def sub(u, v):
	return [u[0] - v[0], u[1] - v[1]]

def mul(c, v):
	return [c * v[0], c * v[1]]

def dot(u, v):
	return (u[0] * v[0]) + (u[1] * v[1])

def mag2(v):
	return dot(v, v)

def mag(v):
	return math.sqrt(mag2(v))

def dist2(u, v):
	return mag2(sub(u, v))

def dist(u, v):
	return math.sqrt(dist2(u, v))

def unit(v):
	# Using trig functions is slightly faster than finding magnitude
	ang = math.atan2(v[1], v[0])
	return [math.cos(ang), math.sin(ang)]

def rectangle(center, dims):
	tl = sub(center, mul(0.5, dims))
	points = [add(tl, [dims[0] * i, dims[1] * j])
	          for i in [0, 1] for j in [0, 1]
	          ]
	points[2], points[3] = points[3], points[2]
	return points

# Button handlers #############################################################

def goto_menu():
	global game_state
	game_state = 'menu'
	physics_timer.stop()
	Hand.drag_end = None

def goto_highscores():
	global game_state
	game_state = 'highscores'

def goto_settings():
	global game_state
	game_state = 'settings'

def goto_how2():
	global game_state
	game_state = 'how2'

def goto_8ball():
	global game_state, balls
	game_state = '8ball'
	physics_timer.stop()
	
	ur = mul(Ball.rad, [math.sqrt(3), -1])
	d = [0, 2 * Ball.rad]
	triangle = []
	for i in range(5):
		for j in range(i + 1):
			triangle.append(add(foot, add(mul(i, ur), mul(j, d))))
	cornnums = [random.randrange(7) + i*8 for i in range(2)]
	positions = list(triangle)
	u_c = positions.pop(14)
	l_c = positions.pop(10)
	cornpos = [u_c, l_c]
	random.shuffle(cornpos)
	m = positions.pop(4)
	random.shuffle(positions)
	positions.insert(cornnums[1], cornpos[1])
	positions.insert(6, m)
	positions.insert(cornnums[0], cornpos[0])
	#positions.insert(0, head)
	balls = [Ball(i + 1, positions[i]) for i in range(15)]
	
	#balls = [Ball(8, foot)]
		
	Hand.state = 'placing'
	Hand.unbroken = True

def goto_arcade():
	global game_state, balls
	goto_8ball()
	balls.insert(0, Ball(0, head))
	game_state = 'arcade'
	physics_timer.stop()
	Hand.state = 'aiming'
	Hand.score = 0
#	balls[0].vel = [Ball.max_vel, 0]
#	balls[0].speed = mag(balls[0].vel)
#	balls[0].acc = [-Ball.friction, 0]

def swap_colors():
	global border_color, trim_color, cloth_color, score_color, \
	current_soundtrack_vol, current_soundtrack_max_vol, \
	current_soundtrack_time, soundtrack_timer, current_soundtrack
	
	current_soundtrack.pause()
	soundtrack_timer.stop()
	
	if trim_color == 'green':
		trim_color = 'blue'
		border_color = 'grey'
		cloth_color = 'darkblue'
		score_color = 'lightblue'
		
		current_soundtrack = alt_soundtrack
		current_soundtrack_vol = \
		alt_soundtrack_max_vol * current_soundtrack_vol / current_soundtrack_max_vol
		current_soundtrack_max_vol = alt_soundtrack_max_vol
		current_soundtrack_time = alt_soundtrack_time
		soundtrack_timer = simplegui.create_timer(current_soundtrack_time,
		                                          restart_soundtrack
		                                          )
	else:
		trim_color = 'green'
		border_color = 'saddlebrown'
		cloth_color = 'darkgreen'
		score_color = 'black'
		
		current_soundtrack = soundtrack
		current_soundtrack_vol = \
		soundtrack_max_vol * current_soundtrack_vol / current_soundtrack_max_vol
		current_soundtrack_max_vol = soundtrack_max_vol
		current_soundtrack_time = soundtrack_time
		soundtrack_timer = simplegui.create_timer(current_soundtrack_time,
		                                          restart_soundtrack
		                                          )
	soundtrack_timer.start()
	current_soundtrack.rewind()
	current_soundtrack.set_volume(current_soundtrack_vol)
	current_soundtrack.play()
	
	Ball.outlined = cloth_color
	for i in range(3):
		buttons['menu'][i].bg_color = trim_color
		buttons['menu'][i].color = score_color
	for i in range(3):
		buttons['settings'][i].bg_color = trim_color
		buttons['settings'][i].color = score_color
	for i in range(3):
		buttons['highscores'][i].bg_color = trim_color
		buttons['highscores'][i].color = score_color
		
def swap_shortcuts():
	global shortcuts_on
	if shortcuts_on:
		shortcuts_on = False
		buttons['settings'][1] = Button('Keyboard shortcuts disabled',
		                                btn_pos[3], swap_shortcuts,
		                                color = score_color,
		                                bg_color = trim_color
		                                )
	else:
		shortcuts_on = True
		buttons['settings'][1] = Button('Keyboard shortcuts enabled',
		                                btn_pos[3], swap_shortcuts,
		                                color = score_color,
		                                bg_color = trim_color
		                                )
		
def swap_cheat():
	global cheat
	if (cheat > 1) and (cheat < 2):
		cheat = 10
		buttons['settings'][2] = Button('Extra long cue ball vector',
		                                btn_pos[5], swap_cheat,
		                                color = score_color,
		                                bg_color = trim_color
		                                )
	elif cheat > 9:
		cheat = 0
		buttons['settings'][2] = Button('Hide cue ball vector',
		                                btn_pos[5], swap_cheat,
		                                color = score_color,
		                                bg_color = trim_color
		                                )
	elif cheat < 1:
		cheat = 1.5
		buttons['settings'][2] = Button('Normal length cue ball vector',
		                                btn_pos[5], swap_cheat,
		                                color = score_color,
		                                bg_color = trim_color
		                                )


def place_ball():
	if Hand.state not in ['over', 'striking', 'waiting']:
		Hand.drag_end = None
		Hand.state = 'placing'
		if balls[0].num == 0:
			balls.pop(0)

# Other helpers ###############################################################

def gameplay_mode():
	# Returns true if the game_state is one of the gameplay modes
	in_play_mode = game_state == '8ball'
	in_play_mode = in_play_mode or game_state == 'arcade'
	return in_play_mode

def constrain_to_table(pos):
	pos = list(pos)
	if pos[0] < border + Ball.rad:
		pos[0] = border + Ball.rad
	if pos[0] > border + table_dims[0] - Ball.rad:
		pos[0] = border + table_dims[0] - Ball.rad
	if pos[1] < border + Ball.rad:
		pos[1] = border + Ball.rad
	if pos[1] > border + table_dims[1] - Ball.rad:
		pos[1] = border + table_dims[1] - Ball.rad
	return pos

def constrain_to_kitchen(pos):
	pos = constrain_to_table(pos)
	pos[0] = min([pos[0], border + table_dims[0]/4])
	return pos

def restart_soundtrack():
	current_soundtrack.rewind()
	current_soundtrack.play()

def constrain(value, lower_bound, upper_bound):
	if value < lower_bound:
		value = lower_bound
	elif value > upper_bound:
		value = upper_bound
	return value

###############################################################################
#   DEFINE CLASSES   #
###############################################################################

class Button:
	def __init__(self, text, pos, handler, size=2*PPI, color='black',
		         bg_color='white'):
		self.text = text
		self.handler = handler
		self.pos = pos
		self.size = size
		self.color = color
		self.bg_color = bg_color
		
		text_width = frame.get_canvas_textwidth(self.text, self.size)
		height = self.size * 1.6
		dims = [text_width + self.size, height]
		
		self.polygon = rectangle(self.pos, dims)
		self.text_pos = add(self.polygon[1],
		                    [0.5 * self.size, -0.5 * self.size]
		                    )
		self.bounds = [[self.polygon[0][i], self.polygon[2][i]]
		               for i in [0, 1]
		               ]
	
	def draw(self, canvas):
		canvas.draw_polygon(self.polygon, 1, self.color, self.bg_color)
		canvas.draw_text(self.text, self.text_pos, self.size, self.color)
	
	def click(self, pos):
		truths = [pos[i] > self.bounds[i][0] and pos[i] < self.bounds[i][1]
		          for i in [0, 1]
		          ]
		if truths[0] and truths[1]:
			self.handler()
			return 1
		else: return 0
	
#class TextPage:
#	def __init__(self, string, pos, size):
#		self.pos = pos
#		self.string = string
#		self.size = size
#	
#	def draw(self, canvas):
#		canvas.draw_text(self.string, self.pos, self.size, score_color)
	
class Wall:
	tol = 0.001
	def __init__(self, ends):
		self.ends = ends
		self.line = sub(ends[1], ends[0])
		self.norm = unit([-self.line[1], self.line[0]])
		self.vertical = self.horizontal = False
		if abs(self.ends[0][0] - self.ends[1][0]) < Wall.tol:
			self.vertical = True
		elif abs(self.ends[0][1] - self.ends[1][1]) < Wall.tol:
			self.horizontal = True
	
	def draw(self, canvas):
		midpoint = mul(0.5, add(*self.ends))
		canvas.draw_line(midpoint, add(midpoint, mul(10, self.norm)), 2, 'red') 
	
class Pocket:
	rad = 2 * PPI
	
	def __init__(self, pos):
		self.pos = pos
		
	def draw(self, canvas):
		canvas.draw_circle(self.pos, Pocket.rad, 1, 'black', 'black')
	
class Ball:
	rad = 1.125 * PPI
	rad2 = rad * rad
	diam2 = 4 * rad * rad
	pockdist2 = (rad + Pocket.rad) * (rad + Pocket.rad)
	pockdist2 = pockdist2 / 3 # Makes it harder to get in pockets
	max_vel = 1.75 * rad
	img_str = 'https://i.imgur.com/p9Czqfj.png'
	img = simplegui.load_image(img_str)
	img_ctr = [25, 25]
	img_w_h = [50, 50]
	w_h = mul(2, [rad, rad])
	outlined = 'darkgreen'
	
	friction = 0.003 * PPI
	ball_collide_loss = 0 # 0.03
	wall_collide_loss = 0.2 # 0.25
	
	def __init__(self, num, pos):
		self.num = num
		self.pos = pos
		self.img_ctr_top = add(Ball.img_ctr, [self.num * Ball.img_w_h[0], 0])
		self.vel = [0, 0]
		self.speed = 0
		self.acc = [0, 0]
		self.ang = [2 * math.pi * random.random() for i in range(2)]
		self.ang_selector = round(self.ang[1] % (2 * pi) / (pi / 6))
		self.img_ctr = \
		[self.img_ctr_top[0],
		 self.img_ctr_top[1] + self.ang_selector * Ball.img_w_h[1]]
	
	colors = ['white', 'yellow', 'blue', 'red', 'purple', 'orange',
	          'limegreen', 'brown', 'black', 'yellow', 'blue', 'red',
	          'purple', 'orange', 'limegreen', 'brown'
	          ]
	def draw(self, canvas):
		self.ang_selector = int(self.ang[1] % (2 * pi) / (pi / 6))
		self.img_ctr = \
		[self.img_ctr_top[0],
		 self.img_ctr_top[1] + self.ang_selector * Ball.img_w_h[1]
		 ]
		if self.num == 0:
			ang = 0
		else:
			ang = self.ang[0]
		canvas.draw_image(Ball.img, self.img_ctr, Ball.img_w_h, self.pos,
		                  Ball.w_h, ang)
		if Ball.outlined:
			canvas.draw_circle(self.pos, Ball.rad, 1, Ball.outlined)
		
	def advance(self):
		if self.speed < 0:
			self.vel = [0, 0]
			self.speed = 0
			self.acc = [0, 0]
		elif self.speed > 0:
			self.pos = add(self.pos, self.vel)
			self.ang[1] += self.speed / Ball.rad
			self.vel = add(self.vel, self.acc)
			self.speed -= Ball.friction
		
	def backtrack(self, amt=0.5):
		self.pos = sub(self.pos, mul(amt, self.vel))
		
	def collide_check_corner(self, corner):
		to_corner = sub(corner, self.pos)
		if mag2(to_corner) < Ball.rad2:
			to_corner_unit = unit(to_corner)
			delta_v_mag = dot(self.vel, to_corner_unit)
			if delta_v_mag > 0:
				delta_v = mul(-2 * delta_v_mag, to_corner_unit)
				self.vel = add(self.vel, delta_v)
				self.vel = mul((1 - Ball.wall_collide_loss), self.vel)
				self.speed *= (1 - Ball.wall_collide_loss)
				if self.speed > 0:
					self.acc = mul(-Ball.friction / self.speed, self.vel)
					self.ang[0] = math.atan2(-self.vel[0], self.vel[1])
				else:
					self.acc = [0, 0]
				wall_collide_sound.rewind()
				vol = wall_vol_min + \
				(wall_vol_max - wall_vol_min) * delta_v_mag / Ball.max_vel
				vol = min([1, vol])
				vol = max([0, vol])
				wall_collide_sound.set_volume(vol)
				wall_collide_sound.play()
				return True
		
	def collide_check_pocket(self, pocket):
		if dist2(self.pos, pocket.pos) < Ball.pockdist2:
			self.collide_pocket()
			return True
		else:
			return False
				
	def collide_pocket(self):
		vol = pocketed_vol_min + \
		(pocketed_vol_max - wall_vol_min) * self.speed / Ball.max_vel
		vol = min([1, vol])
		vol = max([0, vol])
		if self.num == 0 and (game_state is 'arcade'):
			Hand.score += 1
			self.pos = list(head)
			self.vel = [0, 0]
			self.speed = 0
			self.acc = [0, 0]
			self.ang = [2 * math.pi * random.random() for i in range(2)]
			occupied = True
			while occupied:
				occupied = False
				for ball in balls:
					if ball.num > 0:
						occupied = \
						occupied or dist2(self.pos, ball.pos) < Ball.diam2
				if occupied:
					self.pos[0] += Ball.rad
					
		else:
			balls.remove(self)
			if self.num == 0:
				if Hand.state != 'over':
					Hand.state = 'placing'
			else:
				Hand.unbroken = False
		if Hand.game_is_over():
			Hand.state = 'over'
			if Hand.score_is_new_highscore() and game_state == 'arcade':
				Hand.need_name = True
				
		pocketed_sound.rewind()
		pocketed_sound.set_volume(vol)
		pocketed_sound.play()
			
	def collide_check_wall(self, wall):
		collided = False
		if wall.vertical:
			x = self.pos[0] - wall.ends[0][0]
			if wall.norm[0] * x < Ball.rad:
				if (self.pos[1] < wall.ends[0][1]) != \
				(self.pos[1] < wall.ends[1][1]):
					delta_v_mag = -self.vel[0] * wall.norm[0]
					if delta_v_mag > 0:
						self.pos[0] = \
						wall.ends[0][0] + wall.norm[0] * Ball.rad
						self.vel[0] = -self.vel[0]
						self.vel = mul((1 - Ball.wall_collide_loss), self.vel)
						self.speed *= (1 - Ball.wall_collide_loss)
						if self.speed > 0:
							self.acc = \
							mul(-Ball.friction / self.speed, self.vel)
							self.ang[0] = math.atan2(-self.vel[0], self.vel[1])
						else:
							self.acc = [0, 0]
						collided = True
						
		elif wall.horizontal:
			y = self.pos[1] - wall.ends[0][1]
			if wall.norm[1] * y < Ball.rad:
				if (self.pos[0] < wall.ends[0][0]) != \
				(self.pos[0] < wall.ends[1][0]):
					delta_v_mag = -self.vel[1] * wall.norm[1]
					if delta_v_mag > 0:
						self.pos[1] = \
						wall.ends[0][1] + wall.norm[1] * Ball.rad
						self.vel[1] = -self.vel[1]
						self.vel = mul((1 - Ball.wall_collide_loss), self.vel)
						self.speed *= (1 - Ball.wall_collide_loss)
						if self.speed > 0:
							self.acc = \
							mul(-Ball.friction / self.speed, self.vel)
							self.ang[0] = math.atan2(-self.vel[0], self.vel[1])
						else:
							self.acc = [0, 0]
						collided = True
						
		else:
			v1 = sub(self.pos, wall.ends[0])
			if dot(v1, wall.norm) < Ball.rad:
				v2 = sub(self.pos, wall.ends[1])
				if (dot(v1, wall.line) < 0) != (dot(v2, wall.line) < 0):
					delta_v_mag = -dot(self.vel, wall.norm)
					if delta_v_mag > 0:
						self.backtrack()
						delta_v = mul(2 * delta_v_mag, wall.norm)
						self.vel = add(self.vel, delta_v)
						self.vel = mul((1 - Ball.wall_collide_loss), self.vel)
						self.speed = (1 - Ball.wall_collide_loss) * self.speed
						if self.speed > 0:
							self.acc = \
							mul(-Ball.friction / self.speed, self.vel)
							self.ang[0] = math.atan2(-self.vel[0], self.vel[1])
						else:
							self.acc = [0, 0]
						collided = True
		if collided:
			wall_collide_sound.rewind()
			vol = wall_vol_min + \
			(wall_vol_max - wall_vol_min) * delta_v_mag / Ball.max_vel
			vol = min([1, vol])
			vol = max([0, vol])
			wall_collide_sound.set_volume(vol)
			wall_collide_sound.play()
						
		return collided
	
	def collide_check_ball(self, ball):
		if dist2(self.pos, ball.pos) < Ball.diam2:
			return self.collide_ball(ball)
		else:
			return False
			
	def collide_ball(self, ball):
		collided = False
		center_line = sub(ball.pos, self.pos)
		relative_vel = sub(self.vel, ball.vel)
		center_unit = unit(center_line)
		delta_v_mag = dot(relative_vel, center_unit)
		if delta_v_mag > 0:
			self.backtrack(0.5)
			ball.backtrack(0.5)
			center_line = sub(ball.pos, self.pos)
			relative_vel = sub(self.vel, ball.vel)
			center_unit = unit(center_line)
			delta_v_mag = dot(relative_vel, center_unit)
			
			middle = mul(0.5, add(self.pos, ball.pos))
			self.pos = sub(middle, mul(Ball.rad, center_unit))
			ball.pos = add(middle, mul(Ball.rad, center_unit))
			
			delta_v = mul(delta_v_mag, center_unit)
			self.vel = sub(self.vel, delta_v)
			self.vel = mul((1 - Ball.ball_collide_loss), self.vel)
			self.speed = mag(self.vel)
			if self.speed > 0:
				self.acc = mul(-Ball.friction / self.speed, self.vel)
				self.ang[0] = math.atan2(-self.vel[0], self.vel[1])
			else:
				self.acc = [0, 0]
			ball.vel = add(ball.vel, delta_v)
			ball.vel = mul((1 - Ball.ball_collide_loss), ball.vel)
			ball.speed = mag(ball.vel)
			if ball.speed > 0:
				ball.acc = mul(-Ball.friction / ball.speed, ball.vel)
				ball.ang[0] = math.atan2(-ball.vel[0], ball.vel[1])
			else:
				ball.acc = [0, 0]
			ball_collide_sound.rewind()
			vol = ball_vol_min + \
			(ball_vol_max - wall_vol_min) * delta_v_mag / Ball.max_vel
			vol = min([1, vol])
			vol = max([0, vol])
			ball_collide_sound.set_volume(vol)
			ball_collide_sound.play()
			collided = True
		return collided
					
class Hand:
	max_len = 20 * PPI
	max_len2 = max_len * max_len
	
	cue_img_url = 'https://i.imgur.com/5qMvSSR.png'
	cue_img = simplegui.load_image(cue_img_url)
	cue_img_w_h = [800, 23]
	cue_img_w_h = [1165, 33]
	cue_img_ctr = [dim / 2 for dim in cue_img_w_h]
	
	cue_w_h = [58 * PPI, 1.6675 * PPI]
	
	states = ['aiming', 'dragging', 'striking', 'waiting', 'placing', 'over']
	state = 'aiming'
	drag_end = None
	drag_start = None
	unbroken = True
	strike_step = 0.0
	strike_res = 3
	
	score_pos = [20 * PPI, 4 * PPI]
	score_size = 3 * PPI
	score = 0
	score_name = ''
	need_name = False
	
	def game_is_over():
		if game_state == 'arcade':
			is_over = ((len(balls) == 1) and balls[0].num == 0) or \
			(len(balls) == 0)
		elif game_state == '8ball':
			is_over = True
			for ball in balls:
				if ball.num == 8:
					is_over = False
		return is_over
					
	
	def place(pos):
		pos = constrain_to_table(pos)
		if Hand.unbroken:
			pos = constrain_to_kitchen(pos)
		pos_available = True
		for ball in balls:
			if ball.num > 0:
				pos_available = \
				pos_available and (dist2(pos, ball.pos) > Ball.diam2)
		if pos_available:
			if balls[0].num != 0:
				balls.insert(0, Ball(0, pos))
			else:
				balls[0].pos = pos
		return pos_available
	
	def click(pos):
		busy = False
		if Hand.state != 'over':
			if Hand.state == 'placing' and not physics_timer.is_running():
				placed = Hand.place(pos)
				busy = True
				if placed:
					Hand.state = 'aiming'
			elif Hand.state == 'dragging':
				Hand.drag_end = pos
				busy = True
				Hand.state = 'aiming'
		return busy
	
	def drag(pos):
		if Hand.state != 'over':
			if Hand.state == 'placing' and not physics_timer.is_running():
				Hand.place(pos)
			elif Hand.state == 'aiming':
				Hand.drag_start = pos
				Hand.state = 'dragging'
			elif Hand.state == 'dragging':
				Hand.drag_end = pos
			
	def shoot():
		if Hand.drag_end:
			vector = sub(Hand.drag_start, Hand.drag_end)
			if mag2(vector) > Hand.max_len2:
				vector = mul(Hand.max_len, unit(vector))
			Hand.state = 'striking'
			Hand.strike_vector = vector
			Hand.drag_end = None
			
	def strike():
		balls[0].vel = mul(Ball.max_vel / Hand.max_len, Hand.strike_vector)
		balls[0].speed = mag(balls[0].vel)
		if balls[0].speed > 0:
			balls[0].acc = mul(-Ball.friction / balls[0].speed,
			                   balls[0].vel
			                   )
			balls[0].ang[0] = math.atan2(-balls[0].vel[0], balls[0].vel[1]) 
		else:
			balls[0].acc = [0, 0]
		ball_collide_sound.rewind()
		vol = ball_vol_min + \
		(ball_vol_max - wall_vol_min) * balls[0].speed / Ball.max_vel
		vol = min([1, vol])
		vol = max([0, vol])
		ball_collide_sound.set_volume(vol)
		ball_collide_sound.play()
		if game_state == 'arcade':
			Hand.score += 1
			Hand.state = 'aiming'
		elif game_state == '8ball':
			Hand.state = 'waiting'
		physics_timer.start()
		
	def score_is_new_highscore():
		return Hand.score < max(scores)
		
	def update_highscores():
		if Hand.score < max(scores):
			scores.remove(max(scores))
			scores.append(Hand.score)
			scores.sort()
			i = scores.index(Hand.score)
			while (i < len(scores) - 1) and (scores[i+1] == scores[i]):
				i += 1
			temp = Hand.score_name
			for j in range(i, len(scores)):
				another_temp = score_names[j]
				score_names[j] = temp
				temp = another_temp
			for i in range(3):
				buttons['highscores'][i] = Button(str(score_names[i]) + ': ' +
				                                  str(scores[i]),
				                                  btn_pos[3 + i],
				                                  goto_highscores, 3 * PPI,
				                                  color = score_color,
				                                  bg_color = trim_color
				                                  )
	
	def draw(canvas):
		if game_state == 'arcade':
			canvas.draw_text('Shots taken: ' + str(Hand.score), Hand.score_pos,
			                 Hand.score_size, score_color
			                 )
		if Hand.drag_end:
			vector = sub(Hand.drag_start, Hand.drag_end)
			if mag2(vector) > Hand.max_len2:
				vector = mul(Hand.max_len, unit(vector))
			canvas.draw_line(balls[0].pos,
			                 add(balls[0].pos, mul(cheat, vector)),
			                 1, score_color
			                 )
			x = mag(vector)
			vector = mul(x / 2 + Hand.cue_w_h[0] / 2 + Ball.rad,
			             unit(vector)
			             ) ###
			cue_center = sub(balls[0].pos, vector)
			angle = math.atan2(vector[1], vector[0])
			canvas.draw_image(Hand.cue_img, Hand.cue_img_ctr, Hand.cue_img_w_h,
			                  cue_center, Hand.cue_w_h, angle)
		if Hand.state == 'striking':
			Hand.strike_step += 1
			vector = mul(Hand.cue_w_h[0] / 2 + Ball.rad,
			             unit(Hand.strike_vector)
			             )
			vector = add(vector,
			             mul(0.5 - Hand.strike_step / Hand.strike_res / 2.0,
			                 Hand.strike_vector
			                 )
			             )
			cue_center = sub(balls[0].pos, vector)
			angle = math.atan2(vector[1], vector[0])
			canvas.draw_image(Hand.cue_img, Hand.cue_img_ctr, Hand.cue_img_w_h,
			                  cue_center, Hand.cue_w_h, angle)
			if Hand.strike_step >= Hand.strike_res:
				Hand.strike_step = 0.0
				Hand.strike()
		if Hand.state == 'over':
			text_pos = add(center, mul(PPI, [-15, 2.5]))
			canvas.draw_text('GAME OVER', text_pos, 5 * PPI, score_color)
			if Hand.need_name:
				grats_pos = add(text_pos, mul(PPI, [0, 3.5]))
				enter_pos = add(grats_pos, mul(PPI, [7, 2.5]))
				name_pos = add(enter_pos, mul(PPI, [4, 4]))
				canvas.draw_text('Congratulations! You got a high score!',
				                 grats_pos, 2 * PPI, score_color
				                 )
				canvas.draw_text('Enter your initials:', enter_pos, 2 * PPI,
				                 score_color
				                 )
				canvas.draw_text(Hand.score_name, name_pos, 3 * PPI,
				                 score_color
				                 )

###############################################################################
#   DEFINE EVENT HANDLERS   #
###############################################################################
			
def physics_update():
	any_moving = False
	for ball in balls:
		ball.advance()
		any_moving = any_moving or ball.speed > 0
		
		if ball.pos[0] < checking_boundaries[0][0]:
			x_pos = 0
		elif ball.pos[0] < checking_boundaries[0][1]:
			x_pos = 1
		elif ball.pos[0] < checking_boundaries[0][2]:
			x_pos = 2
		else:
			x_pos = 3
			
		if ball.pos[1] < checking_boundaries[1][0]:
			y_pos = 0
		elif ball.pos[1] < checking_boundaries[1][1]:
			y_pos = 1
		else:
			y_pos = 2
		
		[ball.collide_check_pocket(pocket)
		 for pocket in pockets_to_check[y_pos][x_pos]
		 ]
		[ball.collide_check_wall(wall)
		 for wall in walls_to_check[y_pos][x_pos]
		 ]
		[ball.collide_check_corner(corner)
		 for corner in corners_to_check[y_pos][x_pos]
		 ]
		
		for other in balls:
			if other.num < ball.num:
				ball.collide_check_ball(other)
			
	if not any_moving:
		physics_timer.stop()
		if Hand.state == 'waiting':
			Hand.state = 'aiming'
		
text1_ul = [15 * PPI, 8 * PPI]
text1_size = 1.8 * PPI
text1 = ['	Controls:', '',
         'Click and drag back anywhere',
         'on the screen as if you are pulling',
         'back the cue stick. The shot will not',
         'be taken until you click the SPACEBAR',
         'to finalize your shot.',
         '',
         'In 8 Ball mode, click the "place"',
         'button to move the cue ball around the',
         'board. Simply drag your cursor around and',
         'once you release, the cue ball will',
         'remain in place.',
         '',
         'Up and Down arrow keys control',
         'soundtrack volume.'
         ]
text2_ul = [55 * PPI, 8 * PPI]
text2_size = 1.8 * PPI
text2 = ['	How To Play Arcade Mode:',
         '',
         'The objective of arcade mode is to sink',
         'all of the object balls (non-white balls)',
         'using as few shots as possible. This is a',
         'single player game.',
         '',
         '	How To Play 8 Ball Pool:',
         '',
         'There are many ways to play 8 Ball.',
         'Almost everyone you meet plays with',
         'a slightly different rule set, so',
         "I've left most of the rules up to you--",
         'the game does not enforce them. For',
         'example, you may pick up the cue ball',
         'and move it after any turn.'
        ]
texts = [[text1, text1_ul, text1_size], [text2, text2_ul, text2_size]]

def draw(canvas):
	canvas.draw_polygon(table_rectangle, 1, border_color, border_color)
	canvas.draw_polygon(corners, 1, cloth_color, cloth_color)
	for poly in look_good_polys:
		canvas.draw_polygon(poly, 1, trim_color, trim_color)
#	canvas.draw_circle(head, 0.25 * PPI, 1, 'black', 'black')
#	canvas.draw_circle(foot, 0.25 * PPI, 1, 'black', 'black')
	[pocket.draw(canvas) for pocket in pockets]
	[button.draw(canvas) for button in buttons[game_state]]
	if gameplay_mode():
		[ball.draw(canvas) for ball in balls]
		Hand.draw(canvas)
#	[page.draw(canvas) for page in textpages[game_state]]
#	[wall.draw(canvas) for wall in walls]
	if game_state == 'how2':
		for text in texts:
			for i in range(len(text[0])):
				canvas.draw_text(text[0][i],
				                 add(text[1], [0, text[2] * 1.5 * i]),
				                 text[2], score_color
				                 )
	
def click(pos):
	handed = False
	if gameplay_mode():
		handed = Hand.click(pos)
	if not handed:
		for button in buttons[game_state]:
			button.click(pos)

def drag(pos):
	if gameplay_mode():
		Hand.drag(pos)

simplegui.KEY_MAP['backspace'] = 8
simplegui.KEY_MAP['enter'] = 13
		
def keydown(key):
	global current_soundtrack_vol, current_soundtrack_max_vol
	if key == simplegui.KEY_MAP['up']:
		current_soundtrack_vol += current_soundtrack_max_vol / 10.0
	if key == simplegui.KEY_MAP['down']:
		current_soundtrack_vol -= current_soundtrack_max_vol / 10.0
	current_soundtrack_vol = constrain(current_soundtrack_vol, 0,
	                                   current_soundtrack_max_vol
	                                   )
	current_soundtrack.set_volume(current_soundtrack_vol)
	
	if game_state == 'arcade' and Hand.state == 'over' and Hand.need_name:
		if key == simplegui.KEY_MAP['backspace'] and len(Hand.score_name) > 0:
			Hand.score_name = Hand.score_name[:-1]
		elif key >= simplegui.KEY_MAP['a'] and \
		key <= simplegui.KEY_MAP['z'] and \
		len(Hand.score_name) < 3:
			Hand.score_name += chr(key)
		elif key == simplegui.KEY_MAP['enter'] and len(Hand.score_name) > 0:
			Hand.update_highscores()
			Hand.need_name = False
			goto_highscores()
	elif shortcuts_on:
		if game_state == '8ball':
			if key == simplegui.KEY_MAP['r']:
				goto_8ball()
			elif key == simplegui.KEY_MAP['p']:
				place_ball()
		elif game_state == 'arcade':
			if key == simplegui.KEY_MAP['r']:
				goto_arcade()
		elif game_state == 'menu':
			if key == simplegui.KEY_MAP['h']:
				goto_highscores()
			elif key == simplegui.KEY_MAP['s']:
				goto_settings()
			elif key == simplegui.KEY_MAP['p']:
				goto_how2()
		if key == simplegui.KEY_MAP['m']:
			goto_menu()
	if gameplay_mode() and Hand.state in ['aiming', 'dragging']:
		if key == simplegui.KEY_MAP['space']:
			Hand.shoot()
 
def keyup(key):
	pass

###############################################################################
#   GET THINGS ROLLING   #
###############################################################################

def initialize():
	global table_dims, border, frame_dims, center, head, foot, \
	       table_rectangle, corners, walls, pockets, look_good_polys, \
	       border_color, cloth_color, trim_color, shortcuts_on, \
	       frame, btn_pos, buttons, textpages, physics_timer, \
	       score_color, scores, score_names, \
	       checking_boundaries, walls_to_check, corners_to_check, \
	       pockets_to_check, pi, cheat, soundtrack_timer
			
	pi = math.pi
	cheat = 1.5
	
	#table_dims = mul(PPI, [76, 38])
	table_dims = mul(PPI, [92, 46])
	border = 5 * PPI
	frame_dims = add(table_dims, mul(2, [border, border]))
	center = mul(0.5, frame_dims)
	head = add([border, border], [table_dims[0]/4, table_dims[1]/2])
	foot = add(head, [table_dims[0]/2, 0])
	
	table_rectangle = rectangle(center, frame_dims)
	frame_dims[1] += border
	
	corners = [add([border, border], [table_dims[0] * i, table_dims[1] * j])
	           for j in [0, 1] for i in [0, 1]
	           ]
	corners[2], corners[3] = corners[3], corners[2]
	p_or = 1.25 * Pocket.rad
	p_h = (math.sqrt(2)-1) * Pocket.rad
	p_r = Pocket.rad
	
	p_os = p_or * math.sqrt(2)
	p_l = (p_h + p_r) / math.sqrt(2)
	p_u = (p_h - p_r) / math.sqrt(2) + p_os
	corners = [add(corners[0], [0, p_os]), add(corners[0], [p_os, 0]),
	           add(corners[1], [-p_os, 0]), add(corners[1], [0, p_os]),
	           add(corners[2], [0, -p_os]), add(corners[2], [-p_os, 0]),
	           add(corners[3], [p_os, 0]), add(corners[3], [0, -p_os]),
	           ]
	corners = [corners[0], add(corners[0], [-p_l, -p_u]),
	           add(corners[1], [-p_u, -p_l]), corners[1],
	           corners[2], add(corners[2], [p_u, -p_l]),
	           add(corners[3], [p_l, -p_u]), corners[3],
	           corners[4], add(corners[4], [p_l, p_u]),
	           add(corners[5], [p_u, p_l]), corners[5],
	           corners[6], add(corners[6], [-p_u, p_l]),
	           add(corners[7], [-p_l, p_u]), corners[7],
	           ]
	
	s_or = 1.25 * Pocket.rad
	s_h = Pocket.rad
	s_r = Pocket.rad
	s_c_t = [border + table_dims[0]/2, border]
	s_c_b = add(s_c_t, [0, table_dims[1]])
	corners.insert(12, add(s_c_b, [-s_or, 0]))
	corners.insert(12, add(s_c_b, [-s_r, s_h]))
	corners.insert(12, add(s_c_b, [s_r, s_h]))
	corners.insert(12, add(s_c_b, [s_or, 0]))
	corners.insert(4, add(s_c_t, [s_or, 0]))
	corners.insert(4, add(s_c_t, [s_r, -s_h]))
	corners.insert(4, add(s_c_t, [-s_r, -s_h]))
	corners.insert(4, add(s_c_t, [-s_or, 0]))
	
	walls = [Wall([corners[i], corners[(i+1)%len(corners)]])
	         for i in range(len(corners))
	         ]
	walls.pop(21)
	walls.pop(17)
	walls.pop(13)
	walls.pop(9)
	walls.pop(5)
	walls.pop(1)
	
	pocket_pos = [mul(0.5, add(corners[1], corners[2])),
	              mul(0.5, add(corners[5], corners[6])),
	              mul(0.5, add(corners[9], corners[10])),
	              mul(0.5, add(corners[13], corners[14])),
	              mul(0.5, add(corners[17], corners[18])),
	              mul(0.5, add(corners[21], corners[22]))
	              ]
	pockets = [Pocket(pos) for pos in pocket_pos]
	
	look_good_polys = [[corners[(i+2+j*4)%24] for i in range(4)]
	                   for j in range(6)
	                   ]
	
	border_color = 'saddlebrown'
	cloth_color = 'darkgreen'
	trim_color = 'green'
	shortcuts_on = True
	score_color = 'black'
	
	frame = simplegui.create_frame('SimPool', *frame_dims)
	
	btn_cntr = add(center, [0, table_dims[1]/2 + 1.5 * border])
	btn_lft = add(head, [0, table_dims[1]/2 + 1.5 * border])
	btn_rgt = add(foot, [0, table_dims[1]/2 + 1.5 * border])
	btn_cntr1 = add(center, [0, table_dims[1]/4])
	btn_lft1 = add(head, [0, table_dims[1]/4])
	btn_rgt1 = add(foot, [0, table_dims[1]/4])
	btn_pos = [head, center, foot, btn_lft1, btn_cntr1, btn_rgt1, btn_lft,
	           btn_cntr, btn_rgt
	           ]
	buttons = {'menu':[Button('SimPool', btn_pos[1], goto_menu, 5 * PPI,
	                          color = score_color, bg_color = trim_color
	                          ),
					   Button('Play 8 Ball Pool',
							  [(btn_pos[3][0] + btn_pos[4][0])/2,
							   btn_pos[3][1]
							   ], goto_8ball,
							  color = score_color, bg_color = trim_color
							  ),
					   Button('Play Arcade Mode',
							  [(btn_pos[4][0] + btn_pos[5][0])/2,
							   btn_pos[4][1]
							   ], goto_arcade,
							  color = score_color, bg_color = trim_color
							  ),
					   Button('(H)ighscores', btn_pos[6], goto_highscores),
					   Button('(S)ettings', btn_pos[7], goto_settings),
					   Button('How to (P)lay', btn_pos[8], goto_how2)
					   ],
			   '8ball':[Button('(M)enu', btn_pos[7], goto_menu),
						Button('(R)eset', btn_pos[6], goto_8ball),
						Button('(P)lace cue ball', btn_pos[8], place_ball)
						],
			   'arcade':[Button('(M)enu', btn_pos[7], goto_menu),
						Button('(R)eset', btn_pos[6], goto_arcade)
						],
			   'settings':[Button('Swap color scheme', btn_pos[4],
								  swap_colors,
								  color = score_color, bg_color = trim_color
								  ),
						   Button('Keyboard shortcuts enabled',
								  btn_pos[3], swap_shortcuts,
								  color = score_color, bg_color = trim_color
								  ),
						   Button('Normal length cue ball vector',
								  btn_pos[5], swap_cheat,
								  color = score_color, bg_color = trim_color
								  ),
						   Button('(M)enu', btn_pos[7], goto_menu)
						   ],
			   'highscores':[None, None, None,
							 Button('(M)enu', btn_pos[7], goto_menu)
							 ],
			   'how2':[Button('(M)enu', btn_pos[7], goto_menu)]
			   }
	
	for i in range(3):
		buttons['highscores'][i] = Button('WHT: 999',
										  btn_pos[3 + i],
										  goto_highscores, 3 * PPI,
										  color = score_color,
										  bg_color = trim_color
										  )
	
#	textpages = {'menu':[TextPage('SimPool', [35 * PPI, 25 * PPI], 40)],
#				 'speed':[],
#				 'settings':[],
#				 'highscores':[],
#				 'how2':[]
#				 }
	
	physics_timer = simplegui.create_timer(11, physics_update)
	
	scores = [999, 999, 999]
	score_names = ['WHT', 'WHT', 'WHT']
	
	checking_boundaries = [[border + 2 * Ball.rad, center[0],
							table_dims[0] - border - 2 * Ball.rad
							],
						   [border + 2 * Ball.rad,
							table_dims[1] - border - 2 * Ball.rad
							]
						   ]
	
	walls_to_check = [[[walls[17], walls[0], walls[1], walls[2]],
					   [walls[1], walls[2], walls[3]],
					   [walls[4], walls[5], walls[6]],
					   [walls[5], walls[6], walls[7], walls[8]]
					   ],
					  [[walls[15], walls[16], walls[17], walls[0], walls[1]],
					   [], [],
					   [walls[6], walls[7], walls[8], walls[9], walls[10]]
					   ],
					  [[walls[14], walls[15], walls[16], walls[17]],
					   [walls[13], walls[14], walls[15]],
					   [walls[10], walls[11], walls[12]],
					   [walls[8], walls[9], walls[10], walls[11]]
					   ]
					  ]
	
	corners_to_check = [[[corners[0], corners[3]], [corners[3], corners[4]],
						 [corners[7], corners[8]], [corners[8], corners[11]]
						 ],
						[[corners[23], corners[0]], [], [],
						 [corners[11], corners[12]]
						 ],
						[[corners[20], corners[23]],
						 [corners[19], corners[20]],
						 [corners[15], corners[16]], [corners[12], corners[15]]
						 ]
						]
	
	pockets_to_check = [[[pockets[0]], [pockets[1]], [pockets[1]],
						 [pockets[2]]
						 ],
						[[], [], [], []],
						[[pockets[5]], [pockets[4]], [pockets[4]],
						 [pockets[3]]
						 ]
						]
		
	frame.set_canvas_background('white')
	frame.set_draw_handler(draw)
	frame.set_mouseclick_handler(click)
	frame.set_mousedrag_handler(drag)
	frame.set_keydown_handler(keydown)
	frame.set_keyup_handler(keyup)
	
	soundtrack_timer = simplegui.create_timer(current_soundtrack_time,
	                                          restart_soundtrack
	                                          )
	soundtrack_timer.start()
	current_soundtrack.rewind()
	current_soundtrack.set_volume(current_soundtrack_vol)
	current_soundtrack.play()
	
initialize()

frame.start()
