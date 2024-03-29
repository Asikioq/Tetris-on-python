import sqlite3
import pygame
from copy import deepcopy
from random import choice

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
conn = sqlite3.connect('tetris_scores.db')
cursor = conn.cursor()

# Create a table to store high scores if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        score INTEGER
    )
''')
conn.commit()

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

# Close the database connection when the game ends
conn.close()
