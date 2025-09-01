from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Camera-related variables
camera_pos = [0, -400, 300]
camera_angle = 0
camera_height = 300
first_person_mode = False
fovY = 60
GRID_LENGTH = 600
BOUNDARY_HEIGHT = 100

# Game state variables
game_over = False
life = 5
score = 0
bullets_missed = 0
max_misses = 10

# Player variables
player_pos = [0, 0, 30]  # x, y, z position
gun_angle = 0  # Gun rotation angle
player_lying = False

# Cheat mode variables
cheat_mode = False
cheat_vision = False
auto_rotate_angle = 0

# Bullets - each bullet is [x, y, z, angle, active]
bullets = []
BULLET_SPEED = 10

# Enemies - each enemy is [x, y, z, size, speed]
enemies = []
ENEMY_COUNT = 5
ENEMY_BASE_SPEED = 0.8

# Animation variables
enemy_scale_factor = 1.0
scale_direction = 1


def init_game():
    global enemies, bullets, life, score, bullets_missed, game_over, player_lying
    global player_pos, gun_angle, cheat_mode, cheat_vision, auto_rotate_angle

    life = 5
    score = 0
    bullets_missed = 0
    game_over = False
    player_lying = False

    player_pos = [0, 0, 30]
    gun_angle = 0

    cheat_mode = False
    cheat_vision = False
    auto_rotate_angle = 0

    enemies.clear()
    for _ in range(ENEMY_COUNT):
        enemies.append(create_enemy())

    bullets.clear()


def create_enemy():
    side = random.randint(0, 3)
    size = 20

    if side == 0:  # Top
        x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
        y = GRID_LENGTH
    elif side == 1:  # Right
        x = GRID_LENGTH
        y = random.uniform(-GRID_LENGTH, GRID_LENGTH)
    elif side == 2:  # Bottom
        x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
        y = -GRID_LENGTH
    else:  # Left
        x = -GRID_LENGTH
        y = random.uniform(-GRID_LENGTH, GRID_LENGTH)

    z = size
    speed = ENEMY_BASE_SPEED
    return [x, y, z, size, speed]


def respawn_enemy(enemy_index):
    enemies[enemy_index] = create_enemy()


def update_enemy(enemy):
    dx = player_pos[0] - enemy[0]
    dy = player_pos[1] - enemy[1]
    distance = math.sqrt(dx * dx + dy * dy)

    if distance > 0:
        enemy_speed = enemy[4]
        enemy[0] += (dx / distance) * enemy_speed
        enemy[1] += (dy / distance) * enemy_speed


def create_bullet(x, y, z, angle):
    return [x, y, z, angle, True]


def update_bullet(bullet):
    if bullet[4]:
        bullet[0] += BULLET_SPEED * math.cos(math.radians(bullet[3]))
        bullet[1] += BULLET_SPEED * math.sin(math.radians(bullet[3]))

        if abs(bullet[0]) > GRID_LENGTH or abs(bullet[1]) > GRID_LENGTH:
            bullet[4] = False
            return False
    return True


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])

    if player_lying:
        glRotatef(90, 1, 0, 0)

    # Head
    glPushMatrix()
    glTranslatef(0, 0, 35)
    glColor3f(0.9, 0.8, 0.7)
    glutSolidSphere(8, 16, 16)
    glPopMatrix()

    # Body
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glColor3f(0.2, 0.4, 0.8)
    glutSolidSphere(12, 20, 20)
    glPopMatrix()

    # Arms
    glPushMatrix()
    glTranslatef(-14, 0, 22)
    glColor3f(0.2, 0.4, 0.8)
    glutSolidSphere(5, 12, 12)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(14, 0, 22)
    glColor3f(0.2, 0.4, 0.8)
    glutSolidSphere(5, 12, 12)
    glPopMatrix()

    # Legs
    glPushMatrix()
    glTranslatef(-6, 0, 8)
    glColor3f(0.1, 0.1, 0.5)
    glutSolidSphere(6, 12, 12)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(6, 0, 8)
    glColor3f(0.1, 0.1, 0.5)
    glutSolidSphere(6, 12, 12)
    glPopMatrix()

    # Gun (right hand)
    glPushMatrix()
    glTranslatef(18, 0, 22)
    glRotatef(gun_angle, 0, 0, 1)
    glColor3f(0.3, 0.3, 0.3)
    glScalef(2, 0.5, 0.5)
    glutSolidCube(6)
    glPopMatrix()

    glPopMatrix()


def draw_enemies():
    global enemy_scale_factor, scale_direction
    enemy_scale_factor += scale_direction * 0.02
    if enemy_scale_factor > 1.3:
        scale_direction = -1
    elif enemy_scale_factor < 0.7:
        scale_direction = 1

    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy[0], enemy[1], enemy[2])
        glScalef(enemy_scale_factor, enemy_scale_factor, enemy_scale_factor)
        glColor3f(1, 0, 0)
        glutSolidSphere(enemy[3], 10, 10)
        glTranslatef(0, 0, enemy[3] * 0.8)
        glColor3f(1, 1, 0)
        glutSolidSphere(enemy[3] * 0.3, 8, 8)
        glPopMatrix()


def draw_bullets():
    glColor3f(1, 1, 0)
    for bullet in bullets:
        if bullet[4]:
            glPushMatrix()
            glTranslatef(bullet[0], bullet[1], bullet[2])
            glutSolidCube(4)
            glPopMatrix()


def draw_grid():
    glBegin(GL_QUADS)
    for i in range(-6, 7):
        for j in range(-6, 7):
            if (i + j) % 2 == 0:
                glColor3f(1.0, 1.0, 1.0)
            else:
                glColor3f(0.6, 0.2, 0.8)
            x1, x2 = i * 100, (i + 1) * 100
            y1, y2 = j * 100, (j + 1) * 100
            glVertex3f(x1, y1, 0)
            glVertex3f(x2, y1, 0)
            glVertex3f(x2, y2, 0)
            glVertex3f(x1, y2, 0)
    glEnd()


def fire_bullet():
    gun_x = player_pos[0] + 30 * math.cos(math.radians(gun_angle))
    gun_y = player_pos[1] + 30 * math.sin(math.radians(gun_angle))
    bullet = create_bullet(gun_x, gun_y, player_pos[2], gun_angle)
    bullets.append(bullet)


def check_collisions():
    global life, score, bullets_missed, game_over, player_lying

    for bullet in bullets[:]:
        if not bullet[4]:
            continue
        for i, enemy in enumerate(enemies):
            dx = bullet[0] - enemy[0]
            dy = bullet[1] - enemy[1]
            dz = bullet[2] - enemy[2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            if distance < enemy[3]:
                bullet[4] = False
                enemies[i][4] = min(enemies[i][4] + 0.3, 3.0)
                respawn_enemy(i)
                score += 1
                break

    for bullet in bullets[:]:
        if not bullet[4]:
            bullets.remove(bullet)
            if bullet[0] ** 2 + bullet[1] ** 2 > GRID_LENGTH ** 2:
                bullets_missed += 1

    if cheat_mode:
        return

    if not game_over:
        for i, enemy in enumerate(enemies):
            dx = player_pos[0] - enemy[0]
            dy = player_pos[1] - enemy[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 25:
                life -= 1
                respawn_enemy(i)
                break

    if life <= 0 or bullets_missed >= max_misses:
        game_over = True
        player_lying = True


def update_cheat_mode():
    global auto_rotate_angle, gun_angle, score
    if cheat_mode and not game_over:
        for i, enemy in enumerate(enemies):
            dx = player_pos[0] - enemy[0]
            dy = player_pos[1] - enemy[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 200:
                enemy_angle = math.degrees(math.atan2(enemy[1] - player_pos[1], enemy[0] - player_pos[0]))
                gun_angle = enemy_angle
                fire_bullet()
                enemies[i][4] = min(enemies[i][4] + 0.1, 2.0)
                respawn_enemy(i)
                score += 1
                break


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if first_person_mode:
        eye_x = player_pos[0] - 50 * math.cos(math.radians(gun_angle))
        eye_y = player_pos[1] - 50 * math.sin(math.radians(gun_angle))
        eye_z = player_pos[2] + 20
        look_x = player_pos[0] + 100 * math.cos(math.radians(gun_angle))
        look_y = player_pos[1] + 100 * math.sin(math.radians(gun_angle))
        look_z = player_pos[2]
        gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        cam_x = camera_pos[0] + 500 * math.cos(math.radians(camera_angle))
        cam_y = camera_pos[1] + 500 * math.sin(math.radians(camera_angle))
        gluLookAt(cam_x, cam_y, camera_height, 0, 0, 0, 0, 0, 1)


def keyboardListener(key, x, y):
    global gun_angle, cheat_mode, cheat_vision, first_person_mode
    if game_over:
        if key == b'r':
            init_game()
        return
    if key == b'w':
        new_y = player_pos[1] + 10
        if abs(new_y) < GRID_LENGTH - 30:
            player_pos[1] = new_y
    if key == b's':
        new_y = player_pos[1] - 10
        if abs(new_y) < GRID_LENGTH - 30:
            player_pos[1] = new_y
    if key == b'a':
        new_x = player_pos[0] - 10
        if abs(new_x) < GRID_LENGTH - 30:
            player_pos[0] = new_x
        if not cheat_mode:
            gun_angle += 5
    if key == b'd':
        new_x = player_pos[0] + 10
        if abs(new_x) < GRID_LENGTH - 30:
            player_pos[0] = new_x
        if not cheat_mode:
            gun_angle -= 5
    if key == b'c':
        cheat_mode = not cheat_mode
    if key == b'v':
        cheat_vision = not cheat_vision
    if key == b'f':
        first_person_mode = not first_person_mode


def specialKeyListener(key, x, y):
    global camera_angle, camera_height
    if key == GLUT_KEY_UP:
        camera_height = min(camera_height + 20, 800)
    if key == GLUT_KEY_DOWN:
        camera_height = max(camera_height - 20, 100)
    if key == GLUT_KEY_LEFT:
        camera_angle += 5
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 5


def mouseListener(button, state, x, y):
    global first_person_mode
    if game_over:
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not cheat_mode:
        fire_bullet()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode


def update_game():
    if not game_over:
        for bullet in bullets:
            update_bullet(bullet)
        for enemy in enemies:
            update_enemy(enemy)
        update_cheat_mode()
        check_collisions()


def idle():
    update_game()
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()
    glEnable(GL_DEPTH_TEST)
    draw_grid()
    draw_player()
    draw_enemies()
    draw_bullets()
    status_color = "ACTIVE" if not game_over else "GAME OVER"
    cheat_status = "ON" if cheat_mode else "OFF"
    vision_status = "ON" if cheat_vision else "OFF"
    camera_mode = "First Person" if first_person_mode else "Third Person"
    draw_text(10, 770, f"Status: {status_color}")
    draw_text(10, 750, f"Life: {life}")
    draw_text(10, 730, f"Score: {score}")
    draw_text(10, 710, f"Bullets Missed: {bullets_missed}/{max_misses}")
    draw_text(10, 690, f"Cheat Mode: {cheat_status}")
    draw_text(10, 670, f"Cheat Vision: {vision_status}")
    draw_text(10, 650, f"Camera: {camera_mode}")
    if game_over:
        draw_text(400, 400, "GAME OVER! Press R to restart")
    glutSwapBuffers()


def main():
    init_game()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Bullet Frenzy - 3D Game")
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.2, 1.0)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()