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
        elif menu_buttons["quit"].collidepoint(pos):
            quit()


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
    # Aqui vamos inicializar o herói, inimigos, mapa, etc.

def draw_game():
    screen.clear()
    screen.blit("background", (0, 0))

    for ground in ground_blocks:
        ground.draw()

    for plat in platform_blocks:
        plat.draw()

    hero.draw()
    # Vamos desenhar a fase, herói, inimigos, etc.

def update_game():
    if keyboard.a:
        hero.move("left")
    elif keyboard.d:
        hero.move("right")
    else:
        hero.vx = 0  # parado

    hero.update()

    # Vamos atualizar a lógica do jogo aqui
    pass

def draw_game_over():
    screen.clear()
    screen.draw.text("Game Over", center=(WIDTH//2, HEIGHT//2), fontsize=60, color="white")

def on_key_down(key):
    if game_state == "playing":
        if key == keys.SPACE:
            hero.jump()

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
        self.direction = "right"  # direção atual para virar o sprite
        self.actor = Actor("warrior_idle_1", (x, y))  # sprite parado
        self.vy = 0  # velocidade vertical
        self.is_jumping = False
        self.on_ground = False
        self.frames_idle = [
            "warrior_idle_1",
            "warrior_idle_2",
            "warrior_idle_3",
            "warrior_idle_4",
            "warrior_idle_5",
            "warrior_idle_6"
        ]
        self.frames_run = [
            "warrior_run_1",
            "warrior_run_2",
            "warrior_run_3",
            "warrior_run_4",
            "warrior_run_5",
            "warrior_run_6"
        ]
        self.current_frame = 0
        self.frame_timer = 0
        self.flip_manually = True

    def update(self):
        # gravidade
        self.vy += 0.5  # força da gravidade
        self.actor.y += self.vy
        self.on_ground = False

        # movimento horizontal
        self.actor.x += self.vx

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
        
        # animacao
        self.frame_timer += 1
        if self.frame_timer >= 6:
            self.frame_timer = 0

            if self.vx != 0:  # está se movendo
                frames = self.frames_run
            else:
                frames = self.frames_idle

            self.current_frame = (self.current_frame + 1) % len(frames)
            self.actor.image = frames[self.current_frame]

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

    def collide_with(self, block):
        return self.actor.colliderect(block)

    def draw(self):
        self.actor.flip_x = (self.direction == "left")
        self.actor.draw()

pgzrun.go()



# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# COISAS A FAZER DEPOIS DO JOGO PRONTO
#AJUSTAR BACKGROU
#AJUSTAR BOTOES
#
#
#