import pygame

CELL_SIZE = 50
CELL_SPACING = 6
GRID_ORIGIN = (50, 100)
GRID_WIDTH = CELL_SIZE * 10 + CELL_SPACING * 9
GRID_HEIGHT = CELL_SIZE * 10 + CELL_SPACING * 9

class Grid:
    def __init__(self, rows, cols, origin=GRID_ORIGIN):
        self.rows = rows
        self.cols = cols
        self.cells = [[0 for _ in range(cols)] for _ in range(rows)]  # 0 = vide, sinon couleur (tuple)
        self.origin = origin
        self.cell_size = CELL_SIZE
        self.spacing = CELL_SPACING

    def draw(self, surface):
        grid_rect = pygame.Rect(self.origin[0]-8, self.origin[1]-8, GRID_WIDTH+16, GRID_HEIGHT+16)
        pygame.draw.rect(surface, (25, 32, 54), grid_rect, border_radius=10)
        for y in range(self.rows):
            for x in range(self.cols):
                rect = pygame.Rect(
                    self.origin[0] + x*(self.cell_size+self.spacing),
                    self.origin[1] + y*(self.cell_size+self.spacing),
                    self.cell_size, self.cell_size
                )
                if self.cells[y][x] == 0:
                    pygame.draw.rect(surface, (40, 60, 100), rect, border_radius=4)
                    shadow = rect.move(3, 3)
                    pygame.draw.rect(surface, (30, 40, 70), shadow, border_radius=4)
                else:
                    color = self.cells[y][x]
                    pygame.draw.rect(surface, color, rect, border_radius=4)
                    pygame.draw.rect(surface, (80, 80, 80), rect, 2, border_radius=4)

    def can_place_block(self, block, grid_x, grid_y):
        for by, row in enumerate(block.shape):
            for bx, cell in enumerate(row):
                if cell:
                    gx = grid_x + bx
                    gy = grid_y + by
                    if gx < 0 or gx >= self.cols or gy < 0 or gy >= self.rows:
                        return False
                    if self.cells[gy][gx] != 0:
                        return False
        return True

    def can_place_any_block(self, blocks):
        for block in blocks:
            for y in range(self.rows):
                for x in range(self.cols):
                    if self.can_place_block(block, x, y):
                        return True
        return False

    def place_block(self, block, grid_x, grid_y):
        for by, row in enumerate(block.shape):
            for bx, cell in enumerate(row):
                if cell:
                    gx = grid_x + bx
                    gy = grid_y + by
                    self.cells[gy][gx] = block.color

    def clear_full_lines_and_columns(self, game, return_positions=False):
        full_rows = [y for y in range(self.rows) if all(self.cells[y][x] != 0 for x in range(self.cols))]
        full_cols = [x for x in range(self.cols) if all(self.cells[y][x] != 0 for y in range(self.rows))]
        cleared = False
        cleared_positions = set()
        combo_count = len(full_rows) + len(full_cols)
        for y in full_rows:
            for x in range(self.cols):
                self.cells[y][x] = 0
                cleared_positions.add((x, y))
            game.score += self.cols
            cleared = True
        for x in full_cols:
            for y in range(self.rows):
                self.cells[y][x] = 0
                cleared_positions.add((x, y))
            game.score += self.rows
            cleared = True
        if cleared:
            game.play_line_clear_sound()
        if return_positions:
            return cleared, list(cleared_positions), combo_count
        return cleared 