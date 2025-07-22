##task1
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random 


W_WIDTH, W_HEIGHT = 800, 600


MAX_RAINDROPS = 150  
raindrops = []  # rain drop list
rain_speed = 3.0  # default speed
rain_bend = 0.0  

# initially black (night)
bg_color = [0.0, 0.0, 0.0]  

# Raindrops initialize 
def init_raindrops():
    global raindrops
    raindrops = []  # list khali kore dilam
    for _ in range(MAX_RAINDROPS):
        x = random.uniform(-W_WIDTH//2, W_WIDTH//2)  # random x-position
        y = random.uniform(0, W_HEIGHT//2)  # random y-position upper half theke
        speed = random.uniform(2.0, 5.0)  # speed  random
        raindrops.append([x, y, speed])  #  raindrop add 

# House draw korar function
def draw_house():
    glColor3f(0.5, 0.8, 0.2)  # house  green

    # House body draw with triangle 
    glBegin(GL_TRIANGLES)
    glVertex2f(-100, -100)
    glVertex2f(-100, 0)
    glVertex2f(100, -100)

    glVertex2f(-100, 0)
    glVertex2f(100, 0)
    glVertex2f(100, -100)
    glEnd()

    # Roof draw kortesi triangle diye
    glColor3f(0.7, 0.1, 0.1)  # roof  red 
    glBegin(GL_TRIANGLES)
    glVertex2f(-120, 0)
    glVertex2f(0, 100)
    glVertex2f(120, 0)
    glEnd()

    # Door draw kortesi line diye 
    glColor3f(0.3, 0.2, 0.1)  # door  brown
    glLineWidth(3)  
    glBegin(GL_LINES)
    glVertex2f(-20, -100)
    glVertex2f(-20, -50)

    glVertex2f(-20, -50)
    glVertex2f(20, -50)

    glVertex2f(20, -50)
    glVertex2f(20, -100)

    glVertex2f(20, -100)
    glVertex2f(-20, -100)
    glEnd()

# Raindrop draw korar function
def draw_raindrops():
    glColor3f(0.3, 0.6, 1.0)  # rain drop color blue
    glLineWidth(2)  # line width 
    glBegin(GL_LINES)
    for x, y, _ in raindrops:
        glVertex2f(x, y)  # starting point
        glVertex2f(x + rain_bend, y - 10)  # bend + down direction
    glEnd()


def update_raindrops():
    global raindrops
    for i in range(len(raindrops)):
        x, y, speed = raindrops[i]
        x += rain_bend  # left/right bend
        y -= speed  # niche namte thakbe

        # Jodi bottom e chole jay, abar upore niya asbo
        if y < -W_HEIGHT//2:
            y = W_HEIGHT//2
            x = random.uniform(-W_WIDTH//2, W_WIDTH//2)
            speed = random.uniform(2.0, 5.0)

        raindrops[i] = [x, y, speed]  # updated value save 

def keyboardListener(key, x, y):
    global rain_bend, bg_color

    # LEFT arrow 
    if key == GLUT_KEY_LEFT:
        if rain_bend > -1.5:
            rain_bend -= 0.1

    # RIGHT arrow   
    elif key == GLUT_KEY_RIGHT:
        if rain_bend < 1.5:
            rain_bend += 0.1

    #  (night to day)
    elif key == GLUT_KEY_UP:
        bg_color = [min(c + 0.05, 1.0) for c in bg_color]  # bright to brighter

    # (day to night)
    elif key == GLUT_KEY_DOWN:
        bg_color = [max(c - 0.05, 0.0) for c in bg_color]  #dark to darker

    glutPostRedisplay()  #  screen redraw 


def display():
    glClearColor(*bg_color, 1)  # background color set
    glClear(GL_COLOR_BUFFER_BIT)  # screen clean

    # 2D ortho projection set kortesi
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-W_WIDTH//2, W_WIDTH//2, -W_HEIGHT//2, W_HEIGHT//2)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # House and rain draw kortesi
    draw_house()
    draw_raindrops()

    glutSwapBuffers()  # buffer switch kore drawing dekhai

def animate():
    update_raindrops()  # rain er position
    glutPostRedisplay()  #  redraw

# Main function
def main():
    glutInit()
    glutInitWindowSize(W_WIDTH, W_HEIGHT)  # window size set
    glutInitWindowPosition(100, 100)  # screen e position
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)  
    glutCreateWindow(b"Task 1: House with Rainfall")  # window title

    init_raindrops()  # starting raindrops generate 

    glutDisplayFunc(display)  
    glutIdleFunc(animate)  
    glutSpecialFunc(keyboardListener) 

    glutMainLoop()  # loop chalu

# Main function call
if __name__ == "__main__":
    main()

##task2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from random import randint

W_WIDTH, W_HEIGHT = 800, 600
points = []

speed = 0.5  # kom speed
blink = False  # blink off by default
blink_state = True  # blink on-off toggle
freeze = False  # freeze off

def draw_points():
    global blink, blink_state, freeze

    # blink on thakle & freeze off thakle blinking hobe
    for i in range(len(points)):
        x, y, r, g, b, dx, dy = points[i]

        if not freeze:
            x += dx * speed
            y += dy * speed

            if x < 0 or x > W_WIDTH:
                dx *= -1
            if y < 0 or y > W_HEIGHT:
                dy *= -1

            points[i] = [x, y, r, g, b, dx, dy]

        # blink on and blink_state off hole black draw korbo
        if blink and not freeze and not blink_state:
            glColor3f(0, 0, 0)
        else:
            glColor3f(r, g, b)

        glPointSize(6)
        glBegin(GL_POINTS)
        glVertex2f(x, y)
        glEnd()

def mouse_click(button, state, x, y):
    global blink, points

    if state == GLUT_DOWN:
        y = W_HEIGHT - y

        if button == GLUT_RIGHT_BUTTON:
            dx, dy = [(-1, -1), (-1, 1), (1, -1), (1, 1)][randint(0, 3)]
            r, g, b = randint(1, 10)/10, randint(1, 10)/10, randint(1, 10)/10
            points.append([x, y, r, g, b, dx, dy])

        elif button == GLUT_LEFT_BUTTON:
            blink = not blink  # left-click e blink toggle

    glutPostRedisplay()

def special_keys(key, x, y):
    global speed
    if key == GLUT_KEY_UP:
        speed *= 1.5
    elif key == GLUT_KEY_DOWN:
        speed /= 1.5
    glutPostRedisplay()

def keyboard_keys(key, x, y):
    global freeze
    if key == b' ':
        freeze = not freeze  # spacebar  freeze toggle
    glutPostRedisplay()

def display():
    global blink_state

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W_WIDTH, 0, W_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_points()

    glutSwapBuffers()

    # Jodi freeze na thake & blink on thake, blink_state toggle korbo
    if blink and not freeze:
        blink_state = not blink_state

def animate():
    glutPostRedisplay()

def init():
    glClearColor(0, 0, 0, 1)

# Main Loop
glutInit()
glutInitWindowSize(W_WIDTH, W_HEIGHT)
glutInitWindowPosition(100, 100)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutCreateWindow(b"Amazing Box")

init()
glutDisplayFunc(display)
glutIdleFunc(animate)
glutMouseFunc(mouse_click)
glutSpecialFunc(special_keys)
glutKeyboardFunc(keyboard_keys)
glutMainLoop()

##############################
#task 2 
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from random import randint

W_WIDTH, W_HEIGHT = 800, 600
points = []

speed = 0.5  
blink = False  
blink_state = True  
freeze = False  

def draw_points():
    global blink, blink_state, freeze

    # blink on thakle & freeze off thakle blinking hobe
    for i in range(len(points)):
        x, y, r, g, b, dx, dy = points[i]

        if not freeze:
            x += dx * speed
            y += dy * speed

            if x < 0 or x > W_WIDTH:
                dx *= -1
            if y < 0 or y > W_HEIGHT:
                dy *= -1

            points[i] = [x, y, r, g, b, dx, dy]

        # blink on and blink_state off hole black draw korbo
        if blink and not freeze and not blink_state:
            glColor3f(0, 0, 0)
        else:
            glColor3f(r, g, b)

        glPointSize(6)
        glBegin(GL_POINTS)
        glVertex2f(x, y)
        glEnd()

def mouse_click(button, state, x, y):
    global blink, points

    if state == GLUT_DOWN:
        y = W_HEIGHT - y

        if button == GLUT_RIGHT_BUTTON:
            dx, dy = [(-1, -1), (-1, 1), (1, -1), (1, 1)][randint(0, 3)]
            r, g, b = randint(1, 10)/10, randint(1, 10)/10, randint(1, 10)/10
            points.append([x, y, r, g, b, dx, dy])

        elif button == GLUT_LEFT_BUTTON:
            blink = not blink  # left-click e blink toggle

    glutPostRedisplay()

def special_keys(key, x, y):
    global speed
    if key == GLUT_KEY_UP:
        speed *= 1.5
    elif key == GLUT_KEY_DOWN:
        speed /= 1.5
    glutPostRedisplay()

def keyboard_keys(key, x, y):
    global freeze
    if key == b' ':
        freeze = not freeze  # spacebar e freeze toggle
    glutPostRedisplay()

def display():
    global blink_state

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, W_WIDTH, 0, W_HEIGHT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_points()

    glutSwapBuffers()

    # Jodi freeze na thake & blink on thake, blink_state toggle korbo
    if blink and not freeze:
        blink_state = not blink_state

def animate():
    glutPostRedisplay()

def init():
    glClearColor(0, 0, 0, 1)

# Main Loop
glutInit()
glutInitWindowSize(W_WIDTH, W_HEIGHT)
glutInitWindowPosition(100, 100)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutCreateWindow(b"Amazing Box")

init()
glutDisplayFunc(display)
glutIdleFunc(animate)
glutMouseFunc(mouse_click)
glutSpecialFunc(special_keys)
glutKeyboardFunc(keyboard_keys)
glutMainLoop()