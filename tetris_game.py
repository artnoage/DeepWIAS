import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_MARGIN = 1

# Calculate display dimensions
DISPLAY_WIDTH = (BLOCK_SIZE + GRID_MARGIN) * GRID_WIDTH + GRID_MARGIN + 200  # Extra space for score
DISPLAY_HEIGHT = (BLOCK_SIZE + GRID_MARGIN) * GRID_HEIGHT + GRID_MARGIN

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Colors for each shape
SHAPE_COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Tetromino:
    def __init__(self):
        self.shape_index = random.randint(0, len(SHAPES) - 1)
        self.shape = [row[:] for row in SHAPES[self.shape_index]]
        self.color = SHAPE_COLORS[self.shape_index]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        # Transpose the shape matrix (rotate 90 degrees)
        rotated = [[self.shape[y][x] for y in range(len(self.shape))] 
                  for x in range(len(self.shape[0])-1, -1, -1)]
        return rotated

    def get_positions(self):
        positions = []
        for y, row in enumerate(self.shape):
            for x, cell in enumerate(row):
                if cell:
                    positions.append((self.x + x, self.y + y))
        return positions

def create_grid(locked_positions={}):
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    
    return grid

def valid_space(tetromino, grid):
    accepted_positions = [[(x, y) for x in range(GRID_WIDTH) if grid[y][x] == 0] 
                         for y in range(GRID_HEIGHT)]
    accepted_positions = [pos for sublist in accepted_positions for pos in sublist]
    
    formatted = tetromino.get_positions()
    
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] >= 0:  # Only check if the piece is on the board
                return False
    
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 0:
            return True
    return False

def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid)-1, -1, -1):
        row = grid[i]
        if 0 not in row:
            inc += 1
            # Remove the row
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    
    if inc > 0:
        # Sort locked by y value and shift down
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < inc:
                continue
            newKey = (x, y - inc)
            locked[newKey] = locked.pop(key)
    
    return inc

def draw_grid(surface, grid):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(
                surface, 
                grid[y][x] if grid[y][x] else BLACK,
                (x * (BLOCK_SIZE + GRID_MARGIN) + GRID_MARGIN,
                 y * (BLOCK_SIZE + GRID_MARGIN) + GRID_MARGIN,
                 BLOCK_SIZE,
                 BLOCK_SIZE)
            )
    
    # Draw grid lines
    for y in range(GRID_HEIGHT + 1):
        pygame.draw.line(
            surface,
            WHITE,
            (0, y * (BLOCK_SIZE + GRID_MARGIN)),
            (GRID_WIDTH * (BLOCK_SIZE + GRID_MARGIN), y * (BLOCK_SIZE + GRID_MARGIN))
        )
    
    for x in range(GRID_WIDTH + 1):
        pygame.draw.line(
            surface,
            WHITE,
            (x * (BLOCK_SIZE + GRID_MARGIN), 0),
            (x * (BLOCK_SIZE + GRID_MARGIN), GRID_HEIGHT * (BLOCK_SIZE + GRID_MARGIN))
        )

def draw_tetromino(surface, tetromino, grid_offset=(0, 0)):
    positions = tetromino.get_positions()
    for pos in positions:
        x, y = pos
        if y >= 0:  # Only draw if the piece is on the board
            pygame.draw.rect(
                surface,
                tetromino.color,
                (grid_offset[0] + x * (BLOCK_SIZE + GRID_MARGIN) + GRID_MARGIN,
                 grid_offset[1] + y * (BLOCK_SIZE + GRID_MARGIN) + GRID_MARGIN,
                 BLOCK_SIZE,
                 BLOCK_SIZE)
            )

def draw_next_shape(surface, tetromino):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape:', 1, WHITE)
    
    start_x = GRID_WIDTH * (BLOCK_SIZE + GRID_MARGIN) + 20
    start_y = 50
    
    surface.blit(label, (start_x, start_y - 40))
    
    # Draw the shape
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(
                    surface,
                    tetromino.color,
                    (start_x + x * (BLOCK_SIZE + GRID_MARGIN),
                     start_y + y * (BLOCK_SIZE + GRID_MARGIN),
                     BLOCK_SIZE,
                     BLOCK_SIZE)
                )

def draw_score(surface, score, level, lines_cleared):
    font = pygame.font.SysFont('comicsans', 30)
    
    score_label = font.render(f'Score: {score}', 1, WHITE)
    level_label = font.render(f'Level: {level}', 1, WHITE)
    lines_label = font.render(f'Lines: {lines_cleared}', 1, WHITE)
    
    start_x = GRID_WIDTH * (BLOCK_SIZE + GRID_MARGIN) + 20
    
    surface.blit(score_label, (start_x, 200))
    surface.blit(level_label, (start_x, 240))
    surface.blit(lines_label, (start_x, 280))

def draw_game_over(surface):
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('GAME OVER', 1, RED)
    
    surface.blit(label, (DISPLAY_WIDTH//2 - label.get_width()//2, DISPLAY_HEIGHT//2 - label.get_height()//2))
    
    font = pygame.font.SysFont('comicsans', 30)
    restart_label = font.render('Press R to restart', 1, WHITE)
    quit_label = font.render('Press Q to quit', 1, WHITE)
    
    surface.blit(restart_label, (DISPLAY_WIDTH//2 - restart_label.get_width()//2, DISPLAY_HEIGHT//2 + 50))
    surface.blit(quit_label, (DISPLAY_WIDTH//2 - quit_label.get_width()//2, DISPLAY_HEIGHT//2 + 90))

def main():
    # Game window
    win = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption('Tetris')
    
    # Game variables
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27  # seconds
    level_time = 0
    score = 0
    level = 1
    lines_cleared = 0
    
    # Game state
    locked_positions = {}
    grid = create_grid(locked_positions)
    
    change_piece = False
    run = True
    current_piece = Tetromino()
    next_piece = Tetromino()
    game_over = False
    
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()
        
        # Increase level and speed every 60 seconds
        if level_time/1000 > 60:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.05
                level += 1
        
        # Move piece down automatically
        if fall_time/1000 > fall_speed and not game_over:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return
            
            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not valid_space(current_piece, grid):
                            current_piece.x += 1
                    
                    if event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not valid_space(current_piece, grid):
                            current_piece.x -= 1
                    
                    if event.key == pygame.K_DOWN:
                        current_piece.y += 1
                        if not valid_space(current_piece, grid):
                            current_piece.y -= 1
                    
                    if event.key == pygame.K_UP:
                        # Rotate the piece
                        old_shape = current_piece.shape
                        current_piece.shape = current_piece.rotate()
                        if not valid_space(current_piece, grid):
                            current_piece.shape = old_shape
                
                if event.key == pygame.K_r and game_over:
                    # Restart game
                    locked_positions = {}
                    grid = create_grid(locked_positions)
                    change_piece = False
                    score = 0
                    level = 1
                    lines_cleared = 0
                    fall_speed = 0.27
                    current_piece = Tetromino()
                    next_piece = Tetromino()
                    game_over = False
                
                if event.key == pygame.K_q and game_over:
                    run = False
                    pygame.quit()
                    return
        
        # Add piece to the grid if it has landed
        if change_piece:
            for pos in current_piece.get_positions():
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            
            current_piece = next_piece
            next_piece = Tetromino()
            change_piece = False
            
            # Check if rows need to be cleared
            rows_cleared = clear_rows(grid, locked_positions)
            if rows_cleared > 0:
                lines_cleared += rows_cleared
                # Score calculation: more points for clearing multiple rows at once
                if rows_cleared == 1:
                    score += 40 * level
                elif rows_cleared == 2:
                    score += 100 * level
                elif rows_cleared == 3:
                    score += 300 * level
                elif rows_cleared == 4:
                    score += 1200 * level
        
        # Check if game is over
        if check_lost(locked_positions):
            game_over = True
        
        # Draw everything
        win.fill(BLACK)
        draw_grid(win, grid)
        draw_tetromino(win, current_piece)
        draw_next_shape(win, next_piece)
        draw_score(win, score, level, lines_cleared)
        
        if game_over:
            draw_game_over(win)
        
        pygame.display.update()

def show_menu():
    win = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption('Tetris')
    
    run = True
    while run:
        win.fill(BLACK)
        font = pygame.font.SysFont('comicsans', 60)
        title = font.render('TETRIS', 1, CYAN)
        win.blit(title, (DISPLAY_WIDTH//2 - title.get_width()//2, 100))
        
        font = pygame.font.SysFont('comicsans', 30)
        start = font.render('Press any key to start', 1, WHITE)
        controls = font.render('Controls:', 1, WHITE)
        move = font.render('Arrow keys to move', 1, WHITE)
        rotate = font.render('Up arrow to rotate', 1, WHITE)
        
        win.blit(start, (DISPLAY_WIDTH//2 - start.get_width()//2, 300))
        win.blit(controls, (DISPLAY_WIDTH//2 - controls.get_width()//2, 400))
        win.blit(move, (DISPLAY_WIDTH//2 - move.get_width()//2, 440))
        win.blit(rotate, (DISPLAY_WIDTH//2 - rotate.get_width()//2, 480))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return False
            
            if event.type == pygame.KEYDOWN:
                main()
                return True
    
    return False

if __name__ == "__main__":
    show_menu()
