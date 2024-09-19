import pygame, sys
import os
from pygame.math import Vector2 as vector
from os.path import join
from random import randint,choice
pygame.init()
os.environ["SDL_VIDEO_CENTERED"]="1"
info =pygame.display.Info()
WINDOW_WIDTH, WINDOW_HEIGHT = info.current_w,info.current_h
TILE_SIZE = 64
ANIMATION_SPEED = 6

# layers 
Z_LAYERS = {
	'bg': 0,
	'clouds': 1,
	'bg tiles': 2,
	'path': 3,
	'bg details': 4,
	'main': 5,
	'water': 6,
	'fg': 7
}
