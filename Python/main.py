import pgzrun
import random
import math
from pygame import Rect

# --- CONFIGURAÇÕES INICIAIS ---

TITLE = "Ninja vs Zombies"
WIDTH = 800
HEIGHT = 480
LEVEL_WIDTH = 2400

# --- ESTADOS DO JOGO ---

game_state = "menu"
camera_x = 0
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

    if game_state == "game_over":
        if menu_button_rect.collidepoint(pos):
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
        ground.draw()  # normalmente chão e plataforma não precisam de câmera

    for plat in platform_blocks:
        original_x = plat.x
        plat.x = plat.x - camera_x
        plat.draw()
        plat.x = original_x

    # Ajustar posição do herói para câmera
    original_x = hero.actor.x
    hero.actor.x = hero.actor.x - camera_x
    hero.actor.draw()
    hero.actor.x = original_x  # restaurar posição

    for enemy in enemies:
        original_x = enemy.actor.x
        enemy.actor.x = enemy.actor.x - camera_x
        enemy.actor.draw()
        enemy.actor.x = original_x

    screen.draw.text(f"Hero Direction: {hero.direction}", (10, 10), color="white")
    screen.draw.text(f"Hero Flip: {hero.actor.flip_x}", (10, 30), color="white")
    
    for i, enemy in enumerate(enemies):
        screen.draw.text(f"Enemy {i} Dir: {enemy.direction}", (10, 60 + i*20), color="white")
        screen.draw.text(f"Enemy {i} Flip: {enemy.actor.flip_x}", (10, 80 + i*20), color="white")

def update_game():
    if not hero.is_attacking:
        if keyboard.a or keyboard.left:
            hero.move("left")
            hero.direction = "left"
        elif keyboard.d or keyboard.right:
            hero.move("right")
            hero.direction = "right"
        else:
            hero.vx = 0  # parado

    hero.update()

    global camera_x

# Centraliza o herói no meio da tela, mas com limites nas bordas do mapa
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
            # Aqui você pode implementar uma lógica de game over
            global game_state
            game_state = "game_over"
            stop_music()  # Para a música
            play_sound("death") 

    # Vamos atualizar a lógica do jogo aqui
    pass

def draw_game_over():
    draw_game()  # Desenha o jogo normalmente como estava

    # Sobrepõe o texto "Game Over"
    screen.draw.text("Game Over", center=(WIDTH//2, HEIGHT//2 - 50), fontsize=60, color="red", owidth=1.0, ocolor="black")
    screen.draw.text("Pressione R para recomecar", center=(WIDTH//2, HEIGHT//2 + 20), fontsize=40, color="white", owidth=1.0, ocolor="black")

    menu_button = Rect((WIDTH // 2 - 100, HEIGHT // 2 + 60), (200, 50))
    screen.draw.filled_rect(menu_button, "gray")
    screen.draw.text("Menu", center=menu_button.center, fontsize=40, color="black")

    # Salvar posição do botão para detecção de clique
    global menu_button_rect
    menu_button_rect = menu_button


# --- CENARIO ---

background = Actor("background", topleft=(0, 0))

ground_blocks = []  # blocos do chão
platform_blocks = []  # plataformas suspensas

TILE_WIDTH = 64  # largura dos blocos
TILE_HEIGHT = 64

def setup_level():
    global enemies

    """Cria o chão e plataformas para o herói andar/pular"""
    ground_y = HEIGHT - TILE_HEIGHT

    # Chão cobrindo toda a largura da tela
    for x in range(0, LEVEL_WIDTH, TILE_WIDTH):
        ground = Actor("ground", topleft=(x, ground_y))
        ground_blocks.append(ground)

    # Adiciona algumas plataformas suspensas
    # (posição X, posição Y)
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

    # Limpa a lista global antes de preencher
    platform_blocks.clear()

    # Cria atores das plataformas e adiciona na lista global
    for pos in platform_positions:
        plat = Actor("platform", topleft=pos)
        platform_blocks.append(plat)

    enemies = [
        ZombieWoman(300, HEIGHT - TILE_HEIGHT - 31, 200, 800),
        Enemy(550, HEIGHT - TILE_HEIGHT - 31, 400, 1000),
        ZombieWoman(800, HEIGHT - TILE_HEIGHT - 31, 750, 1500),
        ZombieFourLegs(1100, HEIGHT - TILE_HEIGHT - 31, 1050, 2400)
    ] 

# --- PERSONAGENS ---

class Hero:
    def __init__(self, x, y):
        self.vx = 0  # velocidade horizontal
        self.vy = 0  # velocidade vertical
        self.is_jumping = False
        self.on_ground = False
        self.is_attacking = False
        self.direction = "right"  # direção atual para virar o sprite
        self.actor = Actor("samurai_idle_1", (x, y))  # sprite parado

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
        self.vy += 0.3  # força da gravidade
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
        elif self.actor.right > LEVEL_WIDTH:
            self.actor.right = LEVEL_WIDTH
       
        # colisão com chão
        for ground in ground_blocks:
            if self.vy > 0 and self.collide_with(ground):
                self.actor.bottom = ground.top
                self.vy = 0
                self.on_ground = True
                break

        # colisão com plataformas
        for plat in platform_blocks:
            if self.vy > 0 and self.collide_with(plat):
                # Verifica se o herói está caindo e acima da plataforma
                if self.actor.bottom <= plat.top + 10:
                    self.actor.bottom = plat.top
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
                self.actor.flip_x = (self.direction == "left")
                print(f"Hero idle: image={self.actor.image}, direction={self.direction}, flip_x={self.actor.flip_x}")
        elif self.state == "running":
            self.run_timer += 1 / 60
            if self.run_timer >= self.run_speed:
                self.run_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.run_frames)
                self.actor.image = self.run_frames[self.frame_index]
                self.actor.flip_x = (self.direction == "left")


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
            self.actor.image = self.attack_frames[0]
            self.vx = 0
            play_sound("swordslash")
                    
    def attack_hitbox(self):
        offset = 5
        if self.direction == "right":
            return Rect(self.actor.right, self.actor.top, offset, self.actor.height)
        else:
            return Rect(self.actor.left - offset, self.actor.top, offset, self.actor.height)

    def collide_with(self, block):
        return self.actor.colliderect(block)

class Enemy:
    def __init__(self, x, y, territory_start, territory_end):
        self.actor = Actor("zombie_idle_1", (x, y))
        self.vx = 1
        self.alive = True
        self.death_bottom_y = None

        self.is_dying = False
        self.death_frame_index = 0
        self.death_timer = 0
        self.death_speed = 0.12

        self.territory_start = territory_start
        self.territory_end = territory_end

        self.idle_frames = [f"zombie_idle_{i}" for i in range(1, 8)]
        self.run_frames = [f"zombie_run_{i}" for i in range(1, 8)]
        self.death_frames = [f"zombie_die_{i}" for i in range(1, 6)]

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
                    if self.death_frame_index < len(self.death_frames):
                        self.actor.image = self.death_frames[self.death_frame_index]
                        self.actor.flip_x = (self.direction == "left")
                        if self.death_bottom_y is not None:
                            self.actor.bottom = self.death_bottom_y
                    else:
                        self.death_frame_index = len(self.death_frames) - 1
                        self.is_dying = False
            return

        if self.actor.x <= self.territory_start:
            self.vx = abs(self.vx)
            self.direction = "right"
        elif self.actor.x >= self.territory_end:
            self.vx = -abs(self.vx)
            self.direction = "left"

        self.actor.x += self.vx

        # animação
        self.frame_timer += 1
        if self.frame_timer >= 10:
            self.frame_timer = 0
            frames = self.run_frames if self.vx != 0 else self.idle_frames
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.actor.image = frames[self.current_frame]
            self.actor.flip_x = (self.direction == "left")


    def collide_with_hero(self, hero):
        # Distância entre os centros dos sprites
        dx = abs(self.actor.x - hero.actor.x)
        dy = abs(self.actor.y - hero.actor.y)
        
        # Define o alcance de ataque mais realista
        return dx < 30 and dy < 40
    
    def die(self):
        self.is_dying = True
        self.vx = 0
        self.alive = False
        self.death_frame_index = 0
        self.death_timer = 0

        self.death_bottom_y = self.actor.bottom  # SALVA posição exata do chão
        self.actor.image = self.death_frames[0]
        self.actor.flip_x = (self.direction == "left")
        self.actor.bottom = self.death_bottom_y  # Garante que já comece certo


class ZombieWoman(Enemy):
    def __init__(self, x, y, territory_start, territory_end):
        super().__init__(x, y, territory_start, territory_end)
        self.run_frames = [f"zombiewoman_run_{i}" for i in range(1, 7)]
        self.death_frames = [f"zombiewoman_die_{i}" for i in range(1, 6)]
        self.actor.image = self.run_frames[0]
        self.actor.flip_x = (self.direction == "left")
        self.detection_range = 200  # distância de "visão"
        self.following_hero = False

    def update(self):
        if not self.alive:
            super().update()
            return

        # Distância horizontal entre ela e o herói
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
            # Patrulha padrão do Enemy
            if self.actor.x <= self.territory_start:
                self.vx = 1
                self.direction = "right"
            elif self.actor.x >= self.territory_end:
                self.vx = -1
                self.direction = "left"

        # Movimento
        self.actor.x += self.vx

        # Animação
        self.frame_timer += 1
        if self.frame_timer >= 10:
            self.frame_timer = 0
            frames = self.run_frames
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.actor.image = frames[self.current_frame]
            if self.direction == "left":
                self.scale_x = -1


class ZombieFourLegs(Enemy):
    def __init__(self, x, y, territory_start, territory_end):
        super().__init__(x, y, territory_start, territory_end)
        # Sprites específicos para zumbi de quatro patas
        #self.idle_frames = [f"zombiefour_idle_{i}" for i in range(1, 8)]
        self.run_frames = [f"zombiefour_run_{i}" for i in range(1, 10)]
        self.death_frames = [f"zombiefour_die_{i}" for i in range(1, 6)]
        self.actor.image = self.run_frames[0]
        self.vx = 3  # mais rápido
        self.actor.bottom = y + 50


pgzrun.go()



# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# COISAS A FAZER DEPOIS DO JOGO PRONTO

# CORRIGIR ANIMACOES PARA ESQUERDA
# AJUSTAR BOTOES DO MENU
# CORRIGIR ORGANIZACAO DAS PASTAS E DO CODIGO
