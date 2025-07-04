import pgzrun

alien = Actor('alien')
alien.topright = 0, 250

WIDTH = 800
HEIGHT = 500
TITLE = "Roguelike Adventure"

def draw():
    screen.clear()
    alien.draw()
    screen.draw.circle((400, 300), 30, 'blue')

def update():
    alien.left += 2
    if alien.left > WIDTH:
        alien.right = 0
    on_touch_circle()

def on_touch_circle():
    if alien.left == 350:
        set_alien_hurt()

def on_mouse_down(pos):
    if alien.collidepoint(pos):
        set_alien_hurt()

def set_alien_hurt():
    alien.image = 'alien_hurt'
    sounds.loli.play()
    clock.schedule_unique(set_alien_normal, 1.0)

def set_alien_normal():
    alien.image = 'alien'

pgzrun.go()
