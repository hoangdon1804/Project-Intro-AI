import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, speed, size, fill, border, moves_sequence, change_limit):
        self.groups = game.all_sprites, game.players
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((size, size))
        self.image.fill(border)
        r_offset = random.randint(-20, 20); g_offset = random.randint(-20, 20); b_offset = random.randint(-20, 20)
        final_fill = (max(0, min(255, fill[0]+r_offset)), max(0, min(255, fill[1]+g_offset)), max(0, min(255, fill[2]+b_offset)))
        pygame.draw.rect(self.image, final_fill, [4, 4, size - 8, size - 8])
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y, self.speed, self.size = x, y, speed, size
        
        self.moves = moves_sequence
        self.change_limit = change_limit
        
        self.current_move_index = 0; self.is_alive = True; self.cause_of_death = ''
        self.safe_zone_frames = 0; self.actual_move_count = 0
        self.changes_in_random_phase = 0; self.last_direction = -1
        self.final_score = 0; self.final_distance = 0
        self.random_mode_direction = random.randint(0, 8)

    def _read_move(self, direction):
        vx, vy = 0, 0
        if direction in [4, 5, 6]: vy = self.speed
        if direction in [8, 1, 2]: vy = -self.speed
        if direction in [6, 7, 8]: vx = -self.speed
        if direction in [2, 3, 4]: vx = self.speed
        return vx, vy

    def _wall_collision(self, vx, vy):
        self.rect.x += vx
        wall_hit_x = pygame.sprite.spritecollide(self, self.game.walls, False)
        if wall_hit_x:
            if vx > 0: self.rect.right = wall_hit_x[0].rect.left
            if vx < 0: self.rect.left = wall_hit_x[0].rect.right
        self.rect.y += vy
        wall_hit_y = pygame.sprite.spritecollide(self, self.game.walls, False)
        if wall_hit_y:
            if vy > 0: self.rect.bottom = wall_hit_y[0].rect.top
            if vy < 0: self.rect.top = wall_hit_y[0].rect.bottom

    def update(self):
        if not self.is_alive: return
        
        action = 0
        is_in_programmed_phase = self.current_move_index < len(self.moves)

        if is_in_programmed_phase:
            action = int(self.moves[self.current_move_index])
        else:
            if random.randint(0, 10) == 0:
                self.random_mode_direction = random.randint(0, 8)
            action = self.random_mode_direction
        
        self.current_move_index += 1
        self.process_action(action, is_in_programmed_phase)

    def update_single_step(self, action):
        is_in_programmed_phase = self.current_move_index < len(self.moves)
        self.current_move_index += 1
        self.process_action(action, is_in_programmed_phase)
        
    def process_action(self, action, is_programmed):
        if action > 0: self.actual_move_count += 1
        
        if not is_programmed:
            if action != self.last_direction:
                self.changes_in_random_phase += 1
            if self.changes_in_random_phase > self.change_limit:
                self.die('wander_death'); return
        
        self.last_direction = action
        vx, vy = self._read_move(action)
        self._wall_collision(vx, vy)

    def die(self, cause):
        if not self.is_alive: return
        self.is_alive = False; self.cause_of_death = cause; self.kill()