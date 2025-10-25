from EnemyLinear import * # Make sure this imports Wall, SafeZone, Border, functions, settings

class Player(pygame.sprite.Sprite):
    """
    The player that moves to complete levels

    Attributes
    ----------
    game : Game
        The game that this player is in
    groups : sprite group
        All sprite groups this sprite belongs in
    image : surface
        The pygame surface that the player will be drawn on
    rect : rect
        Pygame rectangle
    rect.x : float
        The x coordinate of the player
    rect.y : float
        The y coordinate of the player
    vx : float
        The velocity in the x direction
    vy : float
        The velocity in the y direction
    direction : int
        Direction of player's total velocity
    speed : float
        The speed of the player
    size : int
        The side length of the square player
    fill : int list
        The color of the player in RGB
    border : int list
        The border color of the player in RGB
    moves : str
        String of move history
    changes : int
        Number of directional changes in velocity
    change_limit : int
        The limit of directional changes before the player is killed off
    current_target_checkpoint_index : int
        The index of the checkpoint this specific player is currently trying to reach
    inherited_moves : str
        String of moves inherited from the previous generation's best player
    current_move_index : int
        Index to track which inherited move is currently being executed
    hit : bool
        True if the player collided with an enemy

    Methods
    -------
    move(control : str) -> None
        Moves the player based on its control
    read_move(direction : int) -> None
        Manually moves player in the inputted direction
    update(None) -> None
        Updates player position
    wall_collision(None) -> None
        Checks for player collision with walls
    enemy_collision(None) -> None
        Checks for player collision with enemies
    respawn(None) -> None
        Moves the player back to its original starting position
    die(None) -> None
        Removes the player from all sprite groups and lists
    end_moves(None) -> None
        Kills the player and writes its moves to the moves file along with it score

    """

    def __init__(self, game, control, x, y, speed, size, fill, border):
        """
        Constructor to build a player

        Parameters
        ----------
        game : Game
            The game that this player is in
        control : str
            The type of control that this player will move to, 'keys', 'random', or 'hybrid'
        x : float
            The x coordinate of the player
        y : float
            The y coordinate of the player
        speed : float
            The speed of the player
        size : int
            The side length of the square player
        fill : int list
            The color of the player in RGB
        border : int list
            The color of the player border in RGB

	    Returns
        -------
        None

        """

        self.groups = game.all_sprites, game.players
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((size, size))
        self.image.fill(border)
        # The inner rectangle fill should be based on size, not hardcoded 20x20 if size changes
        pygame.draw.rect(self.image, fill, [4, 4, size - 8, size - 8]) # Adjusted to be relative to size
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
        self.change_limit = 100 # Limit for directional changes
        self.current_target_checkpoint_index = self.game.checkpoint_progress # THIS WAS THE FIX
        self.inherited_moves = '' # For 'hybrid' players to store moves from previous best
        self.current_move_index = 0 # To track progress through inherited_moves
        self.hit = False # True if the player collided with an enemy
        self.score_calculated = False # To prevent multiple score writings on death

    def move(self, control):
        """
        Moves the player in a direction based on its control type

        Parameters
        ----------
        control : str (e.g., 'keys', 'random')

        Returns
        -------
        None

        """

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
                # Adjust direction for diagonals
                if direction == 5: # moving down-left
                    direction = 6
                elif direction == 1: # moving up-left
                    direction = 8
                else: # just left
                    direction = 7
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vx = self.speed
                #Adjust direction for diagonals
                if direction == 5: # moving down-right
                    direction = 4
                elif direction == 1: # moving up-right
                    direction = 2
                else: # just right
                    direction = 3
            # Update direction and add to moves list
            self.direction = direction
            self.moves += str(self.direction)

        elif control == 'random':
            # 0 - rest, 1 - up, 2 - up right ... 8 - up left
            direction = random.randint(0, 8)
            # Probability of changing directions
            # Only change if the random number is 0 (1/11 chance to change direction)
            # This makes movement less chaotic than changing every tick
            change_chance = random.randint(0, 10) # 0 to 10, total 11 possibilities
            
            if change_chance == 0: # If we decide to change direction
                self.changes += 1 # Another directional change
                self.vx = 0
                self.vy = 0 # Reset velocity before setting new one

                if direction in [4, 5, 6]: # Down, Down-Left, Down-Right
                    self.vy = self.speed
                if direction in [8, 1, 2]: # Up, Up-Left, Up-Right
                    self.vy = -self.speed
                if direction in [6, 7, 8]: # Left, Down-Left, Up-Left
                    self.vx = -self.speed
                if direction in [2, 3, 4]: # Right, Up-Right, Down-Right
                    self.vx = self.speed
                self.direction = direction # Update current direction

            # Update moves list (even if direction didn't visually change,
            # this records the 'intent' or lack of change)
            self.moves += str(self.direction)

    def read_move(self, direction):
        """
        Manually moves player in the inputted direction

        Parameters
        ----------
        direction : int
            Direction of move (0-8)

        Returns
        -------
        None

        """

        # Move in inputted direction
        self.vx = 0
        self.vy = 0
        if direction in [4, 5, 6]: # Down, Down-Left, Down-Right
            self.vy = self.speed
        if direction in [8, 1, 2]: # Up, Up-Left, Up-Right
            self.vy = -self.speed
        if direction in [6, 7, 8]: # Left, Down-Left, Up-Left
            self.vx = -self.speed
        if direction in [2, 3, 4]: # Right, Up-Right, Down-Right
            self.vx = self.speed

    def update(self):
        """
        Updates player position and handles AI logic

        Parameters
        ----------
        None

        Returns
        -------
        None

        """

        # Check if direction change limit is reached (only for AI controlled players)
        if self.control in ['random', 'hybrid'] and self.changes > self.change_limit:
            self.end_moves()
            return # Player died, no further updates for this tick

        # Handle Rewinder logic (the lime player)
        if self.game.rewind:
            # Check if this player is the rewinder (assuming rewinder is always the last added player)
            # A more robust check might be self.fill == lime or passing a specific 'rewinder' control
            if self.fill == lime: # Assuming lime is exclusively for the rewinder
                if self.game.tick < self.game.best_moves_num_for_rewind:
                    # Execute inherited move
                    self.read_move(int(self.game.best_moves_for_rewind[self.game.tick]))
                    self.game.tick += 1
                    # Rewinder doesn't need to record its own 'moves' string for sorting
                else:
                    # Rewinder has finished its path
                    self.game.rewind = False
                    self.game.tick = 0 # Reset tick for next rewind phase

                    # Update starting position for next generation to rewinder's final position
                    self.game.checkx = self.rect.x
                    self.game.checky = self.rect.y
                    print(f"Rewinder finished. New generation starting point: ({self.game.checkx}, {self.game.checky})")

                    # Create the new generation of players
                    self.game.new_generation_players()

                    self.die() # The rewinder dies after creating the new generation
                    return # No further updates for the rewinder this tick
        else:
            # Logic for normal players (random or hybrid)
            if self.control == 'hybrid':
                if self.current_move_index < len(self.inherited_moves):
                    # Execute step from inherited moves
                    direction_from_inherited = int(self.inherited_moves[self.current_move_index])
                    self.read_move(direction_from_inherited)
                    self.current_move_index += 1
                    self.moves += str(direction_from_inherited) # Record this move
                else:
                    # After inherited moves, switch to random movement
                    self.move('random')
            elif self.control == 'random': # Initial generation players
                self.move('random')
            elif self.control == 'keys': # Manual player (if any)
                self.move('keys')
            # If control is anything else, player does not move

        # Apply velocity and check collisions
        self.rect.x += self.vx
        self.wall_collision('x')
        self.rect.y += self.vy
        self.wall_collision('y')
        self.enemy_collision() # This will call end_moves() if hit

        # Check for if a checkpoint has been reached (only for actual players, not rewinder)
        # Assuming rewinder's score isn't tracked in moves.txt
        if not self.game.rewind or self.fill != lime:
            if self.current_target_checkpoint_index < len(self.game.checkpoints_list):
                coordinates = self.game.checkpoints_list[self.current_target_checkpoint_index]

                # Calculate distance to center of the target checkpoint tile
                checkpoint_center_x = float(coordinates[0] + tile_size / 2)
                checkpoint_center_y = float(coordinates[1] + tile_size / 2)
                player_center_x = float(self.rect.x + self.size / 2)
                player_center_y = float(self.rect.y + self.size / 2)

                dist_to_checkpoint = math.hypot(checkpoint_center_x - player_center_x,
                                                  checkpoint_center_y - player_center_y)

                # If player is close enough to the checkpoint
                if dist_to_checkpoint <= 1.5 * tile_size: # 1.5 times tile size for some leniency
                    self.current_target_checkpoint_index += 1
                    # Update global game checkpoint progress if this player reached further
                    if self.current_target_checkpoint_index > self.game.checkpoint_progress:
                        self.game.checkpoint_progress = self.current_target_checkpoint_index
                        print(f"Player (Gen {self.game.generation}) reached checkpoint {self.game.checkpoint_progress -1}.")
                    
                    # If all checkpoints are reached, the AI has "passed the level"
                    if self.current_target_checkpoint_index >= len(self.game.checkpoints_list):
                        print(f"AI passed Level {self.game.level} in Generation {self.game.generation}!")
                        self.end_moves(passed_level=True) # Pass a flag indicating level completion
                        self.game.run = False # Stop the game loop

    def wall_collision(self, direction):
        """
        Checks for player collision with walls

        Parameters
        ----------
        direction : char
            The direction the player is hitting the wall in, x or y

        Return
        ------
        None

        """
        if direction == 'x':
            wall_hit = pygame.sprite.spritecollide(self, self.game.walls, False)
            if wall_hit:
                if self.vx > 0: # Moving right, hit wall from left
                    self.rect.right = wall_hit[0].rect.left
                if self.vx < 0: # Moving left, hit wall from right
                    self.rect.left = wall_hit[0].rect.right
                self.vx = 0 # Stop horizontal movement
        if direction == 'y':
            wall_hit = pygame.sprite.spritecollide(self, self.game.walls, False)
            if wall_hit:
                if self.vy > 0: # Moving down, hit wall from top
                    self.rect.bottom = wall_hit[0].rect.top
                if self.vy < 0: # Moving up, hit wall from bottom
                    self.rect.top = wall_hit[0].rect.bottom
                self.vy = 0 # Stop vertical movement

    def enemy_collision(self):
        """
        Checks for player collision with enemies

        Parameters
        ----------
        None

        Return
        ------
        None

        """

        enemy_hit = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if enemy_hit:
            self.hit = True
            self.end_moves() # Player dies on enemy hit

    def respawn(self):
        """
        Moves the player back to its original starting position (or last checkpoint)

        Parameters
        ----------
        None

        Return
        ------
        None

        """

        # For AI, respawn isn't typically used. Players just "die" and new ones are made.
        # But if you want to reuse players, this can be handy.
        self.rect.x = self.game.startx
        self.rect.y = self.game.starty
        # Reset velocities and other state
        self.vx = 0
        self.vy = 0
        self.direction = 0
        self.changes = 0
        self.current_target_checkpoint_index = 0
        self.moves = ''
        self.inherited_moves = ''
        self.current_move_index = 0
        self.hit = False
        self.score_calculated = False


    def die(self):
        """
        Removes the player from all sprite groups and lists

        Parameters
        ----------
        None

        Return
        ------
        None

        """

        # Remove from sprite lists
        self.game.all_sprites.remove(self)
        self.game.players.remove(self)
        # Remove from player list
        if self in self.game.player_list:
            self.game.player_list.remove(self)


    def end_moves(self, passed_level=False):
        """
        Kills the player and writes its moves to the moves file along with its score.
        Only writes if score hasn't been calculated for this player already.

        Parameters
        ----------
        passed_level : bool
            True if the player died because it completed the level.

        Return
        ------
        None

        """
        if self.score_calculated: # Prevent writing score multiple times
            return

        self.score_calculated = True # Mark score as calculated

        # Calculate score before dying
        score = checkpoint_score(self.game, self)

        # Writes moves pre death into moves file to be scored and sorted
        with open(moves_path, 'a') as file:
            file.write(f"Score: {score} Moves: {self.moves}\n")
        
        # If the level was passed, stop further processing
        if passed_level:
            self.game.run = False # Stop the game loop
            print(f"AI Successfully Completed Level {self.game.level}!")

        self.die()