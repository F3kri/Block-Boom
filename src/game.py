import pygame
import json
import os
from .grid import Grid
from .block import Block, generate_block_set, BombBlock
from .particle import Particle, create_particles
SETTINGS_FILE = os.path.join("stockage", "settings.json")

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
BEST_SCORE_FILE = os.path.join("stockage", "best_score.json")

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Block Boom")
        self.clock = pygame.time.Clock()
        self.grid = Grid(10, 10, origin=(320, 100))
        self.blocks = generate_block_set()
        self.selected_block = None
        self.selected_block_index = None
        self.score = 0
        self.running = True
        self.font = pygame.font.SysFont(None, 36)
        self.drag_pos = (0, 0)
        self.particles = []
        self.score_anim_timer = 0
        self.game_over = False
        self.best_score = self.load_best_score()
        self.slow_motion_timer = 0
        self.combo_flash_timer = 0
        self.combo_flash_color = (255,255,255)
        self.show_settings_menu = False
        self.sound_enabled = True
        self.load_settings()
        try:
            self.crown_img = pygame.image.load("assets/crown.png").convert_alpha()
            self.crown_img = pygame.transform.smoothscale(self.crown_img, (48, 48))
        except Exception as e:
            print("Erreur chargement couronne:", e)
            self.crown_img = None
        try:
            self.line_clear_sound = pygame.mixer.Sound("sounds/2.mp3")
        except Exception as e:
            print("Erreur chargement son 2:", e)
            self.line_clear_sound = None
        try:
            self.piece_detache_sound = pygame.mixer.Sound("sounds/3.mp3")
        except Exception as e:
            print("Erreur chargement son 3:", e)
            self.piece_detache_sound = None
        try:
            self.invalid_drop_sound = pygame.mixer.Sound("sounds/4.mp3")
        except Exception as e:
            print("Erreur chargement son 4:", e)
            self.invalid_drop_sound = None
        self.has_bomb = False
        self.bomb_given = False
        self.in_main_menu = True
        self.menu_options = ["Jouer", "Paramètres", "Quitter"]
        self.menu_selected = 0
        self.game_mode = None
        self.timer_30s = 30
        self.timer_started = False

    def load_best_score(self):
        if os.path.exists(BEST_SCORE_FILE):
            try:
                with open(BEST_SCORE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("best_score", 0)
            except Exception as e:
                print("Erreur lecture best_score.json:", e)
        return 0

    def save_best_score(self):
        try:
            with open(BEST_SCORE_FILE, "w", encoding="utf-8") as f:
                json.dump({"best_score": self.best_score}, f)
        except Exception as e:
            print("Erreur écriture best_score.json:", e)

    def play_line_clear_sound(self):
        if self.line_clear_sound and self.sound_enabled:
            self.line_clear_sound.play()

    def play_piece_detache_sound(self):
        if self.piece_detache_sound and self.sound_enabled:
            self.piece_detache_sound.play()

    def play_invalid_drop_sound(self):
        if self.invalid_drop_sound and self.sound_enabled:
            self.invalid_drop_sound.play()

    def add_particles(self, positions, color):
        for (x, y) in positions:
            px = self.grid.origin[0] + x * (self.grid.cell_size + self.grid.spacing) + self.grid.cell_size // 2
            py = self.grid.origin[1] + y * (self.grid.cell_size + self.grid.spacing) + self.grid.cell_size // 2
            self.particles.extend(create_particles(px, py, color))

    def trigger_score_animation(self):
        self.score_anim_timer = 12  # durée de l'effet (frames)

    def trigger_combo_effects(self, combo_count, cleared_positions):
        if combo_count >= 3:
            self.slow_motion_timer = 18  # 0.3s à 60 FPS
            self.combo_flash_timer = 10
            import random
            self.combo_flash_color = random.choice([(255,255,180),(180,255,255),(255,180,255),(255,255,255)])
            # Explosions colorées
            import random
            for (x, y) in cleared_positions:
                px = self.grid.origin[0] + x * (self.grid.cell_size + self.grid.spacing) + self.grid.cell_size // 2
                py = self.grid.origin[1] + y * (self.grid.cell_size + self.grid.spacing) + self.grid.cell_size // 2
                color = random.choice([(255,255,180),(180,255,255),(255,180,255),(255,255,255)])
                self.particles.extend(create_particles(px, py, color, n=18))

    def reset(self):
        self.grid = Grid(10, 10, origin=(320, 100))
        self.blocks = generate_block_set()
        self.selected_block = None
        self.selected_block_index = None
        self.score = 0
        self.particles = []
        self.score_anim_timer = 0
        self.game_over = False
        self.bomb_given = False
        self.timer_started = False

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.sound_enabled = data.get("sound_enabled", True)
                    self.game_mode = data.get("game_mode", "normal")
            except Exception as e:
                print("Erreur lecture settings.json:", e)

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump({"sound_enabled": self.sound_enabled, "game_mode": self.game_mode}, f)
        except Exception as e:
            print("Erreur écriture settings.json:", e)

    def run(self):
        while self.running:
            if self.in_main_menu:
                self.handle_menu_events()
                self.draw_main_menu()
                self.clock.tick(60)
                continue
            self.handle_events()
            # Si on quitte les paramètres depuis le menu principal, on revient au menu principal
            if not self.show_settings_menu and hasattr(self, 'was_in_settings_from_menu') and self.was_in_settings_from_menu:
                self.in_main_menu = True
                self.was_in_settings_from_menu = False
                continue
            self.update()
            # Donne une bombe si le score atteint 50 et pas déjà donnée
            if self.score >= 50 and not self.bomb_given:
                self.blocks.append(BombBlock())
                self.bomb_given = True
            self.draw()
            if self.slow_motion_timer > 0:
                pygame.time.delay(40)  # ralentit la boucle
            self.clock.tick(60)

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if self.menu_options[self.menu_selected] == "Jouer":
                        self.in_main_menu = False
                        if self.game_mode == "30s":
                            self.timer_30s = 30
                            self.timer_started = True
                    elif self.menu_options[self.menu_selected] == "Paramètres":
                        self.show_settings_menu = True
                        self.was_in_settings_from_menu = True
                        self.in_main_menu = False
                    elif self.menu_options[self.menu_selected] == "Quitter":
                        self.running = False

    def draw_main_menu(self):
        self.screen.fill((30, 40, 70))
        font = pygame.font.SysFont(None, 80)
        title = font.render("Block Boom", True, (255, 215, 0))
        rect = title.get_rect(center=(self.screen.get_width()//2, 150))
        self.screen.blit(title, rect)
        font2 = pygame.font.SysFont(None, 48)
        for i, option in enumerate(self.menu_options):
            color = (255,255,255) if i != self.menu_selected else (255, 215, 0)
            opt_text = font2.render(option, True, color)
            opt_rect = opt_text.get_rect(center=(self.screen.get_width()//2, 300 + i*80))
            self.screen.blit(opt_text, opt_rect)
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Gestion du menu paramètres
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Si on quitte les paramètres et on venait du menu principal, on ne lance pas le jeu
                if hasattr(self, 'was_in_settings_from_menu') and self.was_in_settings_from_menu:
                    self.show_settings_menu = False
                    return
                self.show_settings_menu = not self.show_settings_menu
                return
            if self.show_settings_menu:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.sound_enabled = not self.sound_enabled
                        self.save_settings()
                        if self.sound_enabled:
                            pygame.mixer.music.set_volume(1.0)
                        else:
                            pygame.mixer.music.set_volume(0.0)
                    elif event.key == pygame.K_m:
                        if self.game_mode == "normal" or self.game_mode is None:
                            self.game_mode = "30s"
                        else:
                            self.game_mode = "normal"
                        self.save_settings()
                    if event.key == pygame.K_ESCAPE:
                        self.show_settings_menu = False
                return
            if self.game_over:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.reset()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, block in enumerate(self.blocks):
                    bx = 80
                    by = 180 + i*140
                    bw = block.size[0]*50
                    bh = block.size[1]*50
                    rect = pygame.Rect(bx, by, bw, bh)
                    if rect.collidepoint(mx, my):
                        self.selected_block = block
                        self.selected_block_index = i
                        self.drag_pos = (mx, my)
                        break
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.selected_block is not None:
                    mx, my = event.pos
                    grid_x = (mx - self.grid.origin[0]) // (self.grid.cell_size + self.grid.spacing)
                    grid_y = (my - self.grid.origin[1]) // (self.grid.cell_size + self.grid.spacing)
                    # Si c'est une bombe, explosion 3x3
                    from .block import BombBlock
                    if isinstance(self.selected_block, BombBlock):
                        # Vérifie si le centre est bien sur la grille
                        if 0 <= grid_x < self.grid.cols and 0 <= grid_y < self.grid.rows:
                            for dy in range(-1, 2):
                                for dx in range(-1, 2):
                                    gx = grid_x + dx
                                    gy = grid_y + dy
                                    if 0 <= gx < self.grid.cols and 0 <= gy < self.grid.rows:
                                        self.grid.cells[gy][gx] = 0
                            del self.blocks[self.selected_block_index]
                        # Sinon, ne rien faire (la bombe reste dans la liste)
                        self.selected_block = None
                        self.selected_block_index = None
                        return
                    if self.grid.can_place_block(self.selected_block, grid_x, grid_y):
                        self.grid.place_block(self.selected_block, grid_x, grid_y)
                        self.score += self.selected_block.count_cells()
                        cleared, cleared_positions, combo_count = self.grid.clear_full_lines_and_columns(self, return_positions=True)
                        if cleared:
                            self.add_particles(cleared_positions, (255, 255, 255))
                            self.trigger_score_animation()
                            self.trigger_combo_effects(combo_count, cleared_positions)
                        if not cleared:
                            self.play_piece_detache_sound()
                        del self.blocks[self.selected_block_index]
                        # Si après suppression il ne reste que la bombe, on regénère 3 pièces de base
                        from .block import BombBlock
                        # On cherche la position de la bombe (si elle existe)
                        bomb_indices = [i for i, b in enumerate(self.blocks) if isinstance(b, BombBlock)]
                        base_blocks = [b for b in self.blocks if not isinstance(b, BombBlock)]
                        if len(base_blocks) == 0:
                            if bomb_indices:
                                bomb_index = bomb_indices[0]
                                # On régénère les blocs de base et on insère la bombe à sa position initiale
                                new_blocks = generate_block_set()
                                self.blocks = new_blocks[:bomb_index] + [self.blocks[bomb_index]] + new_blocks[bomb_index:]
                            else:
                                self.blocks = generate_block_set()
                        if not self.grid.can_place_any_block(self.blocks):
                            self.game_over = True
                            if self.score > self.best_score:
                                self.best_score = self.score
                                self.save_best_score()
                    else:
                        self.play_invalid_drop_sound()
                    self.selected_block = None
                    self.selected_block_index = None
            elif event.type == pygame.MOUSEMOTION:
                if self.selected_block is not None:
                    self.drag_pos = event.pos

    def update(self):
        self.particles = [p for p in self.particles if p.is_alive()]
        for p in self.particles:
            p.update()
        if self.score_anim_timer > 0:
            self.score_anim_timer -= 1
        if self.slow_motion_timer > 0:
            self.slow_motion_timer -= 1
        if self.combo_flash_timer > 0:
            self.combo_flash_timer -= 1
        # Gestion du timer 30 secondes
        if self.game_mode == "30s" and self.timer_started:
            self.timer_30s -= 1/60  # 60 FPS
            if self.timer_30s <= 0:
                self.game_over = True
                if self.score > self.best_score:
                    self.best_score = self.score
                    self.save_best_score()

    def draw(self):
        # Effet flash combo
        if self.combo_flash_timer > 0:
            self.screen.fill(self.combo_flash_color)
        else:
            self.screen.fill((74, 108, 179))
        x, y = 15, 15
        if self.crown_img:
            self.screen.blit(self.crown_img, (x, y))
            best_font = pygame.font.SysFont(None, 48)
            best_score_surf = best_font.render(f"{self.best_score}", True, (255, 215, 0))
            self.screen.blit(best_score_surf, (x + 58, y + 10))
        else:
            best_font = pygame.font.SysFont(None, 48)
            best_score_surf = best_font.render(f"{self.best_score}", True, (255, 215, 0))
            self.screen.blit(best_score_surf, (x, y))
        # Effet d'animation sur le score
        base_size = 64
        if self.score_anim_timer > 0:
            scale = 1.0 + 0.5 * (self.score_anim_timer / 12)
        else:
            scale = 1.0
        font_size = int(base_size * scale)
        anim_font = pygame.font.SysFont(None, font_size)
        score_surf = anim_font.render(f"{self.score}", True, (255,255,255))
        grid_x = self.grid.origin[0]
        grid_w = self.grid.cell_size * self.grid.cols + self.grid.spacing * (self.grid.cols - 1)
        score_rect = score_surf.get_rect(center=(grid_x + grid_w//2, self.grid.origin[1] - 40))
        self.screen.blit(score_surf, score_rect)
        self.grid.draw(self.screen)
        for p in self.particles:
            p.draw(self.screen)
        for i, block in enumerate(self.blocks):
            if self.selected_block is not None and i == self.selected_block_index:
                continue
            block.draw(self.screen, 80, 180 + i*140)
        if self.selected_block is not None:
            mx, my = self.drag_pos
            self.selected_block.draw(self.screen, mx, my)
            grid_x = (mx - self.grid.origin[0]) // (self.grid.cell_size + self.grid.spacing)
            grid_y = (my - self.grid.origin[1]) // (self.grid.cell_size + self.grid.spacing)
            if self.grid.can_place_block(self.selected_block, grid_x, grid_y):
                px = self.grid.origin[0] + grid_x * (self.grid.cell_size + self.grid.spacing)
                py = self.grid.origin[1] + grid_y * (self.grid.cell_size + self.grid.spacing)
                self.selected_block.draw_preview(self.screen, px, py, valid=True)
        # Affichage du timer en mode 30 secondes
        if self.game_mode == "30s" and self.timer_started:
            timer_font = pygame.font.SysFont(None, 48)
            timer_text = timer_font.render(f"Temps: {int(self.timer_30s)}s", True, (255, 255, 0))
            timer_rect = timer_text.get_rect(center=(self.screen.get_width()//2, 50))
            self.screen.blit(timer_text, timer_rect)
        # Affichage de l'écran de défaite
        if self.game_over:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            font = pygame.font.SysFont(None, 80)
            if self.game_mode == "30s":
                text = font.render("Temps écoulé !", True, (255, 80, 80))
            else:
                text = font.render("Défaite !", True, (255, 80, 80))
            rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 60))
            self.screen.blit(text, rect)
            font2 = pygame.font.SysFont(None, 48)
            score_text = font2.render(f"Score : {self.score}", True, (255,255,255))
            rect2 = score_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 10))
            self.screen.blit(score_text, rect2)
            best_text = font2.render(f"Meilleur : {self.best_score}", True, (255, 215, 0))
            rect_best = best_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 60))
            self.screen.blit(best_text, rect_best)
            font3 = pygame.font.SysFont(None, 36)
            restart_text = font3.render("Cliquez pour recommencer", True, (255,255,0))
            rect3 = restart_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 120))
            self.screen.blit(restart_text, rect3)
        # Affichage du menu paramètres si activé
        if self.show_settings_menu:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0,0,0,180))
            self.screen.blit(overlay, (0,0))
            font = pygame.font.SysFont(None, 64)
            text = font.render("Paramètres", True, (255,255,255))
            rect = text.get_rect(center=(self.screen.get_width()//2, 180))
            self.screen.blit(text, rect)
            font2 = pygame.font.SysFont(None, 40)
            sound_status = "Activé" if self.sound_enabled else "Désactivé"
            sound_text = font2.render(f"Son : {sound_status} (S)", True, (255,255,0))
            rect2 = sound_text.get_rect(center=(self.screen.get_width()//2, 300))
            self.screen.blit(sound_text, rect2)
            mode_status = "30 Secondes" if self.game_mode == "30s" else "Normal"
            mode_text = font2.render(f"Mode : {mode_status} (M)", True, (255,255,0))
            rect3 = mode_text.get_rect(center=(self.screen.get_width()//2, 380))
            self.screen.blit(mode_text, rect3)
            quit_text = font2.render("Appuyez sur Echap pour fermer", True, (200,200,200))
            rect4 = quit_text.get_rect(center=(self.screen.get_width()//2, 460))
            self.screen.blit(quit_text, rect4)
            pygame.display.flip()
            return
        pygame.display.flip() 