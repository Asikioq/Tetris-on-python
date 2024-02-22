import pygame
import sys
import psycopg2
from copy import deepcopy
from random import choice

pygame.init()

# Set up the main window for registration
registration_screen = pygame.display.set_mode((400, 200))
pygame.display.set_caption('Tetris Registration')

font = pygame.font.Font(None, 36)

# Input box parameters
input_box1 = pygame.Rect(150, 50, 200, 32)
input_box2 = pygame.Rect(150, 110, 200, 32)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color1 = color_inactive
color2 = color_inactive
active1 = False
active2 = False
text1 = ''
text2 = ''
user_name = ''

# Labels
font_label = pygame.font.Font(None, 24)
label1 = font_label.render('Nickname:', True, pygame.Color('white'))
label2 = font_label.render('Password:', True, pygame.Color('white'))

def draw_input_box(input_box, color, text):
    pygame.draw.rect(registration_screen, color, input_box, 2)
    text_surface = font.render(text, True, pygame.Color('white'))
    width = max(200, text_surface.get_width() + 10)
    input_box.w = width
    registration_screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))

register_user = False
while not register_user:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_box1.collidepoint(event.pos):
                active1 = not active1
                active2 = False
            elif input_box2.collidepoint(event.pos):
                active2 = not active2
                active1 = False
            else:
                active1 = False
                active2 = False
            color1 = color_active if active1 else color_inactive
            color2 = color_active if active2 else color_inactive
        if event.type == pygame.KEYDOWN:
            if active1:
                if event.key == pygame.K_RETURN:
                    active1 = False
                    active2 = True
                elif event.key == pygame.K_BACKSPACE:
                    text1 = text1[:-1]
                else:
                    text1 += event.unicode
            elif active2:
                if event.key == pygame.K_RETURN:
                    active2 = False
                    register_user = True
                elif event.key == pygame.K_BACKSPACE:
                    text2 = text2[:-1]
                else:
                    text2 += event.unicode

    registration_screen.fill((30, 30, 30))

    # Draw labels
    registration_screen.blit(label1, (50, 60 - 25))
    registration_screen.blit(label2, (50, 120 - 25))

    # Draw input boxes
    draw_input_box(input_box1, color1, text1)
    draw_input_box(input_box2, color2, '*' * len(text2))  # Display asterisks for password input

    pygame.display.flip()

# Continue with the Tetris game code
# (Remaining Tetris game code unchanged)

W, H = 10, 20
TILE = 45
GAME_RES = W * TILE, H * TILE
FPS = 60

pygame.init()
game_sc = pygame.display.set_mode(GAME_RES)
clock = pygame.time.Clock()
pygame.display.set_caption('Tetris')

grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)]

anim_count, anim_speed, anim_limit = 0, 60, 2000
figure = deepcopy(choice(figures))
next_figure = deepcopy(choice(figures))  # New variable for the next figure

# Connect to the database
conn = psycopg2.connect(
    database="project",
    user="postgres",
    password="123",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Create a table to store high scores if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id SERIAL PRIMARY KEY,
        score INTEGER
    )
''')
conn.commit()

# Check if the user already exists in the user data file
user_exists = False
cursor.execute("SELECT username FROM user_data WHERE username = %s", (text1,))
existing_username = cursor.fetchone()
if not user_exists:
    # Save the entered username and password to the user data file
    with open('user_data.txt', 'a') as file:
        file.write(f'Username: {text1}\n')
        file.write(f'Password: {text2}\n')

    print(f'Tetris game started for user: {text1}')
else:
    print(f'User "{text1}" already exists. Starting Tetris game for existing user.')

if existing_username:
    user_exists = True

score = 0
filepath = r'C:\Users\Asus\OneDrive\Desktop\IT\django\bestscore'
with open(filepath) as file:
    content = file.read().strip()
    if content:
        best_score = int(content)
    else:
        print("File is empty. No best score available.")

def save_score():
    try:
        with open(filepath, 'w') as file:
            file.write(str(score))
        print(f"Current score saved to 'bestscore.txt'")
    except Exception as e:
        print(f"Error saving score: {e}")

def draw_figure(figure, color, offset_x=0, offset_y=0):
    for i in range(4):
        figure_rect.x = (figure[i].x + offset_x) * TILE
        figure_rect.y = (figure[i].y + offset_y) * TILE
        pygame.draw.rect(game_sc, color, figure_rect)

def check_borders():
    for i in range(4):
        if figure[i].x < 0 or figure[i].x > W - 1:
            return False
        elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
            return False
    return True

paused = False

while True:
    dx, rotate = 0, False
    game_sc.fill(pygame.Color('black'))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True
            elif event.key == pygame.K_ESCAPE:
                if score > best_score:
                    save_score()
                exit()
            elif event.key == pygame.K_SPACE:
                paused = not paused

    if not paused:
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].x += dx
            if not check_borders():
                figure = deepcopy(figure_old)
                break

        anim_count += anim_speed
        if anim_count > anim_limit:
            anim_count = 0
            figure_old = deepcopy(figure)
            for i in range(4):
                figure[i].y += 1
                if not check_borders():
                    for i in range(4):
                        field[figure_old[i].y][figure_old[i].x] = pygame.Color('white')
                    figure = deepcopy(next_figure)  # Set the current figure to the next one
                    next_figure = deepcopy(choice(figures))  # Generate a new next figure
                    anim_limit = 2000
                    # Update the score in the database when a figure is placed
                    cursor.execute('INSERT INTO scores (score) VALUES (?)', (score,))
                    conn.commit()
                    break

        center = figure[0]
        figure_old = deepcopy(figure)
        if rotate:
            for i in range(4):
                x = figure[i].y - center.y
                y = figure[i].x - center.x
                figure[i].x = center.x - x
                figure[i].y = center.y + y
                if not check_borders():
                    figure = deepcopy(figure_old)
                    break

        line = H - 1
        for row in range(H - 1, -1, -1):
            count = 0
            for i in range(W):
                if field[row][i]:
                    count += 1
                field[line][i] = field[row][i]
            if count < W:
                line -= 1
            else:
                score += 10  # Increment the score when a line is filled

        # Check if the top row is filled
        if any(field[0]):
            if score > best_score:
                    save_score()
            exit()

    # Draw the next figure on the screen
    draw_figure(next_figure, pygame.Color('gray'), offset_x=3, offset_y=1)

    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]

    draw_figure(figure, pygame.Color('white'))

    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    # Draw the score on the screen
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, pygame.Color('white'))
    best = font.render(f'Best score: {best_score}', True, pygame.Color('white'))
    next_fig = font.render(f'Next figure:', True, pygame.Color('white'))
    game_sc.blit(score_text, (10, 10))
    game_sc.blit(best, (10,50))
    game_sc.blit(next_fig, (300, 10))

    if paused:
        pause_text = font.render("Paused", True, pygame.Color('white'))
        game_sc.blit(pause_text, (GAME_RES[0] // 2 - 50, GAME_RES[1] // 2))

    pygame.display.flip()
    clock.tick(FPS)

conn.close()
