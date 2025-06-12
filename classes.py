from settings import WIDTH, HEIGHT
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pgzero.builtins import sounds, clock
from pygame import Rect
import global_variables as g

class Player(Actor):
    def __init__ (self, sprite, pos:tuple = None):
        super().__init__(sprite+'_idle', pos)
        self.speed = 5
        self.sprite=sprite+'_'
        self_action = 'idle'
        self.grounded = True
        self.facing_right = True
        self.frame_index_idle = 0
        self.frame_index_move = 0
        self.jump_frame = 0
        self.walk_sound_lenght = sounds.sfx_footsteps.get_length()
        self.walk_sound_ran = 0
        self.falling_frames = 0
        self.velocity_y = 0
        self.gravity = g.gravity
        self.jump_force = -22
        self.max_fall_speed = 20
        g.world_objects['player'] = self
        g.global_player_x, g.global_player_y = self.x, self.y
        
    def get_rect(self):
        return Rect(
            (self.x - self.width / 4, self.bottom - self.height / 1.5),
            (self.width/2, self.height/1.5)
        )

    def idle(self):
        if self.grounded:
            frames = [self.sprite+'idle', self.sprite+'idle_a', self.sprite+'idle', self.sprite+'idle_b']
            self.image = frames[self.frame_index_idle]
        else:
            self.image = self.sprite + 'jump'

    def move(self, direction):
        frames = [self.sprite+'walk_a', self.sprite+'walk_b']
        
        if self.grounded:
            self.image = frames[self.frame_index_move]
            if self.walk_sound_ran >= self.walk_sound_lenght:
                self.walk_sound_ran = 0
                sounds.sfx_footsteps.play()
            self.walk_sound_ran += g.delta_time
        
        if 0 <= g.global_player_x <= g.limit_x:
            movement = self.speed
            if direction == 'l':
                movement *= -1
            self.facing_right = direction == 'r'
            g.global_player_x += movement
            self.x += movement

    def jump(self):
        if self.grounded:
            sounds.sfx_jump.play()
            self.velocity_y = self.jump_force
            self.grounded = False
            

    def apply_gravity(self):
        was_grounded = self.grounded

        if not self.grounded:
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed

            future_rect = Rect(
                (self.x - self.width / 4, (self.y + self.velocity_y) + self.height / 2 - self.height / 1.5),
                (self.width / 2, self.height / 1.5)
            )

            for obj in g.world_objects['tiles']:
                floor_rect = obj.get_rect(g.offset_x)

                falling_from_above = self.y < floor_rect.top and self.velocity_y >= 0
                vertical_overlap = future_rect.bottom >= floor_rect.top
                horizontal_overlap = (
                    future_rect.right > floor_rect.left and
                    future_rect.left < floor_rect.right
                )

                if falling_from_above and vertical_overlap and horizontal_overlap:
                    self.y = floor_rect.top - self.height / 2
                    g.global_player_y = self.y
                    self.velocity_y = 0
                    self.grounded = True
                    return

            self.y += self.velocity_y
            g.global_player_y = self.y
            self.grounded = False

        else:
            player_rect = Rect(
                (self.x - self.width / 4, self.y + self.height / 2 - self.height / 1.5),
                (self.width / 2, self.height / 1.5)
            )

            supported = False
            for obj in g.world_objects['tiles']:
                floor_rect = obj.get_rect(g.offset_x)
                touching_top = abs(player_rect.bottom - floor_rect.top) <= 2
                horizontal_overlap = (
                    player_rect.right > floor_rect.left and
                    player_rect.left < floor_rect.right
                )
                if touching_top and horizontal_overlap:
                    supported = True
                    break

            if not supported:
                self.grounded = False 

    
    def is_touching_floor(self):
        player_rect = self.get_rect()
        for obj in g.world_objects['tiles']:
            obj_rect = obj.get_rect()
            if player_rect.right >= obj_rect.left and player_rect.left <= obj_rect.right:
                if player_rect.bottom >= obj_rect.top and player_rect.bottom - obj_rect.top <= 10:
                    return obj
        return None

    def snap_to_floor(self):
        obj = self.is_touching_floor()
        if obj:
            obj_rect = obj.get_rect()
            self.bottom = obj_rect.top
            self.grounded = True

    def check_grounded(self):
        self.grounded = False
        px = self.get_rect()

        for obj in g.world_objects['tiles']:
            obj_rect = obj.get_rect(g.offset_x)
            if px.right > obj_rect.left and px.left < obj_rect.right:
                if abs(px.bottom - obj_rect.top) <= 2:
                    self.bottom = obj_rect.top
                    self.grounded = True
                    self.falling_frames = 0
                    return
    
    def update(self):
        if self.facing_right:
            self.sprite = self.sprite.replace('/left/', '/right/')
        else:
            self.sprite = self.sprite.replace('/right/', '/left/')
        self.apply_gravity()
        self.idle()


class Enemy(Actor):
    def __init__ (self, sprite, pos:tuple=None):
        super().__init__(sprite+'_idle', pos)
        g.world_objects['enemies'].append(self)



class Floor(Actor):
    def __init__ (self, sprite, pos:tuple=None):
        super().__init__(sprite, pos)
        g.world_objects['tiles'].append(self)

    def get_rect(self, offset_x=g.offset_x, offset_y=g.offset_y):
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        return Rect(
            (screen_x - g.tile_size/2, screen_y - g.tile_size/2),
            (g.tile_size, g.tile_size)
        )