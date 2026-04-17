from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import sys
from PIL import Image

# Game variables
bird_x = -0.8
bird_y = 0.0
bird_vel = 0.0
gravity = -0.0005

pipes = []
score = 0
game_over = False
app_running = True
bg_scroll = 0.0

pipe_width = 0.1
pipe_gap = 0.4
pipe_speed = 0.005

bird_width = 0.06
bird_height = 0.10

bird_frame = 0
frame_counter = 0
textures = []
bg_textures = []
bg_index = 0   

# ---------------- INIT ----------------
def init():
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    global textures, bg_textures, bg_index

    # -------- BIRD TEXTURES --------
    textures = glGenTextures(4)

    for i in range(4):
        try:
            glBindTexture(GL_TEXTURE_2D, textures[i])
            img = Image.open(f'assets/bird{i+1}.png')
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img = img.convert('RGBA')

            img_data = img.tobytes()

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                         img.width, img.height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, img_data)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        except Exception as e:
            print(f"Error loading bird{i+1}.png:", e)

    # -------- BACKGROUND TEXTURES --------
    bg_files = ['assets/bg1.png', 'assets/bg2.png']
    bg_textures = glGenTextures(len(bg_files))

    for i, bg_path in enumerate(bg_files):
        try:
            glBindTexture(GL_TEXTURE_2D, bg_textures[i])
            img = Image.open(bg_path)
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            img = img.convert('RGBA')

            img_data = img.tobytes()

            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                         img.width, img.height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, img_data)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        except Exception as e:
            print(f"Error loading {bg_path}:", e)

    bg_index = random.randrange(len(bg_files))

# ---------------- DRAW BACKGROUND ----------------
def draw_background():
    global bg_scroll
    glColor3f(1, 1, 1)
    glBindTexture(GL_TEXTURE_2D, bg_textures[bg_index])

    glBegin(GL_QUADS)
    # Scroll the texture horizontally
    glTexCoord2f(bg_scroll, 0); glVertex2f(-1, -1)
    glTexCoord2f(bg_scroll + 2, 0); glVertex2f(1, -1)
    glTexCoord2f(bg_scroll + 2, 1); glVertex2f(1, 1)
    glTexCoord2f(bg_scroll, 1); glVertex2f(-1, 1)
    glEnd()

# ---------------- DRAW BIRD ----------------
def draw_bird(frame):
    glColor3f(1.0, 1.0, 1.0)

    glBindTexture(GL_TEXTURE_2D, textures[frame])

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex2f(bird_x - bird_width, bird_y - bird_height)
    glTexCoord2f(1.0, 0.0); glVertex2f(bird_x + bird_width, bird_y - bird_height)
    glTexCoord2f(1.0, 1.0); glVertex2f(bird_x + bird_width, bird_y + bird_height)
    glTexCoord2f(0.0, 1.0); glVertex2f(bird_x - bird_width, bird_y + bird_height)
    glEnd()

# ---------------- DRAW PIPE ----------------
def draw_pipe(x, gap_y):
    glDisable(GL_TEXTURE_2D)

    glColor3f(0.0, 1.0, 0.0)

    glBegin(GL_QUADS)
    glVertex2f(x - pipe_width/2, -1.0)
    glVertex2f(x + pipe_width/2, -1.0)
    glVertex2f(x + pipe_width/2, gap_y - pipe_gap/2)
    glVertex2f(x - pipe_width/2, gap_y - pipe_gap/2)
    glEnd()

    glBegin(GL_QUADS)
    glVertex2f(x - pipe_width/2, gap_y + pipe_gap/2)
    glVertex2f(x + pipe_width/2, gap_y + pipe_gap/2)
    glVertex2f(x + pipe_width/2, 1.0)
    glVertex2f(x - pipe_width/2, 1.0)
    glEnd()

    glEnable(GL_TEXTURE_2D)

# ---------------- DISPLAY ----------------
def display():
    glClear(GL_COLOR_BUFFER_BIT)

    draw_background()   
    draw_bird(bird_frame)

    for pipe in pipes:
        draw_pipe(pipe[0], pipe[1])

    glutSwapBuffers()

# ---------------- UPDATE ----------------
def update(value):
    global bird_y, bird_vel, pipes, score, game_over, bird_frame, frame_counter, app_running, bg_scroll

    if not app_running:
        return

    frame_counter += 1
    if frame_counter >= 8:
        bird_frame = (bird_frame + 1) % 4
        frame_counter = 0

    if not game_over:
        bird_vel += gravity
        bird_y += bird_vel

        if bird_y > 0.9:
            bird_y = 0.9
            bird_vel = 0
        elif bird_y < -0.9:
            bird_y = -0.9
            bird_vel = 0

        for pipe in pipes:
            pipe[0] -= pipe_speed

        # Scroll background with pipes for seamless effect
        bg_scroll += pipe_speed
        if bg_scroll > 1.0:
            bg_scroll -= 1.0

        pipes[:] = [p for p in pipes if p[0] > -1.2]

        if not pipes or pipes[-1][0] < 0.5:
            pipes.append([1.0, random.uniform(-0.3, 0.3), False])

        for pipe in pipes:
            # Bird collision box
            bird_left = bird_x - bird_width
            bird_right = bird_x + bird_width
            bird_top = bird_y + bird_height
            bird_bottom = bird_y - bird_height
            
            # Pipe collision box
            pipe_left = pipe[0] - pipe_width/2
            pipe_right = pipe[0] + pipe_width/2
            gap_top = pipe[1] + pipe_gap/2
            gap_bottom = pipe[1] - pipe_gap/2
            
            # Check if bird and pipe X ranges overlap
            x_overlap = bird_right >= pipe_left and bird_left <= pipe_right
            
            if x_overlap:
                # Check if bird hits top pipe or bottom pipe (outside the gap)
                hits_top_pipe = bird_top >= gap_top
                hits_bottom_pipe = bird_bottom <= gap_bottom
                
                if hits_top_pipe or hits_bottom_pipe:
                    game_over = True
                    print("Game Over!")

        for pipe in pipes:
            if pipe[0] + pipe_width/2 < bird_x and not pipe[2]:
                score += 1
                pipe[2] = True
                print("Score:", score)

    glutPostRedisplay()
    if app_running:
        glutTimerFunc(16, update, 0)

# ---------------- INPUT ----------------
def keyboard(key, x, y):
    global bird_vel, game_over, pipes, score, bird_y, app_running, bg_index

    try:
        if key == b' ' and not game_over:
            bird_vel = 0.01

        elif key == b'r' and game_over:
            bird_y = 0
            bird_vel = 0
            pipes.clear()
            score = 0
            game_over = False
            bg_index = random.randrange(len(bg_textures))

        elif key == b'q':
            app_running = False
            glutLeaveMainLoop()
    except KeyboardInterrupt:
        app_running = False
        glutLeaveMainLoop()

# ---------------- CLOSE WINDOW ----------------
def on_close():
    global app_running
    app_running = False
    glutLeaveMainLoop()

# ---------------- MAIN ----------------
def main():
    global app_running
    try:
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
        glutInitWindowSize(800, 600)
        glutCreateWindow(b"Flappy Bird OpenGL")
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1, 1, -1, 1, -1, 1)
        glMatrixMode(GL_MODELVIEW)

        init()

        glutDisplayFunc(display)
        glutKeyboardFunc(keyboard)
        glutCloseFunc(on_close)
        glutTimerFunc(0, update, 0)

        glutMainLoop()
    except KeyboardInterrupt:
        app_running = False
    finally:
        app_running = False

if __name__ == "__main__":
    main()
