import pgzrun
import random
import math
from pygame import Rect

# --- CONFIGURAÇÕES INICIAIS ---

TITLE = "Ninja vs Zombies"
WIDTH = 800
HEIGHT = 480

# --- ESTADOS DO JOGO ---

game_state = "menu"
sound_on = True
hero = None

# --- ATIVOS DO MENU ---

menu_buttons = {
    "start": Rect((WIDTH//2 - 75, 150, 150, 40)),
    "toggle_sound": Rect((WIDTH//2 - 75, 210, 150, 40)),
    "quit": Rect((WIDTH//2 - 75, 270, 150, 40))
}


# --- FUNÇÕES PADRÃO ---

def draw():
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        draw_game()
    elif game_state == "game_over":
        draw_game_over()

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

def play_sound(name):
    if sound_on:
        getattr(sounds, name).play()

def play_music(name):
    if sound_on:
        music.play(name)

def stop_music():
    music.stop()


# --- FUNÇÕES DO MENU ---

def draw_menu():
    screen.clear()
    screen.fill((30, 30, 30))
    screen.draw.text("Ninja vs Zombies", center=(WIDTH//2, 80), fontsize=48, color="white")
    
    screen.draw.filled_rect(menu_buttons["start"], "darkgreen")
    screen.draw.text("Start Game", center=menu_buttons["start"].center, color="white")
    
    screen.draw.filled_rect(menu_buttons["toggle_sound"], "navy")
    sound_text = "Sound: ON" if sound_on else "Sound: OFF"
    screen.draw.text(sound_text, center=menu_buttons["toggle_sound"].center, color="white")
    
    screen.draw.filled_rect(menu_buttons["quit"], "darkred")
    screen.draw.text("Quit", center=menu_buttons["quit"].center, color="white")


# --- FUNÇÕES DO JOGO ---

def start_game():
    global game_state, hero, enemies
    game_state = "playing"
    ground_blocks.clear()
    platform_blocks.clear()
    setup_level()
    hero = Hero(100, HEIGHT)
    enemies = [
        Enemy(300, HEIGHT - TILE_HEIGHT - 31, 250, 400),
        Enemy(550, HEIGHT - TILE_HEIGHT - 31, 500, 650)
    ]
    play_music("background_music")


    # Aqui vamos inicializar o herói, inimigos, mapa, etc.

def draw_game():
    screen.clear()
    screen.blit("background", (0, 0))

    for ground in ground_blocks:
        ground.draw()

    for plat in platform_blocks:
        plat.draw()

    hero.draw()

    for enemy in enemies:
        enemy.draw()

    # Vamos desenhar a fase, herói, inimigos, etc.

def update_game():
    if not hero.is_attacking:
        if keyboard.a or keyboard.left:
            hero.move("left")
        elif keyboard.d or keyboard.right:
            hero.move("right")
        else:
            hero.vx = 0  # parado

    hero.update()

    if hero.is_attacking:
        hitbox = hero.attack_hitbox()
        for enemy in enemies:
            if enemy.alive:
                enemy_rect = Rect(enemy.actor.left, enemy.actor.top, enemy.actor.width, enemy.actor.height)
                if hitbox.colliderect(enemy_rect):
                    enemy.alive = False
                    play_sound("swordslash")


    for enemy in enemies:
        enemy.update()
        if enemy.alive and enemy.collide_with_hero(hero):
            # Aqui você pode implementar uma lógica de game over
            global game_state
            game_state = "game_over"

    # Vamos atualizar a lógica do jogo aqui
    pass

def draw_game_over():
    screen.clear()
    screen.draw.text("Game Over", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")

def on_key_down(key):
    if game_state == "playing":
        if key == keys.SPACE:
            hero.jump()
        if key == keys.K:
            hero.attack()


# --- CENARIO ---

background = Actor("background", topleft=(0, 0))

ground_blocks = []  # blocos do chão
platform_blocks = []  # plataformas suspensas

TILE_WIDTH = 64  # largura dos blocos
TILE_HEIGHT = 64

def setup_level():
    """Cria o chão e plataformas para o herói andar/pular"""
    ground_y = HEIGHT - TILE_HEIGHT

    # Chão cobrindo toda a largura da tela
    for x in range(0, WIDTH, TILE_WIDTH):
        ground = Actor("ground", topleft=(x, ground_y))
        ground_blocks.append(ground)

    # Adiciona algumas plataformas suspensas
    # (posição X, posição Y)
    positions = [
        (200, 340),
        (400, 250),
        (600, 340)
    ]

    for pos in positions:
        plat = Actor("platform", topleft=pos)
        platform_blocks.append(plat)

# --- PERSONAGENS ---

class Hero:
    def __init__(self, x, y):
        self.vx = 0  # velocidade horizontal
        self.vy = 0  # velocidade vertical
        self.is_jumping = False
        self.on_ground = False
        self.direction = "right"  # direção atual para virar o sprite
        self.actor = Actor("samurai_idle_1", (x, y))  # sprite parado
        self.is_attacking = False

        self.idle_frames = [f"samurai_idle_{i}" for i in range(1, 6)]
        self.run_frames = [f"samurai_run_{i}" for i in range(1, 8)]
        self.attack_frames = [f"samurai_attack_{i}" for i in range(1, 10)]

        self.attack_frame_index = 0
        self.attack_timer = 0

        self.frame_index = 0
        self.idle_timer = 0
        self.idle_speed = 0.3  # menor = mais lento

        self.run_timer = 0
        self.run_speed = 0.08  #  mais rápido que o idle

        self.state = "idle"  # ou "run"

    def update(self):
        # gravidade
        self.vy += 0.5  # força da gravidade
        self.actor.y += self.vy
        self.actor.x += self.vx
        self.on_ground = False

        if hero.vx != 0:
            self.state = 'running'
        else:
            self.state = 'idle'

        # impedir sair da tela
        if self.actor.left < 0:
            self.actor.left = 0
        elif self.actor.right > WIDTH:
            self.actor.right = WIDTH
       
        # colisão com chão
        for ground in ground_blocks:
            if self.collide_with(ground):
                self.actor.bottom = ground.top
                self.vy = 0
                self.on_ground = True
                break

        # colisão com plataformas
        for plat in platform_blocks:
            if self.vy > 0 and self.collide_with(plat):
                # Verifica se o herói está caindo e acima da plataforma
                if self.actor.bottom <= plat.top + 10:
                    self.actor.bottom = plat.top + 1
                    self.vy = 0
                    self.on_ground = True
                    break

        # Animacao de ataque
        if self.is_attacking:
            self.attack_timer += 1
            if self.attack_timer >= 5:
                self.attack_timer = 0
                self.attack_frame_index += 1
                if self.attack_frame_index >= len(self.attack_frames):
                    self.is_attacking = False
                    self.attack_frame_index = 0
                else:
                    self.actor.image = self.attack_frames[self.attack_frame_index]
            return  # Impede que outras animações rodem enquanto ataca

        # Animacao de andar e correr

        if self.state == "idle":
            self.idle_timer += 1 / 60  # considerando 60 FPS
            if self.idle_timer >= self.idle_speed:
                self.idle_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.idle_frames)
                self.actor.image = self.idle_frames[self.frame_index]

        elif self.state == "running":
            self.run_timer += 1 / 60
            if self.run_timer >= self.run_speed:
                self.run_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.run_frames)
                self.actor.image = self.run_frames[self.frame_index]


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
            self.vy = -10
            self.on_ground = False
            play_sound("jump")

    def attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_frame_index = 0
            self.attack_timer = 0
            self.actor.image = self.attack_frames[0]
            self.vx = 0
            play_sound("swordslash")
                    
    def attack_hitbox(self):
        offset = 40
        if self.direction == "right":
            return Rect(self.actor.right, self.actor.top, offset, self.actor.height)
        else:
            return Rect(self.actor.left - offset, self.actor.top, offset, self.actor.height)

    def collide_with(self, block):
        return self.actor.colliderect(block)

    def draw(self):
        self.actor.flip_x = (self.direction == "left")
        self.actor.draw()

class Enemy:
    def __init__(self, x, y, territory_start, territory_end):
        self.actor = Actor("zombie_idle_1", (x, y))
        self.vx = 1  # velocidade inicial
        self.alive = True

        self.territory_start = territory_start
        self.territory_end = territory_end

        self.idle_frames = [f"zombie_idle_{i}" for i in range(1, 8)]
        self.run_frames = [f"zombie_run_{i}" for i in range(1, 8)]

        self.current_frame = 0
        self.frame_timer = 0
        self.direction = "right"

    def update(self):
        if not self.alive:
            return
        # movimento horizontal
        self.actor.x += self.vx

        # inverter direção ao chegar nas bordas do território
        if self.actor.x < self.territory_start:
            self.vx = abs(self.vx)
            self.direction = "right"
        elif self.actor.x > self.territory_end:
            self.vx = -abs(self.vx)
            self.direction = "left"

        # animação
        self.frame_timer += 1
        if self.frame_timer >= 10:
            self.frame_timer = 0
            frames = self.run_frames if self.vx != 0 else self.idle_frames
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.actor.image = frames[self.current_frame]

    def draw(self):
        if not self.alive:
            return
        self.actor.flip_x = (self.direction == "left")
        self.actor.draw()

    def collide_with_hero(self, hero):
        return self.actor.colliderect(hero.actor)


pgzrun.go()



# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# COISAS A FAZER DEPOIS DO JOGO PRONTO
#AJUSTAR BACKGROUD PARA PARALAX
#AJUSTAR BOTOES
#ARRUMAR QUANTIDADE DE SPRITES DE CORRIDA
#
#