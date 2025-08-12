# pip install PyOpenGL PyOpenGL_accelerate
# python catch_diamonds_step3_full_game.py

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import time
import random

SCREEN_HEIGHT = 800  
SCREEN_WIDTH = 600   
BUTTON_POSITION_Y = SCREEN_HEIGHT - 50  
BUTTON_DIMENSION = 36  

# Zone-0 and map other zones to Zone-0.

def find_zone(x1, y1, x2, y2):
  
    dx = (x2 - x1)
    dy = (y2 - y1)
    adx = abs(dx)
    ady = abs(dy)
    # If |dx| >= |dy|, the line is shallow (zones 0,3,4,7)
    if adx >= ady:
        if dx >= 0 and dy >= 0:
            return 0
        if dx < 0 and dy >= 0:
            return 3
        if dx < 0 and dy < 0:
            return 4
        return 7
    else:
        # steep lines (zones 1,2,5,6)
        if dx >= 0 and dy >= 0:
            return 1
        if dx < 0 and dy >= 0:
            return 2
        if dx < 0 and dy < 0:
            return 5
        return 6

def to_zone0(zone, x, y):
    
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return y, -x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return -y, x
    if zone == 7:
        return x, -y
    return x,y

def from_zone0(zone, x, y):
  
    if zone == 0:
        return x, y
    if zone == 1:
        return y, x
    if zone == 2:
        return -y, x
    if zone == 3:
        return -x, y
    if zone == 4:
        return -x, -y
    if zone == 5:
        return -y, -x
    if zone == 6:
        return y, -x
    if zone == 7:
        return x, -y
    return x,y

def midpoint_zone0(x1, y1, x2, y2, put_pixel):

    dx = x2 - x1
    dy = y2 - y1
    # degenerate: single point
    if dx == 0 and dy == 0:
        put_pixel(x1, y1)
        return
    # if dx==0 after zone mapping, treat as vertical line
    if dx == 0:
        step = 1 if y2 >= y1 else -1
        y = y1
        while True:
            put_pixel(x1, y)
            if y == y2:
                break
            y += step
        return
    d = 2 * dy - dx
    incE = 2 * dy # increment for east step
    incNE = 2 * (dy - dx) #increment for north east step
    x = x1 #starting x
    y = y1
    while x <= x2:
        put_pixel(x, y)
        if d > 0:
            d += incNE
            y += 1
        else:
            d += incE
        x += 1

def draw_line(x1, y1, x2, y2, color=(1.0, 1.0, 1.0)):
    #a line between (x1,y1) and (x2,y2)
    glColor3f(*color)
    zone = find_zone(x1, y1, x2, y2)
    ax1, ay1 = to_zone0(zone, x1, y1)
    ax2, ay2 = to_zone0(zone, x2, y2)
 
    if ax1 > ax2: # left-to-right in zone0
        ax1, ax2, ay1, ay2 = ax2, ax1, ay2, ay1

    def put_zone0(px, py): # back to original zone & plot 
        ox, oy = from_zone0(zone, px, py)
        glBegin(GL_POINTS)
        glVertex2i(int(round(ox)), int(round(oy)))
        glEnd()

    midpoint_zone0(int(round(ax1)), int(round(ay1)), int(round(ax2)), int(round(ay2)), put_zone0)

# ---------------- Game constants ----------------

CATCHER_WIDTH = 150  
CATCHER_HEIGHT = 20  
CATCHER_BASE_Y = 50  
DIAMOND_EDGE = 24  

BUTTON_LEFT_X = 60  
BUTTON_CENTER_X = SCREEN_WIDTH // 2 
BUTTON_RIGHT_X = SCREEN_WIDTH - 60 

# ---------------- Game state ----------------
catcher_x = SCREEN_WIDTH // 2  
catcher_color = (1.0, 1.0, 1.0)
keys = {'left': False, 'right': False}

diamond_x = random.randint(DIAMOND_EDGE, SCREEN_WIDTH - DIAMOND_EDGE)
diamond_y = SCREEN_HEIGHT - 60
diamond_speed = 120.0  # px/sec 
diamond_color = (1.0, 1.0, 1.0)

score = 0
is_game_over = False
is_playing = True
last_time = None

# ---------------- Utility functions ----------------

def random_bright_color(): # random color diamond .
    return (random.uniform(0.6, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0))

def draw_catcher(cx, color=None):
   
    if color is None:
        color = (1.0, 1.0, 1.0)
    half = CATCHER_WIDTH // 2
    left = cx - half
    right = cx + half
    top = CATCHER_BASE_Y + CATCHER_HEIGHT
    # left vertical
    draw_line(left, CATCHER_BASE_Y, left, top, color)
    # left slanted up towards middle
    draw_line(left, top, cx - 14, top + 12, color)
    # middle top horizontal small segment
    draw_line(cx - 14, top + 12, cx + 14, top + 12, color)
    # right slanted down to right top
    draw_line(cx + 14, top + 12, right, top, color)
    # right vertical down
    draw_line(right, top, right, CATCHER_BASE_Y, color)


def draw_diamond(cx, cy, size, color=None):

    if color is None:
        color = (1.0, 1.0, 1.0)
    half = size // 2
    top = (cx, cy + half)
    right = (cx + half, cy)
    bottom = (cx, cy - half)
    left = (cx - half, cy)
    draw_line(top[0], top[1], right[0], right[1], color)
    draw_line(right[0], right[1], bottom[0], bottom[1], color)
    draw_line(bottom[0], bottom[1], left[0], left[1], color)
    draw_line(left[0], left[1], top[0], top[1], color)


def draw_left_arrow_icon(x, y, size):
    s = size // 2
    # three points forming a simple left arrowhead
    p1 = (x + s, y + s)
    p2 = (x - s, y)
    p3 = (x + s, y - s)
    teal = (0.0, 0.75, 0.72)
    draw_line(p1[0], p1[1], p2[0], p2[1], teal)
    draw_line(p2[0], p2[1], p3[0], p3[1], teal)


def draw_play_icon(x, y, size):

    s = size // 2
    p1 = (x - s//2, y - s)
    p2 = (x - s//2, y + s)
    p3 = (x + s, y)
    amber = (1.0, 0.7, 0.0)
    draw_line(p1[0], p1[1], p2[0], p2[1], amber)
    draw_line(p2[0], p2[1], p3[0], p3[1], amber)
    draw_line(p3[0], p3[1], p1[0], p1[1], amber)


def draw_pause_icon(x, y, size):
    
    s = size // 2
    amber = (1.0, 0.7, 0.0)
    bar_w = max(2, size // 8)
    # left bar
    draw_line(x - s + 3, y - s, x - s + 3, y + s, amber)
    draw_line(x - s + 3 + bar_w, y - s, x - s + 3 + bar_w, y + s, amber)
    # right bar
    draw_line(x + s - 3 - bar_w, y - s, x + s - 3 - bar_w, y + s, amber)
    draw_line(x + s - 3, y - s, x + s - 3, y + s, amber)


def draw_cross_icon(x, y, size):
    
    s = size // 2
    red = (1.0, 0.2, 0.2)
    draw_line(x - s, y - s, x + s, y + s, red)
    draw_line(x - s, y + s, x + s, y - s, red)

def draw_button(x, y, size, color):
    #square button 
    glColor3f(*color)  # Set the button color
    glBegin(GL_QUADS)  
    glVertex2f(x - size, y - size)
    glVertex2f(x + size, y - size)
    glVertex2f(x + size, y + size)
    glVertex2f(x - size, y + size)
    glEnd()

def draw_buttons():
    
    button_color = (0.0, 1.0, 0.0)  # Green

    # button (Restart)
    draw_button(BUTTON_LEFT_X, BUTTON_POSITION_Y, BUTTON_DIMENSION, button_color)

    #button (Play/Pause)
    draw_button(BUTTON_CENTER_X, BUTTON_POSITION_Y, BUTTON_DIMENSION, button_color)

    #button (Quit)
    draw_button(BUTTON_RIGHT_X, BUTTON_POSITION_Y, BUTTON_DIMENSION, button_color)

# ---------------- Collision (Axis Alined Bounding Box) ----------------

def has_collided(box1, box2):
    #take decision increse score or game over 
    return (box1['x'] < box2['x'] + box2['w'] and
            box1['x'] + box1['w'] > box2['x'] and
            box1['y'] < box2['y'] + box2['h'] and
            box1['y'] + box2['h'] > box2['y']) #collision happended when overlaps x,y direction

# ---------------- Input handlers ----------------

def keyboard(key, x, y):
    """Controls: ESC quits, R restarts, P pauses/plays."""
    global is_playing, score
        #key must be string
    if not isinstance(key, str):
        key = key.decode()

    # ESC key
    if key == '\x1b':  # ESC
        print(" game over", score)
        try:
            glutLeaveMainLoop()
        except:
            sys.exit(0)

    # Restart
    elif key.lower() == 'r':
        restart_game()

    # Pause / Play
    elif key.lower() == 'p':
        toggle_play_pause()



def special_down(key, x, y):
    if key == GLUT_KEY_LEFT:
        keys['left'] = True
    if key == GLUT_KEY_RIGHT:
        keys['right'] = True


def special_up(key, x, y):
    if key == GLUT_KEY_LEFT:
        keys['left'] = False
    if key == GLUT_KEY_RIGHT:
        keys['right'] = False


def mouse(button, state, mx, my):
    global is_playing
    # Only react on left-button press
    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
        return
    # convert y coordinate
    my = SCREEN_HEIGHT - my
    # left button bounds
    if (BUTTON_LEFT_X - BUTTON_DIMENSION <= mx <= BUTTON_LEFT_X + BUTTON_DIMENSION and
            BUTTON_POSITION_Y - BUTTON_DIMENSION <= my <= BUTTON_POSITION_Y + BUTTON_DIMENSION):
        # restart
        print('Starting Over')
        restart_game()
        return
    # center button bounds
    if (BUTTON_CENTER_X - BUTTON_DIMENSION <= mx <= BUTTON_CENTER_X + BUTTON_DIMENSION and
            BUTTON_POSITION_Y - BUTTON_DIMENSION <= my <= BUTTON_POSITION_Y + BUTTON_DIMENSION):
        toggle_play_pause()
        return
    # right button bounds
    if (BUTTON_RIGHT_X - BUTTON_DIMENSION <= mx <= BUTTON_RIGHT_X + BUTTON_DIMENSION and
            BUTTON_POSITION_Y - BUTTON_DIMENSION <= my <= BUTTON_POSITION_Y + BUTTON_DIMENSION):
        print('Goodbye', score)
        try:
            glutLeaveMainLoop()
        except Exception:
            sys.exit(0)

# ---------------- Game control helpers ----------------

def restart_game():

    global score, diamond_speed, is_game_over, is_playing, catcher_color, diamond_x, diamond_y
    score = 0
    diamond_speed = 120.0
    is_game_over = False
    is_playing = True
    catcher_color = (1.0, 1.0, 1.0)
    diamond_x = random.randint(DIAMOND_EDGE, SCREEN_WIDTH - DIAMOND_EDGE)
    diamond_y = SCREEN_HEIGHT - 60


def toggle_play_pause():
    
    global is_playing
    is_playing = not is_playing

# ---------------- Game update logic ----------------

def respawn_diamond():
    #respawn diamond random x and randm color."""
    global diamond_x, diamond_y, diamond_color
    diamond_x = random.randint(DIAMOND_EDGE, SCREEN_WIDTH - DIAMOND_EDGE)
    diamond_y = SCREEN_HEIGHT - 40
    diamond_color = random_bright_color()


def update(dt):
  
    global diamond_y, diamond_speed, score, is_game_over, catcher_x, catcher_color
    if is_game_over or not is_playing:
        return
    # Move catcher by keyboard input
    catcher_speed = 260.0  # px/sec
    if keys['left']:
        catcher_x -= catcher_speed * dt
    if keys['right']:
        catcher_x += catcher_speed * dt
    # clamp catcher to screen
    half = CATCHER_WIDTH // 2
    if catcher_x - half < 0:
        catcher_x = half
    if catcher_x + half > SCREEN_WIDTH:
        catcher_x = SCREEN_WIDTH - half
    # update diamond vertical position
    diamond_y -= diamond_speed * dt
    # speed ramp
    diamond_speed += 6.0 * dt
    # collision detection using AABB
    dbox = {'x': diamond_x - DIAMOND_EDGE/2, 'y': diamond_y - DIAMOND_EDGE/2, 'w': DIAMOND_EDGE, 'h': DIAMOND_EDGE}
    cbox = {'x': catcher_x - CATCHER_WIDTH/2, 'y': CATCHER_BASE_Y, 'w': CATCHER_WIDTH, 'h': CATCHER_HEIGHT + 12}
    if has_collided(dbox, cbox):
        score += 1
        print('Score:', score)
        respawn_diamond()
    # missed: diamond beyond bottom
    if diamond_y < 0:
        is_game_over = True
        catcher_color = (1.0, 0.0, 0.0)
        print('Game Over', score)

# ---------------- Display callback ----------------

def display():
    
    global last_time
    now = time.time()
    if last_time is None:
        last_time = now
    dt = now - last_time
    last_time = now

    # Update game logic with dt
    update(dt)

    # Clear screen
    glClear(GL_COLOR_BUFFER_BIT)

    # Draw catcher
    draw_catcher(int(catcher_x), catcher_color)

    # Draw diamond only if not game over 
    if not is_game_over:
        draw_diamond(int(diamond_x), int(diamond_y), DIAMOND_EDGE, diamond_color)

    # Draw buttons (icons drawn with midpoint lines)
    draw_left_arrow_icon(BUTTON_LEFT_X, BUTTON_POSITION_Y, BUTTON_DIMENSION)
    if is_playing:
        draw_pause_icon(BUTTON_CENTER_X, BUTTON_POSITION_Y, BUTTON_DIMENSION)
    else:
        draw_play_icon(BUTTON_CENTER_X, BUTTON_POSITION_Y, BUTTON_DIMENSION)
    draw_cross_icon(BUTTON_RIGHT_X, BUTTON_POSITION_Y, BUTTON_DIMENSION)

    # Swap buffers and request next frame 
    glutSwapBuffers()
    glutPostRedisplay()



def reshape(w, h):

    global SCREEN_WIDTH, SCREEN_HEIGHT, BUTTON_CENTER_X, BUTTON_RIGHT_X, BUTTON_POSITION_Y
    SCREEN_WIDTH = w
    SCREEN_HEIGHT = h
    BUTTON_CENTER_X = SCREEN_WIDTH // 2
    BUTTON_RIGHT_X = SCREEN_WIDTH - 60
    BUTTON_POSITION_Y = SCREEN_HEIGHT - 50
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init_gl():
    glClearColor(0.08, 0.10, 0.12, 1.0)  # dark background
    glPointSize(2.8)
    glEnable(GL_POINT_SMOOTH)


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Catch the Diamonds Game (Assingment2) ")

    init_gl()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_down)
    glutSpecialUpFunc(special_up)
    glutMouseFunc(mouse)

    print('Controls: Left/Right arrows move catcher. Click top icons to Restart/Play-Pause/Quit. R=Restart, P=Pause/Play, ESC=Quit.')
    glutMainLoop()


if __name__ == '__main__':
    main()