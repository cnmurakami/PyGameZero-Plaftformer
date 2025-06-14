from settings import WIDTH, HEIGHT
from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from pgzero.builtins import sounds, clock, animate, music
from pygame import Rect
import global_variables as g

class Player(Actor):
    def __init__ (self, sprite, pos:tuple = None):
        super().__init__(sprite+'_idle', pos)
        self.speed = 5
        self.sprite=sprite+'_'
        self.is_moving = False
        self.grounded = True
        self.facing_right = True
        self.frame_timer = 0
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
        self.health = 3
        self.invincible = False
        self.invisible = False
        self.can_move = True
        g.world_objects['player'] = self
        g.global_player_x, g.global_player_y = self.x, self.y
        
    def get_rect(self):
        return Rect(
            (self.x - self.width / 4, self.bottom - self.height / 1.5),
            (self.width/2, self.height/1.5)
        )

    def idle(self):
        self.is_moving = False
        if not self.can_move:
            return
        if self.grounded:
            frames = [self.sprite+'idle', self.sprite+'idle_a', self.sprite+'idle', self.sprite+'idle_b']
            self.image = frames[self.frame_index_idle]
        else:
            self.image = self.sprite + 'jump'

    def move(self, direction, override = False):
        if not self.can_move and not override:
            return
        self.is_moving = True
        frames = [self.sprite+'walk_a', self.sprite+'walk_b']
        if self.grounded:
            self.image = frames[self.frame_index_move]
            if self.walk_sound_ran >= self.walk_sound_lenght:
                self.walk_sound_ran = 0
                if g.sound and not override:
                    sounds.sfx_footsteps.play()
            self.walk_sound_ran += g.delta_time
        
        movement = self.speed
        if direction == 'l':
            movement *= -1
        if not override:
            self.facing_right = direction == 'r'
        if not self.will_collide(movement, 0):
            g.global_player_x += movement
            self.x += movement
    
    def will_collide(self, dx, dy):
        future_rect = self.get_rect().move(dx, dy)
        buffer = g.tile_size * 2

        for obj in g.world_objects['walls'] + g.world_objects['floors']:
            if abs(obj.x - self.x) > buffer or abs(obj.y - self.y) > buffer:
                continue

            obj_rect = obj.get_rect(g.offset_x)
            if future_rect.colliderect(obj_rect):
                return True
        return False
    
    def jump(self):
        if not self.can_move:
            return
        if self.grounded:
            if g.sound:
                sounds.sfx_jump.play()
            self.velocity_y = self.jump_force
            self.grounded = False
            
    def apply_gravity(self):
        if not self.grounded:
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed

            future_rect = Rect(
                (self.x - self.width / 4, (self.y + self.velocity_y) + self.height / 2 - self.height / 1.5),
                (self.width / 2, self.height / 1.5)
            )

            for obj in g.world_objects['tiles']:
                if not obj.x - g.tile_size*2 < self.x < obj.x + g.tile_size*2:
                    continue
                if type(obj) == Decoration:
                    continue
                try:
                    floor_rect = obj.get_rect()
                except:
                    continue

                falling_from_above = self.y < floor_rect.top and self.velocity_y >= 0
                vertical_overlap = future_rect.bottom >= floor_rect.top
                horizontal_overlap = (
                    future_rect.right > floor_rect.left and
                    future_rect.left < floor_rect.right
                )

                if falling_from_above and vertical_overlap and horizontal_overlap:
                    new_y = floor_rect.top - self.height / 2
                    g.global_player_y += new_y - self.y
                    self.y = new_y
                    self.velocity_y = 0
                    self.grounded = True
                    if obj.type == 'hazards':
                        self.get_hurt(obj.damage, override = True)
                    return

                hitting_ceiling = self.y > floor_rect.bottom and self.velocity_y < 0
                vertical_ceiling_overlap = future_rect.top <= floor_rect.bottom
                horizontal_ceiling_overlap = horizontal_overlap

                if hitting_ceiling and vertical_ceiling_overlap and horizontal_ceiling_overlap:
                    new_y = floor_rect.bottom + self.height / 2
                    g.global_player_y += new_y - self.y
                    self.y = new_y
                    self.velocity_y = 0
                    break

            previous_y = self.y
            self.y += self.velocity_y
            g.global_player_y += self.y - previous_y
            self.grounded = False

        else:
            player_rect = Rect(
                (self.x - self.width / 4, self.y + self.height / 2 - self.height / 1.5),
                (self.width / 2, self.height / 1.5)
            )

            supported = False
            for obj in g.world_objects['tiles']:
                if not obj.x - g.tile_size*2 < self.x < obj.x + g.tile_size*2:
                    continue
                if type(obj) == Decoration:
                    continue
                try:
                    floor_rect = obj.get_rect(g.offset_x)
                except:
                    continue
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

    
    def get_hurt(self, health_loss = 1, hurt_side = '', override = False):
        if override:
            self.health -= health_loss
            return
        if not self.invincible:
            if g.sound:
                sounds.sfx_hurt.play()
            self.health -= health_loss
            self.invincible = True
            self.can_move = False
            self.is_moving = True
            if self.health > 0:
                clock.schedule_unique(self.recover, 3)
                clock.schedule_unique(self.can_move_again, 0.5)
                if hurt_side == '':
                    hurt_side = 'r' if self.facing_right else 'l'
                original_speed = self.speed
                self.speed = self.speed*20
                if hurt_side == 'r':
                    self.turn_around('r')
                    self.move('l', override = True)
                    
                else:
                    self.turn_around('l')
                    self.move('r', override = True)
                    g.global_player_x += g.tile_size*2
                self.speed = original_speed
            self.image = self.sprite+'hit'
    
    def hurt_animation(self):
        if self.invincible:
            self.invisible = not self.invisible
            if self.invisible:
                self.sprite = self.sprite.replace('/left/', '/hurt/')
                self.sprite = self.sprite.replace('/right/', '/hurt/')
            else:
                self.sprite = g.player_sprite+'_'
    
    def can_move_again(self):
        self.can_move = True
        self.image = self.sprite+'idle'

    def recover(self):
        self.sprite = g.player_sprite+'_'
        self.invincible = False
        self.invisible = False

    def turn_around(self, forced=None):
        self.facing_right = True if forced == 'r' else False if forced == 'l' else self.facing_right
        if self.facing_right:
            self.sprite = self.sprite.replace('/left/', '/right/')
        else:
            self.sprite = self.sprite.replace('/right/', '/left/')

    def update_frame_index(self):
        self.frame_timer += g.delta_time
        if self.frame_timer >= g.frame_delay:
            self.frame_timer = 0
            self.frame_index_idle = (self.frame_index_idle + 1) % 4
            self.frame_index_move = (self.frame_index_move + 1) % 2

    def check_death(self):
        if self.health <= 0:
            return True
    
    def death_back_down(self):
        music.play('game_over')
        angle = 180 if self.facing_right else -180
        animate(self, duration = 0.3, tween='accelerate', pos = (self.x, HEIGHT + g.tile_size*2), angle=angle)

    def death_animation(self):
        if g.sound:
            sounds.sfx_disappear.play()
        self.invisible = False
        self.grounded = False
        self.can_move = False
        self.invincible = True
        self.sprite = g.player_sprite+'_'
        self.turn_around('r' if self.facing_right else 'l')
        self.image = self.sprite+'hit'
        duration = 0.5
        angle = 180 if self.facing_right else -180
        clock.schedule(self.death_back_down, duration)
        animate(self, duration=duration, tween='decelerate', pos = (self.x, g.tile_size*2), angle = angle)
        
    def update(self):
        self.hurt_animation()
        if not self.invisible:
            self.turn_around(self)
        self.apply_gravity()
        self.update_frame_index()
        self.idle()


class Enemy(Actor):
    def __init__ (self, sprite, pos:tuple=None):
        super().__init__(sprite+'_idle', pos)
        self.initial_pos_x = pos[0]
        self.initial_pos_y = pos[1]
        self.sprite = sprite + '_'
        self.wait_time = 0
        self.jump_force = 0
        self.jumping = False
        self.grounded = True
        self.facing_right = False
        self.speed = 0
        self.gravity = g.gravity
        self.max_fall_speed = 20
        self.frame_index_idle = 0
        self.frames = ['idle', 'idle_a']
        self.frame_timer = 0
        self.velocity_y = 0
        g.world_objects['enemies'].append(self)
    
    def idle(self):
        self.idle_frames = [self.sprite+x for x in self.frames]
        if self.grounded and not self.jumping:
            self.image = self.idle_frames[self.frame_index_idle]

    def get_rect(self):
        return Rect(
            (self.x - self.width / 4, self.bottom - self.height / 1.5),
            (self.width/2, self.height/1.5)
        )

    def hurt_player(self, damage = 1):
        player:Player = g.world_objects['player']
        if self.get_rect().colliderect(player.get_rect()):
            side = 'r' if player.x < self.x else 'l'
            player.get_hurt(damage, side)

    def turn_around(self, forced=None):
        self.facing_right = True if forced == 'r' else False if forced == 'l' else self.facing_right
        if self.facing_right:
            self.sprite = self.sprite.replace('/left/', '/right/')
        else:
            self.sprite = self.sprite.replace('/right/', '/left/')
        
    def jump(self):
        self.velocity_y = self.jump_force
        self.image = self.sprite+'jump'
        self.grounded = False
            
    def apply_gravity(self):
        if not self.grounded:
            self.velocity_y += self.gravity
            if self.velocity_y > self.max_fall_speed:
                self.velocity_y = self.max_fall_speed

            future_rect = Rect(
                (self.x - self.width / 4, (self.y + self.velocity_y) + self.height / 2 - self.height / 1.5),
                (self.width / 2, self.height / 1.5)
            )

            for obj in g.world_objects['tiles']:
                if not obj.x - g.tile_size*2 < self.x < obj.x + g.tile_size*2:
                    continue
                if type(obj) == Decoration:
                    continue
                floor_rect = obj.get_rect()

                falling_from_above = self.y < floor_rect.top and self.velocity_y >= 0
                vertical_overlap = future_rect.bottom >= floor_rect.top
                horizontal_overlap = (
                    future_rect.right > floor_rect.left and
                    future_rect.left < floor_rect.right
                )

                if falling_from_above and vertical_overlap and horizontal_overlap:
                    new_y = floor_rect.top - self.height / 2
                    self.y = new_y
                    self.velocity_y = 0
                    self.grounded = True
                    self.wait_time = 3
                    self.image = self.sprite+'idle'
                    return

                hitting_ceiling = self.y > floor_rect.bottom and self.velocity_y < 0
                vertical_ceiling_overlap = future_rect.top <= floor_rect.bottom
                horizontal_ceiling_overlap = horizontal_overlap

                if hitting_ceiling and vertical_ceiling_overlap and horizontal_ceiling_overlap:
                    new_y = floor_rect.bottom + self.height / 2
                    self.y = new_y
                    self.velocity_y = 0
                    break

            self.y += self.velocity_y
            self.grounded = False

        else:
            enemy_rect = Rect(
                (self.x - self.width / 4, self.y + self.height / 2 - self.height / 1.5),
                (self.width / 2, self.height / 1.5)
            )

            supported = False
            for obj in g.world_objects['tiles']:
                if not obj.x - g.tile_size*2 < self.x < obj.x + g.tile_size*2:
                    continue
                if type(obj) == Decoration:
                    continue
                floor_rect = obj.get_rect(g.offset_x)
                touching_top = abs(enemy_rect.bottom - floor_rect.top) <= 2
                horizontal_overlap = (
                    enemy_rect.right > floor_rect.left and
                    enemy_rect.left < floor_rect.right
                )
                if touching_top and horizontal_overlap:
                    supported = True
                    break

            if not supported:
                self.grounded = False 

    def will_collide(self, dx, dy):
        future_rect = self.get_rect().move(dx, dy)
        buffer = g.tile_size * 2

        for obj in g.world_objects['walls'] + g.world_objects['floors']:
            if abs(obj.x - self.x) > buffer or abs(obj.y - self.y) > buffer:
                continue

            obj_rect = obj.get_rect(g.offset_x)
            if future_rect.colliderect(obj_rect):
                return True
        return False

    def is_ground_ahead(self):
        direction = 1 if self.facing_right else -1
        step_distance = g.tile_size // 2

        probe_x = self.x + direction * step_distance
        probe_y = self.y + self.height / 2 + 1
        probe_rect = Rect((probe_x - 1, probe_y), (2, 2))

        buffer = g.tile_size * 2

        for tile in g.world_objects['tiles']:
            if isinstance(tile, Decoration):
                continue
            if abs(tile.x - probe_x) > buffer or abs(tile.y - probe_y) > buffer:
                continue
            if probe_rect.colliderect(tile.get_rect()):
                return True
        return False

    def update_frame_index(self):
        self.frame_timer += g.delta_time
        if self.frame_timer >= g.frame_delay:
            self.frame_timer = 0
            self.frame_index_idle = (self.frame_index_idle + 1) % len(self.frames)

    def is_visible(self):
        return -g.tile_size < self.x < WIDTH+g.tile_size and -g.tile_size*2 < self.y < HEIGHT+g.tile_size*2

    def update(self):
        if not self.is_visible():
            return
        self.hurt_player()
        self.turn_around()
        self.update_frame_index()
        self.idle()

class Enemy_Jumper(Enemy):
    def __init__ (self, sprite = 'sprites/enemies/left/frog', pos = (WIDTH/2, HEIGHT/2)):
        super().__init__(sprite, pos=pos)
        self.wait_time = 3
        self.jump_force = -22
        self.jumping = False
        self.grounded = True
        self.gravity = 1.1
        self.max_fall_speed = 20
        self.frame_index_idle = 0
        self.frame_timer = 0
        self.velocity_y = 0
        
    def jump(self):
        super().jump()
        self.jumping = False

    def update(self):
        if not super().is_visible():
            return
        if self.wait_time <= 0:
            if self.grounded and not self.jumping:
                self.jumping = True
                self.image = self.sprite+'jump_a'
                clock.schedule_unique(self.jump, 1)
        else:
            self.wait_time -= g.delta_time
        super().update()
        super().apply_gravity()

class Enemy_Walker(Enemy):
    def __init__ (self, sprite='sprites/enemies/left/mouse', pos = (WIDTH/2, HEIGHT/2)):
        super().__init__(sprite='sprites/enemies/left/mouse', pos=pos)
        self.speed = 7

    def update(self):
        if not super().is_visible():
            return
        super().update()
        direction = 1 if self.facing_right else -1
        dx = direction * self.speed

        if not super().is_ground_ahead() or super().will_collide(dx, 0):
            self.facing_right = not self.facing_right
            direction *= -1
            dx = direction * self.speed

        if not self.will_collide(dx, 0):
            self.x += dx
    
class Terrain(Actor):
    def __init__ (self, sprite, type, pos:tuple=None, damage=0):
        super().__init__(sprite, pos)
        self.type = type
        self.damage = damage
        g.world_objects[type].append(self)
        g.world_objects['tiles'].append(self)

    def get_rect(self, offset_x=g.offset_x, offset_y=g.offset_y):
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        return Rect(
            (screen_x - g.tile_size/2, screen_y - g.tile_size/2),
            (g.tile_size, g.tile_size)
        )


class Decoration(Actor):
    def __init__ (self, sprite, pos:tuple=None):
        super().__init__(sprite, pos)
        g.world_objects['decorations'].append(self)

    def get_rect(self, offset_x=g.offset_x, offset_y=g.offset_y):
        screen_x = self.x - offset_x
        screen_y = self.y - offset_y
        return Rect(
            (screen_x - g.tile_size/2, screen_y - g.tile_size/2),
            (g.tile_size, g.tile_size)
        )


class Parallax(Actor):
    def __init__ (self, sprite, level, pos:tuple=None):
        super().__init__(sprite, pos)
        self.total_width = WIDTH/self.width*self.width+self.width
        self.force_x = level*0.25
        self.force_y = 0.15
        self.auto_scroll = 'clouds' in sprite
        g.world_objects['parallax'][level].append(self)

    def update(self):
        if self.right <= 0:
            self.x += self.total_width
        elif self.left >= WIDTH:
            self.x -= self.total_width
        if self.auto_scroll:
            self.x -=  self.force_x * 0.5


class Camera():
    def __init__(self):
        self.player:Player = g.world_objects['player']
        self.can_move_right = True
        self.can_move_left = True
        self.can_move_down = True
        self.can_move_up = True
        self.offset_x = 0
        self.offset_y = 0
        self.speed = 10
        self.default_speed = 10
        self.started = False
        self.outer_rect = Rect(
            (0, 0),
            (WIDTH, HEIGHT)
        )
        self.inner_rect = Rect(
            (WIDTH/3, (HEIGHT - (HEIGHT/1.75)) / 2),
            (WIDTH/3, HEIGHT/1.75)
        )
        g.world_objects['camera'] = self

    def move_camera(self):
        if self.can_move_right and self.player.facing_right:
            if self.player.x > self.inner_rect.left:
                if self.player.x < self.inner_rect.left:
                    g.offset_x += self.speed
                if self.player.x > self.inner_rect.left:
                    g.offset_x -= self.speed
        
        elif self.can_move_left and not self.player.facing_right:
            if self.player.x < self.inner_rect.right:
                if self.player.x < self.inner_rect.right:
                    g.offset_x += self.speed
                if self.player.x > self.inner_rect.right:
                    g.offset_x -= self.speed
        if self.inner_rect.colliderect(self.player.get_rect()):
            self.update_speed()
        if self.can_move_up and self.player.center[1] < HEIGHT/2:
            g.offset_y += HEIGHT/2 - self.player.center[1]
        if self.can_move_down and self.player.center[1] > HEIGHT/2:
            g.offset_y -= self.player.center[1] - HEIGHT/2

    def offset_stage(self):
        for actor in g.world_objects['enemies']:
            actor.x += g.offset_x
            actor.y += g.offset_y
        for geometry in g.world_objects['tiles']:
            geometry.x += g.offset_x
            geometry.y += g.offset_y
        for item in g.world_objects['decorations']:
            item.x += g.offset_x
            item.y += g.offset_y
    
    def offset_player(self):
        self.player.x += g.offset_x
        self.player.y += g.offset_y
        self.offset_x -= g.offset_x
        self.offset_y += g.offset_y

    def offset_background(self):
        for i in range(3, 0, -1):
            for actor in g.world_objects['parallax'][i]:
                actor.x += g.offset_x * actor.force_x
                actor.y += g.offset_y * actor.force_y
                actor.update()
    def reset_offset(self):
        g.offset_y, g.offset_x = 0, 0

    def update_speed(self):
        if self.player.is_moving:
            can_speed_right = self.player.facing_right and self.player.x > self.inner_rect.left + self.player.width/2
            can_speed_left = not self.player.facing_right and self.player.x < self.inner_rect.right - self.player.width/2
            if can_speed_right or can_speed_left:
                self.speed = self.default_speed + self.player.speed
            else:
                self.speed = self.player.speed
        else:
            self.speed = self.default_speed

    def can_move(self):
        self.can_move_right = self.outer_rect.right+self.offset_x < g.limit_x - g.background_tile_size/2
        self.can_move_left = self.outer_rect.left-(-self.offset_x) > 0
        self.can_move_up = self.outer_rect.top-self.offset_y > 0
        self.can_move_down = self.outer_rect.bottom+(-self.offset_y) < g.limit_y-g.tile_size

    def update(self):
        if not self.started:
            self.speed = self.default_speed*30
        if not self.started and self.inner_rect.colliderect(self.player.get_rect()):
            self.started = True
        self.can_move()
        self.move_camera()
        self.offset_background()
        self.offset_stage()
        self.offset_player()
        self.reset_offset()


class Menu():
    def __init__(self):
        self.state = 'main'
        self.sound_image = 'ui/black/audio_'
        self.music_image = 'ui/black/music_'
        self.sound_icon = Actor(self.sound_image+'on', (WIDTH/2 + 100, HEIGHT/3*2))
        self.music_icon = Actor(self.music_image+'on', (WIDTH/2 - 100, HEIGHT/3*2))
        g.world_objects['menu'] = self
        self.start_button = Actor

    def update(self):
        sound_state = 'on' if g.sound else 'off'
        music_state = 'on' if g.music else 'off'
        self.sound_icon = Actor(self.sound_image+sound_state, (WIDTH/2 + 100, HEIGHT/3*2))
        self.music_icon = Actor(self.music_image+music_state, (WIDTH/2 - 100, HEIGHT/3*2))

    def draw(self):
        self.sound_icon.draw()
        self.music_icon.draw()