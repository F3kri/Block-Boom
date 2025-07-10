import pygame
import random

CELL_SIZE = 50 
CELL_SPACING = 6

BLOCK_SHAPES = [
    # 1x1
    [[1]],
    # 1x2
    [[1,1]],
    # 2x1
    [[1],[1]],
    # 2x2
    [[1,1],[1,1]],
    # L
    [[1,0],[1,0],[1,1]],
    # Ligne 1x3
    [[1,1,1]],
    # Ligne 3x1
    [[1],[1],[1]],
    # T
    [[1,1,1],[0,1,0]],
]
BLOCK_COLORS = [
    (255, 120, 200), # rose
    (120, 200, 255), # bleu clair
    (255, 180, 80),  # orange
    (180, 120, 255), # violet
    (255, 80, 80),   # rouge
    (120, 255, 180), # vert clair
]

class Block:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.size = (len(shape[0]), len(shape))

    def draw(self, surface, x, y):
        for row_idx, row in enumerate(self.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        x + col_idx*(CELL_SIZE+CELL_SPACING),
                        y + row_idx*(CELL_SIZE+CELL_SPACING),
                        CELL_SIZE, CELL_SIZE
                    )
                    # Ombre
                    shadow_rect = rect.move(4, 4)
                    pygame.draw.rect(surface, (60, 60, 90), shadow_rect, border_radius=12)
                    # Bloc principal
                    pygame.draw.rect(surface, self.color, rect, border_radius=12)
                    # Bord
                    pygame.draw.rect(surface, (80,80,80), rect, 2, border_radius=12)

    def draw_preview(self, surface, x, y, valid=True):
        preview_color = self.color if valid else (180, 180, 180)
        s_width = self.size[0]*(CELL_SIZE+CELL_SPACING)-CELL_SPACING
        s_height = self.size[1]*(CELL_SIZE+CELL_SPACING)-CELL_SPACING
        s = pygame.Surface((s_width, s_height), pygame.SRCALPHA)
        for row_idx, row in enumerate(self.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        col_idx*(CELL_SIZE+CELL_SPACING),
                        row_idx*(CELL_SIZE+CELL_SPACING),
                        CELL_SIZE, CELL_SIZE
                    )
                    c = (*preview_color, 120)  # alpha 120
                    pygame.draw.rect(s, c, rect, border_radius=12)
                    pygame.draw.rect(s, (80,80,80,120), rect, 2, border_radius=12)
        surface.blit(s, (x, y))

    def count_cells(self):
        return sum(cell for row in self.shape for cell in row)

class BombBlock(Block):
    def __init__(self):
        super().__init__([[1]], (0,0,0))  # Couleur noire par défaut, non utilisée
        try:
            self.image = pygame.image.load("assets/bombe.png").convert_alpha()
            self.image = pygame.transform.smoothscale(self.image, (CELL_SIZE, CELL_SIZE))
        except Exception as e:
            print("Erreur chargement bombe.png:", e)
            self.image = None
    def draw(self, surface, x, y):
        if self.image:
            surface.blit(self.image, (x, y))
        else:
            pygame.draw.rect(surface, (0,0,0), pygame.Rect(x, y, CELL_SIZE, CELL_SIZE), border_radius=12)
    def draw_preview(self, surface, x, y, valid=True):
        if self.image:
            s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            s.blit(self.image, (0,0))
            if not valid:
                s.set_alpha(120)
            surface.blit(s, (x, y))
        else:
            color = (0,0,0,120) if not valid else (0,0,0)
            pygame.draw.rect(surface, color, pygame.Rect(x, y, CELL_SIZE, CELL_SIZE), border_radius=12)

def generate_block_set():
    return [Block(random.choice(BLOCK_SHAPES), random.choice(BLOCK_COLORS)) for _ in range(3)] 