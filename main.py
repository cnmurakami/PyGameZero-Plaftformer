# lib imports
import pgzrun
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pgzero.builtins import sounds, clock
from random import randint
from pygame import Rect

# local imports
from classes import Player, Enemy, Floor, Parallax, Camera
from settings import *
from level_builder import create_level, draw_background
import global_variables as g


# ----------- BACKGROUND ------------

# def define_boundaries(level):
#     with open(f'level_data/level_{level}_layout.txt', 'r') as file:
#         lines = file.readlines()
#         g.limit_x = len(lines[0].strip())*g.tile_size
#         g.limit_y = len(lines)*g.tile_size        
#     print(f'x: {g.limit_x}')
#     print(f'y: {g.limit_y}')
#     return

# def draw_background():
#     for i in range(3, 0, -1):
#         for actor in g.world_objects['parallax'][i]:
#             actor.draw()

# def build_background(level):
#     sprites = []
#     with open (f'level_data/level_{level}_background.txt', 'r') as file:
#         for i in file.readlines():
#             sprites.append(i.strip())
#     print('y-limit:',g.limit_y+g.background_tile_size+1, g.background_tile_size)
#     print(g.limit_y - (g.background_tile_size * 2))
#     for pos_y in range(-g.background_tile_size, g.limit_y+g.background_tile_size+1, g.background_tile_size):
#         for x in range(-g.background_tile_size, g.limit_x+g.background_tile_size+1, g.background_tile_size):
#             if pos_y < 0:
#                 sprite = sprites[0]
#                 parallax = 1
#             elif 0 <= pos_y < g.background_tile_size:
#                 sprite = sprites[1]
#                 parallax = 1
#             elif g.background_tile_size <= pos_y < g.background_tile_size*2:
#                 sprite = sprites[2]
#                 parallax = 2
#             elif g.background_tile_size*2 <= pos_y < g.background_tile_size*3:
#                 sprite = sprites[3]
#                 parallax = 3
#             else:
#                 sprite = sprites[4]
#                 parallax = 3
#             tile = Parallax(sprite, parallax, (x, pos_y))

# # ------------ MAP LAYOUT ---------------

# def get_tile_dict(level):
#     tile_dict = {}
#     with open (f'level_data/level_{level}_tiles.txt', 'r') as file:
#         for line in file.readlines():
#             if len(line.strip())>0:
#                 key, value = line.split("=")
#                 key = key.strip()
#                 value = value.strip()
#                 tile_dict[key] = value
#     return tile_dict


# def create_level(level_number, ground_asset, wall_asset=None) -> Player:
#     tile_dict = get_tile_dict(level_number)

#     with open (f'level_data/level_{level_number}_layout.txt', 'r') as file:
#         block_y = 0
#         for line in file.readlines():
#             line = line.strip()
#             for block_x in range(len(line)):
#                 pos_x = block_x * g.tile_size
#                 pos_y = block_y * g.tile_size
#                 if line[block_x] in tile_dict.keys():
#                     tile = Floor(tile_dict[line[block_x]], (pos_x, pos_y))
#                 elif line[block_x] == 'p':
#                     player = Player('sprites/characters/right/character_purple', (pos_x, pos_y))
#             block_y += 1
#     define_boundaries(level_number)
#     build_background(level_number)
#     return player


player = create_level(1, 'sprites/tiles/terrain_grass_block_top')
print(g.limit_y)
print(g.limit_y - g.tile_size * 1.5)
# for i in range(-100, 100):
#     enemy = Enemy('sprites/enemies/frog', (i*256, g.limit_y - g.tile_size * 1.5))
#     floor = Floor('sprites/tiles/terrain_grass_block_top', (i*g.tile_size, g.limit_y - g.tile_size/2))
# for i in range(10, 100):
#     if i%3 == 0 and i%5 == 0:
#         floor = Floor('sprites/tiles/terrain_grass_block_top', (i*g.tile_size, g.limit_y-(g.tile_size/2*5)))
#         floor = Floor('sprites/tiles/terrain_grass_block_top', (i*g.tile_size, g.limit_y-(g.tile_size/2*10)))



# ------------ GENERAL METHODS ----------


# ----------- ENGINE -------------

#player = Player('sprites/characters/right/character_purple', (WIDTH/3+WIDTH/2, g.limit_y-g.tile_size/2*10))
g.global_player_x, g.global_player_y = player.pos
camera = Camera()

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
    if key == keys.TAB:
        if keyboard.lctrl:
            g.show_osd = not g.show_osd
        else:
            g.show_box = not g.show_box

def update(dt):
    if g.paused and not g.step:
        return
    g.delta_time = dt
    g.frame_timer += g.delta_time
    player.update()
    if keyboard.d:
        player.move('r')
    if keyboard.a:
        player.move('l')
    if DEBUG:
        if keyboard.right:
            camera.can_move_right=True
            g.offset_x-=10
            player.facing_right = True
            player.pos = (WIDTH/2, HEIGHT/2)
        if keyboard.left:
            player.facing_right = False
            camera.can_move_left=True
            g.offset_x+=10
            player.pos = (WIDTH/2, HEIGHT/2)
        if keyboard.up:
            camera.can_move_up=True
            g.offset_y+=10
            player.pos = (WIDTH/2, HEIGHT/2)
        if keyboard.down:
            camera.can_move_down=True
            g.offset_y-=10
            player.pos = (WIDTH/2, HEIGHT/2)
        g.step = False

    camera.update()

def draw():
    screen.clear()
    screen.fill('pink')
    draw_background()
    for actor in g.world_objects['tiles']:
        actor.draw()
    for actor in g.world_objects['enemies']:
        actor.draw()
    player.draw()
    if DEBUG:
        if g.show_osd:
            screen.draw.text(f'limit: ({g.limit_x}, {g.limit_y})', (10, 10), color = 'black', background=(255,255,255))
            screen.draw.text(f'Player POS SCREEN: {player.pos}', (10, 30), color = 'black', background=(255,255,255))
            screen.draw.text(f'Player POS GLOBAL: {(g.global_player_x, g.global_player_y)}', (10, 50), color = 'black', background=(255,255,255))
            screen.draw.text(f'Facing Right: {player.facing_right}, Moving: {player.is_moving}', (10, 70), color = 'black', background=(255,255,255))
            if player.grounded:
                screen.draw.text(f'GROUNDED: {player.grounded}', (10, 90), color = 'black', background=(255,255,255))
            else:
                screen.draw.text(f'GROUNDED: {player.grounded}', (10, 90), color = 'red', background=(255,255,255))
            screen.draw.text(f'CAM Offset: {(camera.offset_x, camera.offset_y)}', (10, 110), color = 'black', background=(255,255,255))
            screen.draw.text(f'CAM Move: L:{str(camera.can_move_left)[:1]}, R:{str(camera.can_move_right)[:1]}, U:{str(camera.can_move_up)[:1]}, D:{str(camera.can_move_down)[:1]}', (10, 130), color = 'black', background=(255,255,255))
        if g.show_box:
            screen.draw.rect(player.get_rect(), 'blue')
            for obj in g.world_objects['tiles']:
                screen.draw.rect(obj.get_rect(g.offset_x), 'green')
            screen.draw.rect(camera.outer_rect, 'purple')
            screen.draw.rect(camera.inner_rect, 'purple')
