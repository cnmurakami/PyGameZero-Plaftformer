paused = False
step = False
show_osd = True
show_box = True

frame_timer = 0
frame_delay = 0.2
delta_time = 0
gravity = 1.2
offset_x = 0
offset_y = 0
limit_x = 0
limit_y = 0
tile_size = 64
background_tile_size = 256
global_player_x = 0
global_player_y = 0
player_sprite = 'sprites/characters/right/character_purple'
world_objects = {
    'player': None,
    'enemies': [],
    'tiles': [],
    'parallax':{1:[], 2:[], 3:[]}
}
