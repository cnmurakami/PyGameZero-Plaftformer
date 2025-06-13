from settings import WIDTH, HEIGHT
from pgzero.actor import Actor
from pgzero.builtins import sounds
from pygame import Rect
import global_variables as g
from classes import Player, Enemy, Floor, Parallax, Camera

def define_boundaries(level):
    with open(f'level_data/level_{level}_layout.txt', 'r') as file:
        lines = file.readlines()
        g.limit_x = len(lines[0].strip())*g.tile_size
        g.limit_y = len(lines)*g.tile_size        
    print(f'x: {g.limit_x}')
    print(f'y: {g.limit_y}')
    return

def draw_background():
    for i in range(3, 0, -1):
        for actor in g.world_objects['parallax'][i]:
            actor.draw()

def build_background(level):
    sprites = []
    with open (f'level_data/level_{level}_background.txt', 'r') as file:
        for i in file.readlines():
            sprites.append(i.strip())
    print('y-limit:',g.limit_y+g.background_tile_size+1, g.background_tile_size)
    print(g.limit_y - (g.background_tile_size * 2))
    for pos_y in range(-g.background_tile_size, g.limit_y+g.background_tile_size+1, g.background_tile_size):
        for x in range(-g.background_tile_size, g.limit_x+g.background_tile_size+1, g.background_tile_size):
            if pos_y < 0:
                sprite = sprites[0]
                parallax = 1
            elif 0 <= pos_y < g.background_tile_size:
                sprite = sprites[1]
                parallax = 1
            elif g.background_tile_size <= pos_y < g.background_tile_size*2:
                sprite = sprites[2]
                parallax = 2
            elif g.background_tile_size*2 <= pos_y < g.background_tile_size*3:
                sprite = sprites[3]
                parallax = 3
            else:
                sprite = sprites[4]
                parallax = 3
            tile = Parallax(sprite, parallax, (x, pos_y))


def get_tile_dict(level):
    tile_dict = {}
    with open (f'level_data/level_{level}_tiles.txt', 'r') as file:
        for line in file.readlines():
            if len(line.strip())>0:
                key, value = line.split("=")
                key = key.strip()
                value = value.strip()
                tile_dict[key] = value
    return tile_dict


def create_level(level_number, ground_asset, wall_asset=None) -> Player:
    tile_dict = get_tile_dict(level_number)

    with open (f'level_data/level_{level_number}_layout.txt', 'r') as file:
        block_y = 0
        for line in file.readlines():
            line = line.strip()
            for block_x in range(len(line)):
                pos_x = block_x * g.tile_size
                pos_y = block_y * g.tile_size
                if line[block_x] in tile_dict.keys():
                    tile = Floor(tile_dict[line[block_x]], (pos_x, pos_y))
                elif line[block_x] == 'p':
                    player = Player('sprites/characters/right/character_purple', (pos_x, pos_y))
            block_y += 1
    define_boundaries(level_number)
    build_background(level_number)
    return player