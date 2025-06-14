from settings import WIDTH, HEIGHT
from pgzero.actor import Actor
from pgzero.builtins import sounds
from pygame import Rect
import global_variables as g
from classes import Player, Enemy_Jumper, Terrain, Parallax

def define_boundaries(level):
    with open(f'level_data/level_{level}_layout.txt', 'r') as file:
        lines = file.readlines()
        g.limit_x = len(lines[0].strip())*g.tile_size
        g.limit_y = len(lines)*g.tile_size        
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


def get_tile_sources(level):
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
    tile_dict = get_tile_sources(level_number)
    map = []
    with open (f'level_data/level_{level_number}_layout.txt', 'r') as file:
        for line in file.readlines():
            map.append(line.strip())
        
    for i in range(len(map)):
        for j in range(len(map[i])):
            placement = (j*g.tile_size, i*g.tile_size)
            if map[i][j] in tile_dict.keys():
                tile = Actor(tile_dict[map[i][j]], placement)
                g.world_objects['tiles'].append(tile)
            if map[i][j] == 'p':
                player = Player(g.player_sprite, placement) 
            if map[i][j] == '=':
                tile = 'center'
                type = 'ceiling'
                top_tile = False
                bottom_tile = False
                source = tile_dict['terrain']
                try:
                    if map[i-1][j] != '=':
                        top_tile = True
                except:
                    pass
                try:
                    if map[i+1][j] != '=':
                        bottom_tile = True
                except:
                    pass

                if top_tile and bottom_tile:
                    source = tile_dict['single_block']
                    tile = 'middle'
                    type = 'floors'
                    try:
                        if map[i][j-1] != '=':
                            tile = 'left'
                        elif map[i][j+1] != '=':
                            tile = 'right'
                    except:
                        pass
                else:
                    if top_tile:
                        tile = 'top'
                        type = 'floors'
                        try:
                            if map[i][j-1] != '=':
                                tile = 'top_left'
                            elif map[i][j+1] != '=':
                                tile = 'top_right'
                        except:
                            pass
                    elif bottom_tile:
                        tile = 'bottom'
                        type = 'ceilings'
                        try:
                            if map[i][j-1] != '=':
                                tile = 'bottom_left'
                            elif map[i][j+1] != '=':
                                tile = 'bottom_right'
                        except:
                            pass
                    else:
                        type = 'walls'
                        try:
                            if map[i][j-1] != '=':
                                tile = 'left'
                            elif map[i][j+1] != '=':
                                tile = 'right'
                        except:
                            pass
                actor = Terrain(source+tile, type, placement)
            if map[i][j] == '!':
                tile = '_top'
                try:
                    if map[i-1][j] == '!':
                        tile = ''
                except:
                    pass
                actor = Terrain(tile_dict['hazard']+tile, 'hazards', placement)
            if map[i][j] == '1':
                actor = Enemy_Jumper(placement)
            

    define_boundaries(level_number)
    build_background(level_number)
    return player