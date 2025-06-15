# lib imports
import pgzrun
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pgzero.builtins import clock, music, animate


# local imports
from classes import Camera, Menu
from settings import *
from level_builder import create_level, draw_background
import global_variables as g

# ------------------ VARIABLES ----------------------

states = ['running', 'paused', 'win', 'title', 'game_over']
state = 'title' if not DEBUG else 'running'
g.music = g.music if not DEBUG else False
substate = ''
state_ready = False
level = 1
level_components = []

menu = Menu()
music.play('menu')
start_button = Actor('ui/white/start', (WIDTH/2, HEIGHT/2))
restart_button = Actor('ui/white/retry', (WIDTH/2, HEIGHT/2))
next_button = Actor('ui/white/continue', (WIDTH/2, HEIGHT/2))
ufo = Actor('sprites/characters/ufo/ship_green_manned', pos = (-WIDTH, -HEIGHT))
ufo_beam = Actor('sprites/characters/ufo/laser_blue2', pos = (-WIDTH, -HEIGHT))
level_text_actor = Actor(g.player_sprite.replace('/right/', '/hurt/')+'_idle', pos = (-WIDTH, -HEIGHT))
title_sprite_a = Actor('sprites/characters/right/character_purple_hit', (WIDTH/4, HEIGHT/2+100))
title_sprite_b = Actor('sprites/characters/ufo/ship_green_manned', (WIDTH/4*3, HEIGHT/2-100))

# ------------------ BUILDERS ----------------------

def main_menu():
    global state_ready
    music.play('menu')
    state_ready = True

def load_level(level):
    global state_ready
    g.world_objects['player'] = None
    g.world_objects['exit'] = None
    g.world_objects['enemies'] = []
    g.world_objects['tiles'] = []
    g.world_objects['walls'] = []
    g.world_objects['floors'] = []
    g.world_objects['ceilings'] = []
    g.world_objects['hazards'] = []
    g.world_objects['decorations'] = []
    g.world_objects['camera'] = None
    for key in g.world_objects['parallax'].keys():
        g.world_objects['parallax'][key] = []
    player = create_level(level, 'sprites/tiles/terrain_grass_block_top')
    g.global_player_x, g.global_player_y = g.world_objects['player'].pos
    camera = Camera()
    try:
        music.play(f'stage_{level}')
    except:
        music.play(f'stage_1')
    level_text_actor.x = WIDTH/2
    level_text_actor.y = -g.tile_size*2
    animate(level_text_actor, tween='decelerate', duration=2, pos=(level_text_actor.x, HEIGHT/2),
        on_finished = lambda: animate(level_text_actor, tween='accelerate', duration=1, pos=(level_text_actor.x, HEIGHT+g.tile_size*2)
        ))
    state_ready = True

def game_over():
    global state_ready
    g.world_objects['player'].death_animation()
    state_ready = True

def win():
    global state_ready, ufo
    music.play('win')
    player = g.world_objects['player']
    player.win_animation()
    ufo.x = player.x
    ufo.y = -g.tile_size-2
    animate(ufo, tween='decelerate', duration = 3, pos = (player.x, player.y-g.tile_size*1.5))
    clock.schedule_unique(win_animation, 3)
    state_ready = True

def win_animation():
    if state != 'win':
        return
    player = g.world_objects['player']
    ufo_beam.x = player.x
    ufo_beam.bottom = player.bottom
    animate(player, tween='linear', duration=1, pos=(player.x, ufo.y))
    clock.schedule_unique(ufo_leave, 1)

def ufo_leave():
    if state != 'win':
        return
    player = g.world_objects['player']
    empty_image = player.sprite.replace('/right/', '/hurt/').replace('/left/', '/hurt/')+'idle'
    player.image = empty_image
    ufo_beam.image = empty_image
    animate(ufo, tween='bounce_start', duration=1, pos=(ufo.x, -g.tile_size*2))

def check_next_level():
    global level, state, state_ready
    if state != 'win':
        return
    level += 1
    try:
        with open(f'level_data/{level}/layout.txt', 'r') as f:
            pass
        state = 'running'
    except:
        level = 1
        state = 'title'
    state_ready = False

# ------------------ INPUTS ----------------------

def on_mouse_down(pos):
    global state, state_ready
    if DEBUG:
        try:
            for item in g.world_objects['tiles']:
                if item.collidepoint(pos):
                    print(type(item))
                    print(item.type)
                    print(item.damage)
            if g.world_objects['player'].collidepoint(pos):
                g.world_objects['player'].get_hurt(3)
        except:
            pass
    if (start_button.collidepoint(pos) or restart_button.collidepoint(pos)) and state in ['title', 'game_over']:
        state = 'running'
        state_ready = False
    if next_button.collidepoint(pos) and state == 'win':
        check_next_level()
    if menu.music_icon.collidepoint(pos) and state in ['paused', 'title']:
        g.music = not g.music
    if menu.sound_icon.collidepoint(pos) and state in ['paused', 'title']:
        g.sound = not g.sound
    if menu.exit_icon.collidepoint(pos) and state in ['paused', 'title']:
        exit()

def on_key_down(key):
    global state, state_ready
    if (key == keys.RETURN) and state in ['game_over', 'title']:
        state = 'running'
        state_ready = False
    if (key == keys.RETURN) and state == 'win':
        check_next_level()
    if key == keys.ESCAPE:
        if state in ['running', 'paused']:
            state = 'paused' if state=='running' else 'running'
    if key == keys.P and DEBUG:
        g.paused = not g.paused
    if key == keys.BACKSPACE and DEBUG:
        g.step = True
    if (key == keys.W or key == keys.SPACE or key == keys.UP) and state == 'running' and state_ready:
        g.world_objects['player'].jump()
    if key == keys.TAB:
        if keyboard.lctrl:
            g.show_osd = not g.show_osd
        else:
            g.show_box = not g.show_box

# ------------------ ENGINE ----------------------

def update(dt):
    global state, state_ready
    menu.update()
    music.set_volume(g.music)
    if state == 'win':
        if state_ready:
            return
        if not state_ready:
            win()
    if state == 'game_over':
        if state_ready:
            return
        if not state_ready:
            music.stop()
            game_over()
        return
    if state == 'title':
        if not state_ready:
            main_menu()
        if state_ready:
            title_sprite_a.angle+=3
            title_sprite_b.angle-=1
            return
    if state == 'running':
        if not state_ready:
            load_level(level)
            return
        if g.paused and not g.step:
            return
        g.delta_time = dt
        if g.world_objects['player'].check_death():
            state = 'game_over'
            state_ready = False
        if g.world_objects['player'].check_win():
            state = 'win'
            state_ready = False
        g.world_objects['player'].update()
        for enemy in g.world_objects['enemies']:
            enemy.update()
        if keyboard.d or keyboard.right:
            g.world_objects['player'].move('r')
        if keyboard.a or keyboard.left:
            g.world_objects['player'].move('l')
        if DEBUG:
            if keyboard.right or keyboard.up or keyboard.down or keyboard.left:
                g.world_objects['camera'].can_move_right=True
                g.world_objects['camera'].can_move_left=True
                g.world_objects['camera'].can_move_up=True
                g.world_objects['camera'].can_move_down=True
                g.world_objects['player'].pos = (WIDTH/2, HEIGHT/2)
                g.world_objects['player'].invincible = True
                if keyboard.right:
                    g.offset_x-=10
                    g.world_objects['player'].facing_right = True
                if keyboard.left:
                    g.world_objects['player'].facing_right = False
                    g.offset_x+=10
                if keyboard.up:
                    g.offset_y+=10
                if keyboard.down:
                    g.offset_y-=10
                g.world_objects['player'].invincible = False
            g.step = False
        g.world_objects['camera'].update()
    if state == 'paused':
        return

def draw():
    global state
    if state == 'title':
        screen.clear()
        screen.fill((180,200,200))
        title_sprite_a.draw()
        title_sprite_b.draw()
        screen.draw.text('ZERO PLATFORMER\nGAME DEMO', centerx=WIDTH/2, centery=HEIGHT/5, fontname = font, fontsize=80, color = (200,255,255), owidth = 3, ocolor = 'black')
        start_button.draw()
        menu.draw()
    if state in ['running', 'paused', 'game_over', 'win'] and state_ready:
        screen.clear()
        draw_background()
        for actor in g.world_objects['tiles']:
            actor.draw()
        for actor in g.world_objects['decorations']:
            actor.draw()
        for actor in g.world_objects['enemies']:
            actor.draw()
        g.world_objects['player'].draw()
        screen.blit('sprites/tiles/hud_player_helmet_purple', (20, 20))
        for i in range(1, 4):
            img = 'sprites/tiles/hud_heart'
            if i > g.world_objects['player'].health:
                img += '_empty'
            screen.blit(img, (40*i+40, 20))
        screen.draw.text(f'LEVEL {level}', centerx=level_text_actor.x, centery=level_text_actor.y, fontname = font, fontsize=120, color = (200,255,255), owidth = 3, ocolor = 'black')
        if DEBUG:
            if g.show_osd:
                debug_msgs = [
                    f'limit: ({g.limit_x}, {g.limit_y})',
                    f'FPS: {1/g.delta_time if g.delta_time>0 else 0:.2f}',
                    f'Player POS SCREEN: {g.world_objects['player'].pos}',
                    f'Player POS GLOBAL: {(g.global_player_x, g.global_player_y)}',
                    f'Facing Right: {g.world_objects['player'].facing_right}, Moving: {g.world_objects['player'].is_moving}',
                    f'GROUNDED: {g.world_objects['player'].grounded}',
                    f'CAM Offset: {(g.world_objects['camera'].offset_x, g.world_objects['camera'].offset_y)}',
                    f'CAM Move: l:{str(g.world_objects['camera'].can_move_left)[:1]}, r:{str(g.world_objects['camera'].can_move_right)[:1]}, u:{str(g.world_objects['camera'].can_move_up)[:1]}, d:{str(g.world_objects['camera'].can_move_down)[:1]}',
                    f'Invincible: {g.world_objects['player'].invincible}',
                    f'enemies: {len(g.world_objects['enemies'])}',
                    f'tiles: {len(g.world_objects['tiles'])}',
                    f'walls: {len(g.world_objects['walls'])}',
                    f'floors: {len(g.world_objects['floors'])}',
                    f'ceilings: {len(g.world_objects['ceilings'])}',
                    f'hazards: {len(g.world_objects['hazards'])}',
                ]
                for i in range(1, len(debug_msgs)+1):
                    try:
                        screen.draw.text(debug_msgs[i-1], (10, i*20), color = 'black', background = 'white')
                    except:
                        pass
            if g.show_box:
                screen.draw.rect(g.world_objects['player'].get_rect(), 'blue')
                for obj in g.world_objects['tiles']:
                    try:
                        screen.draw.rect(obj.get_rect(g.offset_x), 'green')
                    except:
                        pass
                for obj in g.world_objects['enemies']:
                    screen.draw.rect(obj.get_rect(), 'red')
                screen.draw.rect(g.world_objects['camera'].outer_rect, 'purple')
                screen.draw.rect(g.world_objects['camera'].inner_rect, 'purple')
        if state == 'paused':
            screen.draw.text('PAUSED', centerx=WIDTH/2, centery=HEIGHT/3, fontname = font, fontsize=120, color = (200,255,255), owidth = 3, ocolor = 'black')
            menu.draw()
        if state == 'game_over':
            screen.draw.text('GAME OVER', centerx=WIDTH/2, centery=HEIGHT/4, fontname = font, fontsize=120, color = (200,255,255), owidth = 3, ocolor = 'black')
            restart_button.draw()
        if state == 'win':
            ufo_beam.draw()
            g.world_objects['player'].draw()
            ufo.draw()
            screen.draw.text('SUCCESS', centerx=WIDTH/2, centery=HEIGHT/4, fontname = font, fontsize=120, color = (200,255,255), owidth = 3, ocolor = 'black')
            next_button.draw()