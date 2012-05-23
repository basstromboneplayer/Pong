#!/usr/bin/python

import pygame
from pygame.locals import *
from socket_handler import Socket_Handler
import zipfile, shutil, os

def reset_game(ball, paddle):
	ball.rect = ball.image.get_rect()
	ball.rect.topleft = [25, 25]
	ball.xpos = 25
	ball.ypos = 25
	ball.yvel = 2
	ball.xvel = 5
	paddle.ypos = 0
	paddle2.ypos = 0

	paddle.rect = paddle.image.get_rect() # use image extent values
	paddle.rect.topleft = [0, 0] # put the ball in the top left corner
	paddle2.rect = paddle2.image.get_rect()
	paddle2.rect.topright = [width, 0]

def check_ball_collision(ball, paddle):
	if(ball.rect.colliderect(paddle.rect)):
		ball.xvel = -ball.xvel
		ball.xpos += ball.xvel

def check_ball_offscreen(ball):
	if(ball.rect.topleft[0] < 0):
		#ball left the screen
		reset_game(ball, paddle)
		return

	# Check to see if ball leaves the screen
	#print ball.rect.bottomright[1], ball.rect.topleft[1]
	if(ball.rect.bottomright[1] > height or ball.rect.topleft[1] < 0):
		ball.yvel = -ball.yvel
		ball.ypos += ball.yvel
		print 'reverse direction %d %d' % (ball.yvel, ball.ypos)
	if(ball.rect.bottomright[0] > width or ball.rect.topleft[0] < 0):
		ball.xvel = -ball.xvel
		ball.xpos += ball.xvel

def update_computer_position(ball, computer_paddle):
	# Get middle of paddle

	paddle_mid_y = computer_paddle.rect.topleft[1] + (computer_paddle.rect.bottomright[1] - computer_paddle.rect.topleft[1]) / 2
	ball_mid_y = ball.rect.topleft[1] + (ball.rect.bottomright[1] - ball.rect.topleft[1]) / 2
	#print computer_paddle.rect.topleft[1], computer_paddle.rect.bottomright[1], mid_y
	difference = abs(paddle_mid_y - ball_mid_y)
	difference = min(difference, 5)
	if paddle_mid_y > ball_mid_y:
		computer_paddle.ypos += -difference
	else:
		computer_paddle.ypos += difference



def download_asset_list(s):
	s.send_packet('LIST')
	data = s.decode_packet(s.receive_packet())

	if	data[0:5] != 'ERROR':
		return data
	else:
		print data	# you have an error message from the server

def download_file(s,filename):
	s.send_packet('FILE ' + filename)
	data = s.receive_packet()

	if	data[0:5] != 'ERROR':
		# save the file
		f = open(filename,'wb')
		f.write(data)
		f.close()
	else:
		print data	# you have an error message from the server

def unzip_file(filename):
	zfile = zipfile.ZipFile(filename, 'r')
	for fname in zfile.namelist():
		if fname.endswith('/'):
			os.makedirs(fname)
		else:
			# decompress each file's data
			data = zfile.read(fname)

			# save the decompressed data to a new file
			fout = open(fname, "w")
			fout.write(data)
			fout.close()
			print "New file created --> %s" % fname
			print '-'*40
	
	# delete zip
	if os.path.isfile(filename):
		os.remove(filename)

def clean_dir():
	assets = ['ball.png', 'paddle.png', 'assets.zip', 'temp.txt']
	
	# remove individual assets
	for fname in assets:
		if os.path.isfile(fname):
			os.remove(fname)

	# remove assets directory
	fname = 'assets/'
	if os.path.isdir(fname):
		shutil.rmtree(fname)








width  = 320
height = 240
size   = [width, height]
pygame.init()
screen = pygame.display.set_mode(size)
background = pygame.Surface(screen.get_size())


# always start with no assets
clean_dir()

#######################################
# 3 different modes for getting assets
#######################################

s = Socket_Handler('localhost', 30000, 'client')
s.create()

# 0 - Download each asset individually
# 1 - Download a zip file and extract assets
# 2 - Download an asset list and download each asset as needed

download_method = 0



# Method 1: Download each asset individually
if download_method == 0:
	ball_img = 'ball.png'
	paddle_img = 'paddle.png'
	download_file(s, ball_img)
	download_file(s, paddle_img)

# Method 2: Download a single zip file from the server and extract the assets locally
elif download_method == 1:
	ball_img = 'assets/ball.png'
	paddle_img = 'assets/paddle.png'
	zfile = 'assets.zip'
	download_file(s, zfile)
	unzip_file(zfile)

# Method 3: Download an asset list and download each asset as needed
elif download_method == 2:
	ball_img = 'ball.png'
	paddle_img = 'paddle.png'
	asset_list = download_asset_list(s)
	
	print repr(asset_list)
	
	# Download all assets for now, but should download them as needed
	for fname in asset_list:
		download_file(s, fname)






paddle = pygame.sprite.Sprite() # create sprite
paddle.image = pygame.image.load(paddle_img).convert_alpha() # load ball image

paddle2 = pygame.sprite.Sprite()
paddle2.image = paddle.image


ball = pygame.sprite.Sprite()
ball.image = pygame.image.load(ball_img).convert_alpha()
reset_game(ball, paddle)
screen.blit(ball.image, ball.rect)
screen.blit(paddle.image, paddle.rect)
screen.blit(paddle2.image, paddle2.rect)



#ypos = 0
pygame.display.update()
done = False
while not done:
	# Update ball position
	ball.xpos += ball.xvel
	ball.ypos += ball.yvel
	ball.rect.topleft = [ball.xpos, ball.ypos]
	check_ball_offscreen(ball)
	check_ball_collision(ball, paddle)
	check_ball_collision(ball, paddle2)
	update_computer_position(ball, paddle2)
	#down, up = False, False
	key = pygame.key.get_pressed()
	for event in pygame.event.get():
		if(event.type == pygame.QUIT):
			done = True
	if key[K_UP]:
		paddle.ypos += -5
	if key[K_DOWN]:
		paddle.ypos += 5

	paddle.rect.topleft = [0, paddle.ypos]
	paddle2.rect.topright = [width, paddle2.ypos]
	screen.fill([0, 0, 0])
	screen.blit(ball.image, ball.rect)
	screen.blit(paddle.image, paddle.rect)
	screen.blit(paddle2.image, paddle2.rect)

	pygame.display.update()
	pygame.time.delay(30)