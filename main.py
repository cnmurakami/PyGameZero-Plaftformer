import pgzrun
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pgzero.builtins import sounds, clock
from classes import Player, Enemy, Floor
from pygame import Rect
from settings import *
import global_variables as g
import pygame

pygame.display.set_caption("My Game Window")

# ----------- BACKGROUND ------------

background = []
background_tile_size = 256
with open ('background.txt', 'r') as file:
    for l in file.readlines():
        background.append(l.strip())

background_dict = {
    't': 'sprites/backgrounds/background_solid_cloud',
    'b': 'sprites/backgrounds/background_color_hills'
}

def define_boundaries():
    g.limit_x = len(background[0])*background_tile_size
    g.limit_y = len(background)*background_tile_size
    print(f'x: {g.limit_x}')
    print(f'y: {g.limit_y}')
    return

def build_background():

    for i in range(len(background)):
        for j in range(len(background[i])):
            screen.blit(
                background_dict[background[i][j]],
                (
                    j * background_tile_size + g.offset_x,
                    i * background_tile_size + g.offset_y
                )
            )
    return

# ------------ MAP LAYOUT ---------------

for i in range(-100, 100):
    enemy = Enemy('sprites/enemies/frog', (i*256, HEIGHT - g.tile_size*1.5))
    floor = Floor('sprites/tiles/terrain_grass_block_top', (i*g.tile_size, HEIGHT-g.tile_size/2))
for i in range(0, 10):
    floor = Floor('sprites/tiles/terrain_grass_block_top', (i*g.tile_size, HEIGHT-(g.tile_size/2*5)))

# ------------ GENERAL METHODS ----------

def offset_actors():
    for actor in g.world_objects['enemies']:
        actor.x -= g.offset_x
        actor.y -= g.offset_y
    for geometry in g.world_objects['tiles']:
        geometry.x -= g.offset_x
        geometry.y -= g.offset_y
    g.offset_y, g.offset_x = 0, 0
    return

# ----------- ENGINE -------------

define_boundaries()
player = Player('sprites/characters/right/character_purple', (WIDTH/2, HEIGHT-g.tile_size*2))
g.global_player_x, g.global_player_y = player.pos

def on_mouse_down(pos):
    if DEBUG:
        for item in g.world_objects['tiles']:
            if item.collidepoint(pos):
                print(item)
                g.world_objects['tiles'].remove(item)

def on_key_down(key):
    if key == keys.P:
        g.paused = not g.paused
    elif key == keys.SPACE and DEBUG:
        g.step = True
    if key == keys.W:
        player.jump()

def update(dt):
    if g.paused and not g.step:
        return
    g.delta_time = dt
    g.frame_timer += g.delta_time
    if g.frame_timer >= g.frame_delay:
        g.frame_timer = 0
        player.frame_index_idle = (player.frame_index_idle + 1) % 4
        player.frame_index_move = (player.frame_index_move + 1) % 2
    
    player.update()
    
    if keyboard.d:
        player.move('r')
    if keyboard.a:
        player.move('l')
    if DEBUG:
        if keyboard.right:
            g.offset_x+=10
            player.pos = (WIDTH/2, HEIGHT/2)
        if keyboard.left:
            g.offset_x-=10
            player.pos = (WIDTH/2, HEIGHT/2)
        if keyboard.up:
            g.offset_y-=10
            player.pos = (WIDTH/2, HEIGHT/2)
        if keyboard.down:
            g.offset_y+=10
            player.pos = (WIDTH/2, HEIGHT/2)
        g.step = False

    offset_actors()


def draw():
    screen.clear()
    build_background()
    for actor in g.world_objects['tiles']:
        actor.draw()
    for actor in g.world_objects['enemies']:
        actor.draw()
    player.draw()
    if DEBUG:
        screen.draw.text(f'limit: ({g.limit_x}, {g.limit_y})', (10, 10), color = 'black', background=(255,255,255))
        screen.draw.text(f'Player POS SCREEN: {player.pos}', (10, 30), color = 'black', background=(255,255,255))
        screen.draw.text(f'Player POS GLOBAL: {(g.global_player_x, g.global_player_y)}', (10, 50), color = 'black', background=(255,255,255))
        screen.draw.text(f'Facing Right: {player.facing_right}', (10, 70), color = 'black', background=(255,255,255))
        if player.grounded:
            screen.draw.text(f'GROUNDED: {player.grounded}', (10, 90), color = 'black', background=(255,255,255))
        else:
            screen.draw.text(f'GROUNDED: {player.grounded}', (10, 90), color = 'red', background=(255,255,255))
        screen.draw.rect(player.get_rect(), 'red')
        for obj in g.world_objects['tiles']:
            screen.draw.rect(obj.get_rect(g.offset_x), 'green')
