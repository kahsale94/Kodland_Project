import pgzrun
import random
import math
from pygame import Rect


TITLE = "Ninja vs Zombies"
WIDTH = 800
HEIGHT = 480
LEVEL_WIDTH = 2400


game_state = "menu"
camera_x = 0
sound_on = True
hero = None


menu_buttons = {
    "start": Rect((WIDTH//2 - 105, 240, 200, 71)),
    "toggle_sound": Rect((WIDTH//2 - 155, 320, 199, 71)),
    "quit": Rect((WIDTH//2 - 80, 400, 152, 71)),
    "menu": Rect((WIDTH//2 - 90, 310, 200, 83))
}

victory_button_rect = Rect((0, 0), (0, 0))

def draw():
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "game_over":
        draw_game_over()
    elif game_state == "victory":
        draw_victory()

def update():
    if game_state == "playing":
        update_game()

def on_mouse_down(pos):
    global game_state, sound_on
    
    if game_state == "menu":
        if menu_buttons["start"].collidepoint(pos):
            start_game()
        elif menu_buttons["toggle_sound"].collidepoint(pos):
            sound_on = not sound_on
            if sound_on:
                music.play("background_music")
            else:
                music.stop()
        elif menu_buttons["quit"].collidepoint(pos):
            quit()

    if game_state == "game_over":
        if menu_button_rect.collidepoint(pos):
            game_state = "menu"
            stop_music()

    if game_state == "victory":
        if victory_button_rect.collidepoint(pos):
            game_state = "menu"
            stop_music()


def on_key_down(key):
    if game_state == "playing":
        if key == keys.SPACE:
            hero.jump()
        if key == keys.K:
            hero.attack()
    elif game_state == "game_over":
        if key == keys.R:
            start_game()     

def play_sound(name):
    if sound_on:
        getattr(sounds, name).play()

def play_music(name):
    if sound_on:
        music.play(name)

def stop_music():
    music.stop()

def draw_menu():
    screen.clear()
    screen.blit("background", (0, 0))
    
    screen.blit("logo", (menu_buttons["start"].left - 20, menu_buttons["start"].top - 225))
    screen.blit("play", (menu_buttons["start"].left, menu_buttons["start"].top))
    screen.blit("exit", (menu_buttons["quit"].left, menu_buttons["quit"].top))
    screen.blit("sound", (menu_buttons["toggle_sound"].left, menu_buttons["toggle_sound"].top))
    screen.blit("on" if sound_on else "off", (menu_buttons["toggle_sound"].right + 10, menu_buttons["toggle_sound"].top))

def start_game():
    global game_state, hero
    game_state = "playing"
    ground_blocks.clear()
    platform_blocks.clear()
    setup_level()
    hero = Hero(100, HEIGHT)
    play_music("background_music")


def draw_game():
    screen.clear()
    screen.blit("background", (0, 0))


    for ground in ground_blocks:
        ground.draw()

    for plat in platform_blocks:
        original_x = plat.x
        plat.x = plat.x - camera_x
        plat.draw()
        plat.x = original_x

    original_x = hero.actor.x
    hero.actor.x = hero.actor.x - camera_x
    hero.actor.draw()
    hero.actor.x = original_x

    for enemy in enemies:
        original_x = enemy.actor.x
        enemy.actor.x = enemy.actor.x - camera_x
        enemy.actor.draw()
        enemy.actor.x = original_x 

def update_game():
    if not hero.is_attacking:
        if keyboard.a or keyboard.left:
            hero.move("left")
            hero.direction = "left"
        elif keyboard.d or keyboard.right:
            hero.move("right")
            hero.direction = "right"
        else:
            hero.vx = 0

    hero.update()

    global camera_x
    camera_x = max(0, min(hero.actor.centerx - WIDTH // 2, LEVEL_WIDTH - WIDTH))


    if hero.is_attacking:
        hitbox = hero.attack_hitbox()
        for enemy in enemies:
            if enemy.alive:
                enemy_rect = Rect(enemy.actor.left, enemy.actor.top, enemy.actor.width, enemy.actor.height)
                if hitbox.colliderect(enemy_rect):
                    enemy.die()
                    enemy.alive = False


    for enemy in enemies:
        enemy.update()
        if enemy.alive and enemy.collide_with_hero(hero):
            global game_state
            game_state = "game_over"
            stop_music()
            play_sound("death") 

    if all(not enemy.alive for enemy in enemies):
        game_state = "victory"
        stop_music()

    pass

def draw_game_over():
    draw_game()

    screen.draw.text("Game Over", center=(WIDTH//2, HEIGHT//2 - 50), fontsize=60, color="red", owidth=1.0, ocolor="black")
    screen.draw.text("Pressione R para recomecar", center=(WIDTH//2, HEIGHT//2 + 20), fontsize=40, color="white", owidth=1.0, ocolor="black")

    menu_button = Rect((WIDTH // 2 - 100, HEIGHT // 2 + 60), (200, 50))
    screen.draw.filled_rect(menu_button, "gray")
    screen.draw.text("Menu", center=menu_button.center, fontsize=40, color="black")

    global menu_button_rect
    menu_button_rect = menu_button

def draw_victory():
    draw_game()

    screen.draw.text("Voce Venceu!", center=(WIDTH//2, HEIGHT//2 - 50), fontsize=60, color="green", owidth=1.0, ocolor="black")
    screen.draw.text("Clique para voltar ao Menu", center=(WIDTH//2, HEIGHT//2 + 20), fontsize=40, color="white", owidth=1.0, ocolor="black")

    victory_button = Rect((WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 83))
    screen.blit("menu", (menu_buttons["menu"].left, menu_buttons["menu"].top))

    global victory_button_rect
    victory_button_rect = victory_button


background = Actor("background", topleft=(0, 0))

ground_blocks = []
platform_blocks = []

TILE_WIDTH = 64
TILE_HEIGHT = 64

def setup_level():
    global enemies

    ground_y = HEIGHT - TILE_HEIGHT

    for x in range(0, LEVEL_WIDTH, TILE_WIDTH):
        ground = Actor("ground", topleft=(x, ground_y))
        ground_blocks.append(ground)

    platform_positions = [
        (200, 340),
        (400, 250),
        (600, 340),
        (900, 320),
        (1200, 270),
        (1600, 200),
        (1800, 350),
        (2000, 300),
        (2200, 280),
        (2300, 350) 
    ]

    platform_blocks.clear()

    for pos in platform_positions:
        plat = Actor("platform", topleft=pos)
        platform_blocks.append(plat)

    enemies = [
        ZombieWoman(300, HEIGHT - TILE_HEIGHT - 31, 200, 800),
        Enemy(550, HEIGHT - TILE_HEIGHT - 31, 400, 1000),
        ZombieWoman(800, HEIGHT - TILE_HEIGHT - 31, 750, 1500),
        ZombieFourLegs(1100, HEIGHT - TILE_HEIGHT - 31, 1050, 2400)
    ]


class Hero:
    def __init__(self, x, y):
        self.vx = 0
        self.vy = 0
        self.is_jumping = False
        self.on_ground = False
        self.is_attacking = False
        self.direction = "right"
        self.actor = Actor("samurai_idle_right_1", (x, y))

        self.idle_frames = {
            "right" : [f"samurai_idle_right_{i}" for i in range(1, 6)],
            "left" : [f"samurai_idle_left_{i}" for i in range(1, 6)]
        }

        self.run_frames = {
            "right" : [f"samurai_run_right_{i}" for i in range(1, 8)],
            "left" : [f"samurai_run_left_{i}" for i in range(1, 8)]
        }

        self.attack_frames = {
            "right" : [f"samurai_attack_right_{i}" for i in range(1, 10)],
            "left" : [f"samurai_attack_left_{i}" for i in range(1, 10)]
        }

        self.attack_frame_index = 0
        self.attack_timer = 0

        self.frame_index = 0
        self.idle_timer = 0
        self.idle_speed = 0.3

        self.run_timer = 0
        self.run_speed = 0.08
        self.state = "idle"

    def update(self):
        self.vy += 0.3
        self.actor.y += self.vy
        self.actor.x += self.vx
        self.on_ground = False

        if hero.vx != 0:
            self.state = 'running'
        else:
            self.state = 'idle'

        if self.actor.left < 0:
            self.actor.left = 0
        elif self.actor.right > LEVEL_WIDTH:
            self.actor.right = LEVEL_WIDTH
       
        for ground in ground_blocks:
            if self.vy > 0 and self.collide_with(ground):
                self.actor.bottom = ground.top
                self.vy = 0
                self.on_ground = True
                break

        for plat in platform_blocks:
            if self.vy > 0 and self.collide_with(plat):
                if self.actor.bottom <= plat.top + 10:
                    self.actor.bottom = plat.top
                    self.vy = 0
                    self.on_ground = True
                    break

        if self.is_attacking:
            self.attack_timer += 1
            if self.attack_timer >= 5:
                self.attack_timer = 0
                self.attack_frame_index += 1
                if self.attack_frame_index >= len(self.attack_frames[self.direction]):
                    self.is_attacking = False
                    self.attack_frame_index = 0
                else:
                    self.actor.image = self.attack_frames[self.direction][self.attack_frame_index]
            return

        if self.state == "idle":
            self.idle_timer += 1 / 60
            if self.idle_timer >= self.idle_speed:
                self.idle_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.idle_frames[self.direction])
                self.actor.image = self.idle_frames[self.direction][self.frame_index]
        elif self.state == "running":
            self.run_timer += 1 / 60
            if self.run_timer >= self.run_speed:
                self.run_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.run_frames[self.direction])
                self.actor.image = self.run_frames[self.direction][self.frame_index]


    def move(self, direction):
        speed = 3
        if direction == "left":
            self.vx = -speed
            self.direction = "left"
        elif direction == "right":
            self.vx = speed
            self.direction = "right"

    def jump(self):
        if self.on_ground:
            self.vy = -8
            self.on_ground = False
            play_sound("jump")

    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_frame_index = 0
            self.attack_timer = 0
            self.actor.image = self.attack_frames[self.direction][0]
            self.vx = 0
            play_sound("swordslash")
                    
    def attack_hitbox(self):
        offset = 10
        if self.direction == "right":
            return Rect(self.actor.right, self.actor.top, offset, self.actor.height)
        else:
            return Rect(self.actor.left - offset, self.actor.top, offset, self.actor.height)

    def collide_with(self, block):
        return self.actor.colliderect(block)

class Enemy:
    def __init__(self, x, y, territory_start, territory_end):
        self.actor = Actor("zombie_run_right_1", (x, y))
        self.vx = 1
        self.alive = True
        self.death_bottom_y = None

        self.is_dying = False
        self.death_frame_index = 0
        self.death_timer = 0
        self.death_speed = 0.12

        self.territory_start = territory_start
        self.territory_end = territory_end

        self.run_frames = {
            "right" : [f"zombie_run_right_{i}" for i in range(1, 8)],
            "left" : [f"zombie_run_left_{i}" for i in range(1, 8)]
        }
        self.death_frames = {
            "right" : [f"zombie_die_right_{i}" for i in range(1, 6)],
            "left" : [f"zombie_die_left_{i}" for i in range(1, 6)]
        }

        self.current_frame = 0
        self.frame_timer = 0
        self.direction = "right"

    def update(self):
        if not self.alive:
            if self.is_dying:
                self.death_timer += 1 / 60
                
                if self.death_timer >= self.death_speed:
                    self.death_timer = 0
                    self.death_frame_index += 1
                    frames = self.death_frames[self.direction]
                    if self.death_frame_index < len(frames):
                        self.actor.image = frames[self.death_frame_index]
                        if self.death_bottom_y is not None:
                            self.actor.bottom = self.death_bottom_y
                    else:
                        self.is_dying = False
                        self.death_frame_index = len(frames) - 1

            return

        if self.actor.x <= self.territory_start:
            self.vx = abs(self.vx)
            self.direction = "right"
        elif self.actor.x >= self.territory_end:
            self.vx = -abs(self.vx)
            self.direction = "left"

        self.actor.x += self.vx

        frames = self.run_frames[self.direction] if self.vx != 0 else self.idle_frames[self.direction]

        self.frame_timer += 1 / 60
        if self.frame_timer >= 0.15:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.actor.image = frames[self.current_frame]


    def collide_with_hero(self, hero):
        dx = abs(self.actor.x - hero.actor.x)
        dy = abs(self.actor.y - hero.actor.y)
        
        return dx < 30 and dy < 40
    
    def die(self):
        self.is_dying = True
        self.vx = 0
        self.alive = False
        self.death_frame_index = 0
        self.death_timer = 0

        self.death_bottom_y = self.actor.bottom
        self.actor.image = self.death_frames[self.direction][0]
        self.actor.bottom = self.death_bottom_y


class ZombieWoman(Enemy):
    def __init__(self, x, y, territory_start, territory_end):
        super().__init__(x, y, territory_start, territory_end)

        self.run_frames = {
            "right": [f"zombiewoman_run_right_{i}" for i in range(1, 7)],
            "left": [f"zombiewoman_run_left_{i}" for i in range(1, 7)]
        }
        self.death_frames = {
            "right": [f"zombiewoman_die_right_{i}" for i in range(1, 6)],
            "left": [f"zombiewoman_die_left_{i}" for i in range(1, 6)]
        }

        self.actor.image = self.run_frames[self.direction][0]
        self.detection_range = 200
        self.following_hero = False

    def update(self):
        if not self.alive:
            super().update()
            return

        distance_to_hero = abs(self.actor.x - hero.actor.x)

        if distance_to_hero < self.detection_range:
            self.following_hero = True
        else:
            self.following_hero = False

        if self.following_hero:
            if self.actor.x < hero.actor.x:
                self.vx = 1
                self.direction = "right"
            else:
                self.vx = -1
                self.direction = "left"
        else:
            if self.actor.x <= self.territory_start:
                self.vx = 1
                self.direction = "right"
            elif self.actor.x >= self.territory_end:
                self.vx = -1
                self.direction = "left"

        self.actor.x += self.vx

        frames = self.run_frames[self.direction]
        self.frame_timer += 1 / 60
        if self.frame_timer >= 0.12:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.actor.image = frames[self.current_frame]
            


class ZombieFourLegs(Enemy):
    def __init__(self, x, y, territory_start, territory_end):
        super().__init__(x, y, territory_start, territory_end)

        self.run_frames = {
            "right": [f"zombiefour_run_right_{i}" for i in range(1, 10)],
            "left": [f"zombiefour_run_left_{i}" for i in range(1, 10)]
        }
        self.death_frames = {
            "right": [f"zombiefour_die_right_{i}" for i in range(1, 6)],
            "left": [f"zombiefour_die_left_{i}" for i in range(1, 6)]
        }

        self.actor.image = self.run_frames[self.direction][0]
        self.vx = 3
        self.actor.bottom = y + 35


pgzrun.go()