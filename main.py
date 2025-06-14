# lib imports
import pgzrun
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pgzero.builtins import sounds, clock, music
from random import randint
from pygame import Rect

# local imports
from classes import Camera, Menu
from settings import *
from level_builder import create_level, draw_background
import global_variables as g

states = ['running', 'paused', 'winning', 'title', 'game_over']
state = 'title' if not DEBUG else 'running'
g.music = g.music if not DEBUG else False
substate = ''
state_ready = False
level = 1
level_components = []

menu = Menu()
music.play('menu')
start_button = Actor('ui/black/button_start', (WIDTH/2, HEIGHT/2))
restart_button = Actor('ui/black/return', (WIDTH/2, HEIGHT/2))

def load_level(level):
    global state_ready
    g.world_objects['player'] = None
    g.world_objects['enemies'] = []
    g.world_objects['tiles'] = []
    g.world_objects['walls'] = []
    g.world_objects['floors'] = []
    g.world_objects['ceilings'] = []
    g.world_objects['hazards'] = []
    g.world_objects['camera'] = None
    for key in g.world_objects['parallax'].keys():
        g.world_objects['parallax'][key] = []
    player = create_level(level, 'sprites/tiles/terrain_grass_block_top')
    g.global_player_x, g.global_player_y = g.world_objects['player'].pos
    camera = Camera()
    music.play(f'stage_{level}')
    state_ready = True

def game_over():
    global state_ready
    g.world_objects['player'].death_animation()
    state_ready = True
    

def on_mouse_down(pos):
    global state, state_ready
    if DEBUG:
        try:
            for item in g.world_objects['tiles']:
                if item.collidepoint(pos):
                    print(item.type)
                    print(item.damage)
                    #g.world_objects['tiles'].remove(item)
            if g.world_objects['player'].collidepoint(pos):
                g.world_objects['player'].get_hurt(3)
        except:
            pass
    if start_button.collidepoint(pos) or restart_button.collidepoint(pos):
        state = 'running'
        state_ready = False
    if menu.music_icon.collidepoint(pos):
        g.music = not g.music
    if menu.sound_icon.collidepoint(pos):
        g.sound = not g.sound

def on_key_down(key):
    global state, state_ready
    if (key == keys.RETURN or key == keys.SPACE) and state == 'game_over':
        state = 'running'
        state_ready = False
    if key == keys.ESCAPE:
        if state in ['running', 'paused']:
            state = 'paused' if state=='running' else 'running'
    if key == keys.P:
        g.paused = not g.paused
    elif key == keys.SPACE and DEBUG:
        g.step = True
    if key == keys.W:
        g.world_objects['player'].jump()
    if key == keys.TAB:
        if keyboard.lctrl:
            g.show_osd = not g.show_osd
        else:
            g.show_box = not g.show_box

def update(dt):
    global state, state_ready
    menu.update()
    music.set_volume(g.music)
    if state == 'game_over':
        if state_ready:
            return
        if not state_ready:
            music.stop()
            game_over()
        return
    if state == 'title':
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
        g.world_objects['player'].update()
        for enemy in g.world_objects['enemies']:
            enemy.update()
        if keyboard.d:
            g.world_objects['player'].move('r')
        if keyboard.a:
            g.world_objects['player'].move('l')
        if DEBUG:
            if keyboard.right or keyboard.up or keyboard.down or keyboard.left:
                g.world_objects['camera'].can_move_right=True
                g.world_objects['camera'].can_move_left=True
                g.world_objects['camera'].can_move_up=True
                g.world_objects['camera'].can_move_down=True
                g.world_objects['player'].pos = (WIDTH/2, HEIGHT/2)
                g.world_objects['player'].get_hurt(0)
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
            g.step = False
        g.world_objects['camera'].update()
    if state == 'paused':
        return




def draw():
    global state
    if state == 'title':
        screen.clear()
        screen.fill((255,255,255))
        screen.draw.text('ZERO PLATFORMER\nGAME DEMO', centerx=WIDTH/2, centery=HEIGHT/4, fontsize=120, color = 'black')
        start_button.draw()
        menu.draw()
    # if state == 'game_over':
    #     screen.clear()
    #     draw_background()
    #     for actor in g.world_objects['tiles']:
    #         actor.draw()
    #     for actor in g.world_objects['enemies']:
    #         actor.draw()
    #     g.world_objects['player'].draw()
    #     screen.blit('sprites/tiles/hud_player_helmet_purple', (20, 20))
    #     for i in range(1, 4):
    #         img = 'sprites/tiles/hud_heart'
    #         if i > g.world_objects['player'].health:
    #             img += '_empty'
    #         screen.blit(img, (40*i+40, 20))
    #     screen.draw.text('GAME OVER', centerx=WIDTH/2, centery=HEIGHT/4, fontsize=120, color = 'black')
    #     restart_button.draw()
    #     menu.draw()
    if state in ['running', 'paused', 'game_over'] and state_ready:
        screen.clear()
        draw_background()
        for actor in g.world_objects['tiles']:
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
            screen.draw.text('PAUSED', centerx=WIDTH/2, centery=HEIGHT/3, fontsize=120, color = 'black')
            menu.draw()
        if state == 'game_over':
            screen.draw.text('GAME OVER', centerx=WIDTH/2, centery=HEIGHT/4, fontsize=120, color = 'black')
            restart_button.draw()
            menu.draw()