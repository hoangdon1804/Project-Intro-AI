from EnemyLinear import *

class Player(pygame.sprite.Sprite):
    """
    The player that moves to complete levels
    """

    def __init__(self, game, control, x, y, speed, size, fill, border):
        self.groups = game.all_sprites, game.players
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((size, size))
        self.image.fill(border)
        pygame.draw.rect(self.image, fill, [4, 4, size - 8, size - 8])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vx = 0
        self.vy = 0
        self.direction = 0

        self.control = control
        self.speed = speed
        self.size = size
        self.fill = fill
        self.border = border

        # AI related attributes
        self.moves = ''
        self.changes = 0
        self.change_limit = 100
        self.inherited_moves = ''
        self.current_move_index = 0
        self.hit = False
        self.score_calculated = False
        
        # Theo dõi số frame trong vùng an toàn
        self.safe_zone_frames = 0

    def move(self, control):
        if control == 'keys':
            self.vx = 0
            self.vy = 0
            direction = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.vy = self.speed
                direction = 5
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.vy = -self.speed
                direction = 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vx = -self.speed
                if direction == 5: direction = 6
                elif direction == 1: direction = 8
                else: direction = 7
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vx = self.speed
                if direction == 5: direction = 4
                elif direction == 1: direction = 2
                else: direction = 3
            self.direction = direction
            self.moves += str(self.direction)

        elif control == 'random':
            direction = random.randint(0, 8)
            change_chance = random.randint(0, 10)
            
            if change_chance == 0:
                self.changes += 1
                self.vx = 0
                self.vy = 0
                if direction in [4, 5, 6]: self.vy = self.speed
                if direction in [8, 1, 2]: self.vy = -self.speed
                if direction in [6, 7, 8]: self.vx = -self.speed
                if direction in [2, 3, 4]: self.vx = self.speed
                self.direction = direction
            self.moves += str(self.direction)

    def read_move(self, direction):
        self.vx = 0
        self.vy = 0
        if direction in [4, 5, 6]: self.vy = self.speed
        if direction in [8, 1, 2]: self.vy = -self.speed
        if direction in [6, 7, 8]: self.vx = -self.speed
        if direction in [2, 3, 4]: self.vx = self.speed

    def update(self):
        # Kiểm tra chết do đi luẩn quẩn
        if self.control in ['random', 'hybrid'] and self.changes > self.change_limit:
            self.end_moves(cause_of_death='wander_death')
            return

        # Logic di chuyển
        if self.game.rewind:
            if self.fill == lime:
                # <<< ĐÂY LÀ DÒNG ĐÃ ĐƯỢC SỬA LỖI >>>
                # Tên biến đã được sửa từ best_moves_num_for_rewind thành best_move_num_for_rewind
                if self.game.tick < self.game.best_move_num_for_rewind:
                    self.read_move(int(self.game.best_move_for_rewind[self.game.tick]))
                    self.game.tick += 1
                else:
                    self.game.rewind = False
                    self.game.tick = 0
                    self.game.checkx = self.rect.x
                    self.game.checky = self.rect.y
                    self.game.new_generation_players()
                    self.die()
                    return
        else:
            if self.control == 'hybrid':
                if self.current_move_index < len(self.inherited_moves):
                    direction = int(self.inherited_moves[self.current_move_index])
                    self.read_move(direction)
                    self.current_move_index += 1
                    self.moves += str(direction)
                else:
                    self.move('random')
            elif self.control == 'random':
                self.move('random')

        # Áp dụng di chuyển và va chạm tường
        self.rect.x += self.vx
        self.wall_collision('x')
        self.rect.y += self.vy
        self.wall_collision('y')

        # Logic phạt và kiểm tra thắng
        if not self.game.rewind:
            zones_hit = pygame.sprite.spritecollide(self, self.game.zones, False)
            in_safe_zone = False
            for zone in zones_hit:
                if zone.type == 'j':
                    self.end_moves(cause_of_death='win')
                    return
                if zone.type in ['s', 'g', 'h']:
                    in_safe_zone = True
            
            if in_safe_zone:
                self.safe_zone_frames += 1

        # Kiểm tra va chạm enemy
        self.enemy_collision()

    def wall_collision(self, direction):
        if direction == 'x':
            wall_hit = pygame.sprite.spritecollide(self, self.game.walls, False)
            if wall_hit:
                if self.vx > 0: self.rect.right = wall_hit[0].rect.left
                if self.vx < 0: self.rect.left = wall_hit[0].rect.right
                self.vx = 0
        if direction == 'y':
            wall_hit = pygame.sprite.spritecollide(self, self.game.walls, False)
            if wall_hit:
                if self.vy > 0: self.rect.bottom = wall_hit[0].rect.top
                if self.vy < 0: self.rect.top = wall_hit[0].rect.bottom
                self.vy = 0

    def enemy_collision(self):
        enemy_hit = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if enemy_hit:
            self.hit = True
            self.end_moves(cause_of_death='enemy_hit')

    def respawn(self):
        self.rect.x = self.game.startx
        self.rect.y = self.game.starty
        self.vx = 0
        self.vy = 0
        self.moves = ''
        self.changes = 0
        self.hit = False
        self.score_calculated = False
        self.safe_zone_frames = 0

    def die(self):
        self.game.all_sprites.remove(self)
        self.game.players.remove(self)
        if self in self.game.player_list:
            self.game.player_list.remove(self)

    def end_moves(self, cause_of_death):
        if self.score_calculated:
            return
        self.score_calculated = True

        score = calculate_final_score(self.game, self, cause_of_death)

        with open(moves_path, 'a') as file:
            file.write(f"Score: {score} Moves: {self.moves}\n")
        
        if cause_of_death == 'win':
            self.game.run = False
            print(f"AI Successfully Completed Level {self.game.level}!")

        self.die()
