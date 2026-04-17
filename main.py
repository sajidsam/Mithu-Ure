from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import sys
from PIL import Image

# ---------------- GAME VARIABLES ----------------
bird_x = -0.6
bird_y = 0.0
bird_vel = 0.0
gravity = -0.0005

pipes = []
score = 0
game_over = False

pipe_width = 0.1
pipe_gap = 0.4
pipe_speed = 0.004

bird_width = 0.06
bird_height = 0.10

bird_frame = 0
frame_counter = 0
textures = []

# ---------------- INIT ----------------
def init():
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    global textures
    textures = glGenTextures(4)

    for i in range(4):
        try:
            glBindTexture(GL_TEXTURE_2D, textures[i])
            img = Image.open(f'assets/bird{i+1}.png')
            img = img.transpose(Image.FLIP_TOP_BOTTOM).convert('RGBA')

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                         img.width, img.height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        except:
            print("Missing bird texture")

# ---------------- DRAW ----------------
def draw_bird():
    glBindTexture(GL_TEXTURE_2D, textures[bird_frame])

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(bird_x - bird_width, bird_y - bird_height)
    glTexCoord2f(1, 0); glVertex2f(bird_x + bird_width, bird_y - bird_height)
    glTexCoord2f(1, 1); glVertex2f(bird_x + bird_width, bird_y + bird_height)
    glTexCoord2f(0, 1); glVertex2f(bird_x - bird_width, bird_y + bird_height)
    glEnd()

def draw_pipe(x, gap_y):
    glDisable(GL_TEXTURE_2D)
    glColor3f(0, 1, 0)

    # bottom pipe
    glBegin(GL_QUADS)
    glVertex2f(x - pipe_width/2, -1)
    glVertex2f(x + pipe_width/2, -1)
    glVertex2f(x + pipe_width/2, gap_y - pipe_gap/2)
    glVertex2f(x - pipe_width/2, gap_y - pipe_gap/2)
    glEnd()

    # top pipe
    glBegin(GL_QUADS)
    glVertex2f(x - pipe_width/2, gap_y + pipe_gap/2)
    glVertex2f(x + pipe_width/2, gap_y + pipe_gap/2)
    glVertex2f(x + pipe_width/2, 1)
    glVertex2f(x - pipe_width/2, 1)
    glEnd()

    glEnable(GL_TEXTURE_2D)

def draw_text(x, y, text):
    glDisable(GL_TEXTURE_2D)
    glColor3f(1,1,1)
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))
    glEnable(GL_TEXTURE_2D)

# ---------------- DISPLAY ----------------
def display():
    glClear(GL_COLOR_BUFFER_BIT)

    draw_bird()

    for pipe in pipes:
        draw_pipe(pipe[0], pipe[1])

    draw_text(0.7, 0.9, f"Score: {score}")

    if game_over:
        draw_text(-0.2, 0.0, "GAME OVER (Press R)")

    glutSwapBuffers()

# ---------------- UPDATE ----------------
def update(value):
    global bird_y, bird_vel, pipes, score, game_over
    global bird_frame, frame_counter

    if not game_over:
        # animation
        frame_counter += 1
        if frame_counter >= 8:
            bird_frame = (bird_frame + 1) % 4
            frame_counter = 0

        # physics
        bird_vel += gravity
        bird_y += bird_vel

        # move pipes
        for pipe in pipes:
            pipe[0] -= pipe_speed

        pipes[:] = [p for p in pipes if p[0] > -1.2]

        if not pipes or pipes[-1][0] < 0.5:
            pipes.append([1.0, random.uniform(-0.3, 0.3), False])

        # ---------------- PERFECT EDGE COLLISION ----------------
        for pipe in pipes:
            hitbox_scale = 0.75
            margin = 0.002  # VERY SMALL → edge detect

            bird_left = bird_x - bird_width * hitbox_scale
            bird_right = bird_x + bird_width * hitbox_scale
            bird_top = bird_y + bird_height * hitbox_scale
            bird_bottom = bird_y - bird_height * hitbox_scale

            pipe_left = pipe[0] - pipe_width/2
            pipe_right = pipe[0] + pipe_width/2
            gap_top = pipe[1] + pipe_gap/2
            gap_bottom = pipe[1] - pipe_gap/2

            touching_x = (
                bird_right >= pipe_left - margin and
                bird_left <= pipe_right + margin
            )

            if touching_x:
                if bird_top >= gap_top - margin or bird_bottom <= gap_bottom + margin:
                    game_over = True

        # score
        for pipe in pipes:
            if pipe[0] < bird_x and not pipe[2]:
                score += 1
                pipe[2] = True

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

# ---------------- INPUT ----------------
def keyboard(key, x, y):
    global bird_vel, game_over, pipes, score, bird_y

    if key == b' ' and not game_over:
        bird_vel = 0.008

    if key == b'r':
        bird_y = 0
        bird_vel = 0
        pipes.clear()
        score = 0
        game_over = False

# ---------------- MAIN ----------------
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Flappy Bird (Fixed Collision)")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1,1,-1,1,-1,1)

    init()

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutTimerFunc(0, update, 0)

    glutMainLoop()

if __name__ == "__main__":
    main()
