init python:
    # RenPyStein - A Wolfenstein 3D-style Raycasting Engine for Ren'Py
    # Main Engine File
    # Credits:
    # Original Python code "Gh0stenstein" by gh0st (http://code.google.com/p/gh0stenstein/)
    # Original Ren'Py coder by SusanTheCat (https://lemmasoft.renai.us/forums/viewtopic.php?t=15329)
    # Adapted and extended for Ren'Py 8.3.7 with multitouch, optimizations, 
    # and state persistence by just6889 (https://github.com/Just3090)

    import math
    import pygame

    # As suggested in a issue in Ren'Py GitHub (https://github.com/renpy/renpy/issues/4292), 
    # we must explicitly enable multitouch events.
    # This is crucial for FINGERUP, FINGERDOWN, and FINGERMOTION events to be recognized on mobile devices.
    config.pygame_events.extend([
        pygame.FINGERMOTION,
        pygame.FINGERDOWN,
        pygame.FINGERUP,
    ])

    # Global flag to switch between keyboard and touch/mouse controls.
    # This is controlled by the in-game UI.
    simulate_touch = False

    # --- Constants ---
    texWidth = 64   # Texture width in pixels
    texHeight = 64  # Texture height in pixels
    twoPI = math.pi * 2

    class Player(object):
        """
        Handles the player's state, movement, and collision detection.
        """
        def __init__(self, wm, x, y, dirx, diry, planex, planey):
            self.wm = wm  # WorldManager reference, used for collision checks.
            # Player position vector
            self.x = x
            self.y = y
            # Player direction vector
            self.dirx = float(dirx)
            self.diry = float(diry)
            # The 2D camera plane vector, perpendicular to the direction vector.
            self.planex = float(planex)
            self.planey = float(planey)
            
            self.health = 100
            self.current_weapon_name = "fist"
            
            # --- Movement state variables ---
            self.rot = math.atan2(diry, dirx) # Player rotation in radians
            self.planerot = math.atan2(planey, planex) # Camera plane rotation
            self.dir = 0            # Rotation direction: 1 for right, -1 for left
            self.speed = 0          # Forward/backward speed: 1 for fwd, -1 for bwd
            self.strafe_speed = 0   # Strafe speed: 1 for left, -1 for right

            # --- Movement parameters ---
            self.moveSpeed = 2.5  # Units per second
            self.rotSpeed = 90 * math.pi / 180  # Radians per second

            # Map dimensions for boundary checks
            self.mapWidth = len(wm.worldMap[0])
            self.mapHeight = len(wm.worldMap)
            
        def move(self, dt):
            """
            Updates the player's position and rotation based on current input state and delta time.
            Args:
                dt (float): Delta time, the time elapsed since the last frame.
            """
            moveStep = self.speed * self.moveSpeed * dt
            strafeStep = self.strafe_speed * self.moveSpeed * dt
            
            # Update rotation
            self.rot += self.dir * self.rotSpeed * dt
            self.rot %= twoPI
            self.planerot += self.dir * self.rotSpeed * dt
            self.planerot %= twoPI

            # Calculate new potential position based on forward/backward movement
            newX = self.x + math.cos(self.rot) * moveStep
            newY = self.y + math.sin(self.rot) * moveStep

            # Add strafing movement to the new position
            newX += math.cos(self.planerot) * strafeStep
            newY += math.sin(self.planerot) * strafeStep
            
            # Update direction and plane vectors from the new rotation angle
            self.dirx = math.cos(self.rot)
            self.diry = math.sin(self.rot)
            self.planex = math.cos(self.planerot)
            self.planey = math.sin(self.planerot)
            
            # Check for collisions and update the final position
            position = self.checkCollision(self.x, self.y, newX, newY, 0.45)
            self.x = position[0]
            self.y = position[1]

        def isBlocking(self, x, y):
            """Checks if a map tile is a solid wall."""
            return self.wm.worldMap[int(x)][int(y)] != 0 

        def checkCollision(self, fromX, fromY, toX, toY, radius):
            """A simple but effective collision detection that prevents walking through walls."""
            # This simplified implementation primarily checks the destination point and its immediate neighbors.
            pos = [fromX, fromY]
 
            if toY < 0 or toY >= self.mapHeight or toX < 0 or toX >= self.mapWidth:
                return pos
   
            blockX = math.floor(toX)
            blockY = math.floor(toY)
   
            if self.isBlocking(blockX, blockY):
                return pos
 
            pos[0] = toX
            pos[1] = toY
            
            # Further checks could be added here for more precise collision sliding,
            # but for this engine, this basic check is sufficient.
            
            return pos 

    class Projectile(object):
        """
        Represents a moving projectile (a bullet).
        """
        def __init__(self, wm, x, y, dir_x, dir_y, texture_index, damage, fired_by_player=False):
            self.wm = wm
            self.x = x
            self.y = y
            self.dir_x = dir_x
            self.dir_y = dir_y
            self.texture_index = texture_index
            self.damage = damage
            self.fired_by_player = fired_by_player
            self.speed = 8.0 # Projectile speed in units per second

        def update(self, dt):
            """
            Moves the projectile and checks for collisions.
            Returns:
                bool: False if the projectile should be destroyed, True otherwise.
            """
            new_x = self.x + self.dir_x * self.speed * dt
            new_y = self.y + self.dir_y * self.speed * dt

            # Check for collision with walls
            if self.wm.worldMap[int(new_x)][int(new_y)] > 0:
                return False # Hit a wall, destroy projectile

            self.x = new_x
            self.y = new_y

            if not self.fired_by_player:
                # Projectile from enemy, check against player
                player = self.wm.player
                dist_to_player = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
                if dist_to_player < 0.5: # Player hitbox
                    player.health -= self.damage
                    self.wm.damage_flash_timer = 0.2
                    renpy.sound.play("sounds/ow.ogg", channel=2)
                    return False # Hit the player, destroy projectile
            else:
                # Projectile from player, check against enemies
                for enemy in self.wm.enemies:
                    dist_to_enemy = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                    if dist_to_enemy < 0.5: # Enemy hitbox
                        enemy.health -= self.damage
                        if enemy.health <= 0:
                            renpy.sound.play("sounds/ow.ogg", channel=1)
                            self.wm.enemies.remove(enemy)
                            self.wm.sprite_positions.append((enemy.x, enemy.y, enemy.destroyed_texture_index))
                        return False

            return True # Projectile is still active

    class BaseEnemy(object):
        """
        A generic base class for all enemies. Handles shared logic like
        state management, line-of-sight, and movement.
        """
        def __init__(self, wm, x, y, health=100):
            self.wm = wm
            self.x = x
            self.y = y
            self.health = health
            self.state = 'idle' # 'idle', 'chasing', 'attacking'
            
            # These will be overridden by subclasses
            self.texture_index = 0
            self.destroyed_texture_index = 0
            self.moveSpeed = 1.5 
            self.rotSpeed = 75 * math.pi / 180
            self.attack_range = 8.0
            self.sight_range = 15.0
            self.attack_cooldown = 1.5
            self.damage = 10
            
            self.attack_timer = 0.0
            self.mapWidth = len(wm.worldMap[0])
            self.mapHeight = len(wm.worldMap)

        def update(self, dt, player):
            """
            Updates the enemy's state machine and acts accordingly.
            Can be overridden for more complex behaviors.
            """
            self.attack_timer = max(0, self.attack_timer - dt)

            player_x, player_y = player.x, player.y
            dist_to_player = math.sqrt((player_x - self.x)**2 + (player_y - self.y)**2)

            # State transitions
            if self.state == 'idle':
                if dist_to_player < self.sight_range and self.has_line_of_sight(player_x, player_y):
                    self.state = 'chasing'
            
            elif self.state == 'chasing':
                # Check if we should go back to idle
                if dist_to_player > self.sight_range or not self.has_line_of_sight(player_x, player_y):
                    self.state = 'idle'
                    return

                # Move if not in the ideal attack sweet spot
                if dist_to_player > self.attack_range or dist_to_player < self.attack_range * 0.8:
                    self.move(dt, player_x, player_y)
                
                # Attack if in range and cooldown is ready
                if dist_to_player < self.attack_range and self.attack_timer == 0:
                    self.attack(player)

        def attack(self, player):
            """
            Placeholder for the attack action. To be overridden by subclasses.
            """
            self.attack_timer = self.attack_cooldown
            # Base enemy does nothing XD
            pass

        def move(self, dt, target_x, target_y):
            """
            Moves the enemy towards a target position.
            """
            angle_to_target = math.atan2(target_y - self.y, target_x - self.x)
            moveStep = self.moveSpeed * dt
            
            newX = self.x + math.cos(angle_to_target) * moveStep
            newY = self.y + math.sin(angle_to_target) * moveStep
            
            position = self.checkCollision(self.x, self.y, newX, newY, 0.45)
            self.x = position[0]
            self.y = position[1]

        def has_line_of_sight(self, target_x, target_y):
            """
            Checks for a clear line of sight to the target using a DDA-like grid traversal.
            """
            ray_start_x, ray_start_y = self.x, self.y
            ray_dir_x = target_x - ray_start_x
            ray_dir_y = target_y - ray_start_y
            
            ray_len = math.sqrt(ray_dir_x**2 + ray_dir_y**2)
            if ray_len == 0: return True

            ray_dir_x /= ray_len
            ray_dir_y /= ray_len

            if ray_dir_x == 0: ray_dir_x = 1e-9
            if ray_dir_y == 0: ray_dir_y = 1e-9
            
            delta_dist_x = abs(1 / ray_dir_x)
            delta_dist_y = abs(1 / ray_dir_y)
            
            map_x, map_y = int(ray_start_x), int(ray_start_y)
            
            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (ray_start_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - ray_start_x) * delta_dist_x

            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (ray_start_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - ray_start_y) * delta_dist_y

            current_dist = 0
            while current_dist < ray_len:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    current_dist = side_dist_x
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    current_dist = side_dist_y
                
                if self.isBlocking(map_x, map_y):
                    return False
            
            return True

        def isBlocking(self, x, y):
            """Checks if a map tile is a solid wall."""
            if not (0 <= x < self.mapWidth and 0 <= y < self.mapHeight):
                return True
            return self.wm.worldMap[int(x)][int(y)] != 0 

        def checkCollision(self, fromX, fromY, toX, toY, radius):
            """A simple collision detection."""
            pos = [fromX, fromY]
 
            if toY < 0 or toY >= self.mapHeight or toX < 0 or toX >= self.mapWidth:
                return pos
   
            blockX = math.floor(toX)
            blockY = math.floor(toY)
   
            if self.isBlocking(blockX, blockY):
                return pos
 
            pos[0] = toX
            pos[1] = toY
            
            return pos

    class Guard(BaseEnemy):
        """
        A specific enemy type: the fucking Guard.
        """
        def __init__(self, wm, x, y, texture_index, destroyed_texture_index, health=100):
            super(Guard, self).__init__(wm, x, y, health)
            self.texture_index = texture_index
            self.destroyed_texture_index = destroyed_texture_index
            self.moveSpeed = 1.5
            self.damage = 10
            self.bullet_texture_index = 6 # The index of bullet.png in sprite_paths

        def attack(self, player):
            """
            The Guard's attack: fire a projectile at the player.
            """
            super(Guard, self).attack(player) # Handles attack timer reset
            
            # Calculate direction vector towards player
            dir_x = player.x - self.x
            dir_y = player.y - self.y
            dist = math.sqrt(dir_x**2 + dir_y**2)
            
            # Normalize the direction vector
            if dist > 0:
                dir_x /= dist
                dir_y /= dist

            # Create and spawn the projectile
            bullet = Projectile(
                wm=self.wm, 
                x=self.x, 
                y=self.y, 
                dir_x=dir_x, 
                dir_y=dir_y, 
                texture_index=self.bullet_texture_index, 
                damage=self.damage,
                fired_by_player=False
            )
            self.wm.projectiles.append(bullet)
            
            # pew
            renpy.sound.play("sounds/pew.ogg", channel=3)

    class Renpystein(renpy.Displayable):
        """
        The main class for the raycasting engine. It's a Ren'Py Displayable,
        meaning it handles its own rendering and event processing.
        """
        # The constructor no longer takes player state or enemy lists, as those are loaded from the persistent store.
        def __init__(self, width, height, worldMap, exits, internal_width=None, internal_height=None, **kwargs):
            super(Renpystein, self).__init__(**kwargs)
            self.width = width
            self.height = height
            
            # OPTIMIZATION: Set the internal rendering resolution.
            # The 3D scene is rendered to this smaller surface and then scaled up.
            self.internal_width = internal_width if internal_width is not None else width
            self.internal_height = internal_height if internal_height is not None else height
            
            self.oldst = None

            # Unified dictionary to track each finger or mouse button.
            # This is the single source of truth for touch/mouse controls.
            self.active_fingers = {} 

            # Asset paths
            self.sprite_paths = [  
                "pics/items/barrel.png", "pics/items/pillar.png",
                "pics/items/greenlight.png", "pics/items/pillar_destroyed.png",
                "pics/enemies/guard.png",
                "pics/enemies/guard_d.png",
                "pics/items/bullet.png",
            ]
            self.image_paths = [  
                "pics/walls/eagle.png", "pics/walls/redbrick.png",
                "pics/walls/purplestone.png", "pics/walls/greystone.png",
                "pics/walls/bluestone.png", "pics/walls/mossy.png",
                "pics/walls/wood.png", "pics/walls/colorstone.png",
            ]
            
            # --- Game State Loading ---
            # The game state is loaded from Ren'Py's persistent store (renpy.store).
            # This ensures that the game resumes at the exact same spot after UI interactions (like menus or changing settings).
            self.worldMap = worldMap
            self.player = Player(self, renpy.store.player_x, renpy.store.player_y, renpy.store.player_dirx, renpy.store.player_diry, renpy.store.player_planex, renpy.store.player_planey)
            if hasattr(renpy.store, 'stein_player_health'):
                self.player.health = renpy.store.stein_player_health
            if hasattr(renpy.store, 'stein_current_weapon'):
                self.player.current_weapon_name = renpy.store.stein_current_weapon

            self.sprite_positions = renpy.store.stein_sprites
            self.exits = exits
            
            self.enemies = []
            for e_data in renpy.store.stein_enemies:
                # e_data can be a 4-element tuple (legacy) or 5-element (with health)
                if len(e_data) == 5:
                    self.enemies.append(Guard(self, e_data[0], e_data[1], e_data[2], e_data[3], health=e_data[4]))
                else:
                    self.enemies.append(Guard(self, e_data[0], e_data[1], e_data[2], e_data[3]))

            self.projectiles = []
            
            self.weapons = {
                "fist": Weapon("fist", 5, 1, damage=100, projectile_type=None),
                "gun": Weapon("gun", 5, 1, damage=50, projectile_type='bullet')
            }
            self.bullet_texture_index = 6 

            self.won = None
            self.damage_flash_timer = 0.0
            self.mouse_initialized = False
            
        def render(self, width, height, st, at):
            """ The main rendering loop, called by Ren'Py on every frame. """
            
            # --- 1. LAZY CACHING OF PYGAME SURFACES ---
            # On the first frame, load all textures and prepare them for rendering.
            if not hasattr(self, 'image_renders'):
                # Load wall textures
                wall_surfs = []
                for path in self.image_paths:
                    with renpy.open_file(path) as f:
                        surf = pygame.image.load(f).convert_alpha()
                    wall_surfs.append(pygame.transform.scale(surf, (texWidth, texHeight)))

                # Create darkened versions for walls on the Y-axis to simulate shadow
                dark_surfs = []
                for surf in wall_surfs:
                    dark_surf = surf.copy()
                    darkener = pygame.Surface(surf.get_size(), flags=pygame.SRCALPHA)
                    darkener.fill((0, 0, 0, 128))
                    dark_surf.blit(darkener, (0,0))
                    dark_surfs.append(dark_surf)
                
                self.image_renders = wall_surfs + dark_surfs

                # Load sprite textures
                self.sprite_renders = []
                for path in self.sprite_paths:
                    with renpy.open_file(path) as f:
                        surf = pygame.image.load(f).convert_alpha()
                    self.sprite_renders.append(pygame.transform.scale(surf, (texWidth, texHeight)))

                # Load and cache the background at the internal resolution
                with renpy.open_file("pics/background.png") as f:
                    bg_surf = pygame.image.load(f).convert()
                self.bg_surf_cached = pygame.transform.scale(bg_surf, (self.internal_width, self.internal_height))

            # --- 2. UPDATE GAME LOGIC ---
            # Calculate delta time (time since last frame)
            if self.oldst is None: self.oldst = st
            dtime = st - self.oldst
            self.oldst = st
            
            if self.won is None:
                # Update timers
                self.damage_flash_timer = max(0, self.damage_flash_timer - dtime)

                # Update player state from touch/mouse inputs
                if simulate_touch:
                    self.update_player_from_touch_state()

                # Move the player
                self.player.move(dtime)
                
                # Update enemies
                self.update_enemies(dtime)

                # Update projectiles
                self.update_projectiles(dtime)

                if self.player.health <= 0:
                    self.player.health = 0
                    self.won = 'game_over'

            # --- 3. SAVE PERSISTENT STATE ---
            # After moving, save the current state to the persistent store
            # This makes the game "survive" menu calls and save/loads
            renpy.store.player_x = self.player.x
            renpy.store.player_y = self.player.y
            renpy.store.player_dirx = self.player.dirx
            renpy.store.player_diry = self.player.diry
            renpy.store.player_planex = self.player.planex
            renpy.store.player_planey = self.player.planey
            renpy.store.stein_player_health = self.player.health
            renpy.store.stein_current_weapon = self.player.current_weapon_name

            # Serialize and save the state of all living enemies
            current_enemies_data = []
            for enemy in self.enemies:
                enemy_tuple = (enemy.x, enemy.y, enemy.texture_index, enemy.destroyed_texture_index, enemy.health)
                current_enemies_data.append(enemy_tuple)
            renpy.store.stein_enemies = current_enemies_data
            
            renpy.store.stein_sprites = self.sprite_positions

            # --- 4. RENDER 3D SCENE ---
            # Create the canvas at the internal (potentially smaller) resolution for performance.
            canvas = pygame.Surface((self.internal_width, self.internal_height), pygame.SRCALPHA)
            canvas.blit(self.bg_surf_cached, (0, 0))
            
            zBuffer = [] # Holds the distance of the wall at each screen column, for sprite occlusion
            
            # --- 4a. WALL CASTING ---
            # Loop through every vertical column of the internal screen resolution.
            for x in range(self.internal_width):
                # Calculate ray position and direction for this column
                cameraX = float(2 * x / float(self.internal_width) - 1)
                rayDirX = self.player.dirx + self.player.planex * cameraX
                rayDirY = self.player.diry + self.player.planey * cameraX

                mapX = int(self.player.x)
                mapY = int(self.player.y)  
                
                # Length of ray from one x or y-side to next x or y-side
                if rayDirX == 0: rayDirX = 0.00001
                deltaDistX = math.sqrt(1 + (rayDirY * rayDirY) / (rayDirX * rayDirX))
                if rayDirY == 0: rayDirY = 0.00001
                deltaDistY = math.sqrt(1 + (rayDirX * rayDirX) / (rayDirY * rayDirY))
                
                # Calculate step and initial sideDist using a DDA (Digital Differential Analysis) algorithm
                if rayDirX < 0:
                    stepX = -1
                    sideDistX = (self.player.x - mapX) * deltaDistX
                else:
                    stepX = 1
                    sideDistX = (mapX + 1.0 - self.player.x) * deltaDistX
                if rayDirY < 0:
                    stepY = -1
                    sideDistY = (self.player.y - mapY) * deltaDistY
                else:
                    stepY = 1
                    sideDistY = (mapY + 1.0 - self.player.y) * deltaDistY
       
                # Perform DDA: step through the grid until a wall is hit
                hit = 0
                while hit == 0:
                    if sideDistX < sideDistY:
                        sideDistX += deltaDistX
                        mapX += stepX
                        side = 0 # Wall was hit on an X-side (vertical)
                    else:
                        sideDistY += deltaDistY
                        mapY += stepY
                        side = 1 # Wall was hit on a Y-side (horizontal)
                    if self.worldMap[mapX][mapY] > 0: 
                        hit = 1

                # Calculate distance to the wall (fisheye correction)
                if side == 0:
                    perpWallDist = abs((mapX - self.player.x + (1 - stepX) / 2) / rayDirX)
                else:
                    perpWallDist = abs((mapY - self.player.y + (1 - stepY) / 2) / rayDirY)
          
                if perpWallDist == 0: perpWallDist = 0.000001
                
                # Calculate height of line to draw on screen
                lineHeight = int(self.internal_height / perpWallDist)
                
                # FIX: Clamp lineHeight to a large but safe value.
                # When perpWallDist is near zero, lineHeight can become astronomically large,
                # crashing pygame.transform.scale with a "Size too large for scaling" error.
                if lineHeight > 30000: lineHeight = 30000
                
                if lineHeight > 0:
                    drawStart = -lineHeight / 2 + self.internal_height / 2
                    texNum = self.worldMap[mapX][mapY] - 1
                   
                    # Calculate value of wallX (where exactly the wall was hit)
                    if side == 1:
                        wallX = self.player.x + ((mapY - self.player.y + (1 - stepY) / 2) / rayDirY) * rayDirX
                    else:
                        wallX = self.player.y + ((mapX - self.player.x + (1 - stepX) / 2) / rayDirX) * rayDirY
                    wallX -= math.floor(wallX)
                   
                    # Get the corresponding column from the texture
                    texX = int(wallX * float(texWidth))
                    if side == 0 and rayDirX > 0: texX = texWidth - texX - 1
                    if side == 1 and rayDirY < 0: texX = texWidth - texX - 1
                    if side == 1: texNum += 8 # Use the darkened texture for Y-side walls
                    
                    # Get the 1-pixel-wide slice from the texture
                    source_surf = self.image_renders[texNum]
                    slice_area = (texX, 0, 1, texHeight)
                    
                    # Scale the slice to the calculated line height and draw it on the canvas
                    scaled_surf = pygame.transform.scale(source_surf.subsurface(slice_area), (1, lineHeight))
                    canvas.blit(scaled_surf, (x, int(drawStart)))

                zBuffer.append(perpWallDist)       

            # --- 4b. SPRITE CASTING ---
            renderable_enemies = [(e.x, e.y, e.texture_index) for e in self.enemies]
            renderable_projectiles = [(p.x, p.y, p.texture_index) for p in self.projectiles]
            mergedlist = self.sprite_positions + renderable_enemies + renderable_projectiles
            
            # Sort sprites from far to near to handle transparency correctly
            mergedlist.sort(key=self.sprite_sort_key, reverse=True)
            for sprite in mergedlist:
                # Translate sprite position to be relative to camera
                spriteX = sprite[0] - self.player.x
                spriteY = sprite[1] - self.player.y
              
                # Transform sprite with the inverse camera matrix
                invDet = 1.0 / (self.player.planex * self.player.diry - self.player.dirx * self.player.planey)
                transformX = invDet * (self.player.diry * spriteX - self.player.dirx * spriteY)
                transformY = invDet * (-self.player.planey * spriteX + self.player.planex * spriteY) # this is the depth inside the screen
                
                # Don't render sprites that are behind the camera plane
                if transformY <= 0.1: continue
                    
                # Calculate sprite's position and size on screen
                spritesurfaceX = (self.internal_width / 2.0) * (1.0 + transformX / transformY)
                f_spriteHeight = self.internal_height / transformY
                f_spriteWidth = f_spriteHeight * (texWidth / texHeight)
                
                i_spriteHeight = int(f_spriteHeight)
                i_spriteWidth = int(f_spriteWidth)

                if i_spriteHeight <= 0 or i_spriteWidth <= 0: continue
                
                # Calculate drawing boundaries on the screen
                f_drawStartY = self.internal_height / 2.0 - f_spriteHeight / 2.0
                f_drawStartX = spritesurfaceX - f_spriteWidth / 2.0
                i_drawStartX = int(f_drawStartX)
                i_drawEndX = int(f_drawStartX + f_spriteWidth)
                
                if i_drawEndX < 0 or i_drawStartX > self.internal_width: continue

                # Scale the full sprite texture to its on-screen size
                source_sprite_surf = self.sprite_renders[sprite[2]]
                scaled_sprite = pygame.transform.scale(source_sprite_surf, (i_spriteWidth, i_spriteHeight))

                # Loop through the vertical stripes of the sprite on screen
                for stripe in range(i_drawStartX, i_drawEndX):
                    # Check if stripe is on screen and in front of a wall
                    if 0 <= stripe < self.internal_width and transformY < zBuffer[stripe]:
                        source_x = stripe - i_drawStartX
                        if source_x < i_spriteWidth:
                            # Draw a 1-pixel wide slice of the scaled sprite
                            blit_area = (source_x, 0, 1, i_spriteHeight)
                            canvas.blit(scaled_sprite, (stripe, int(f_drawStartY)), area=blit_area)

            # --- 5. FINAL COMPOSITING AND DISPLAY ---
            # OPTIMIZATION: Scale the small internal canvas up to the full display size.
            final_canvas = pygame.transform.scale(canvas, (self.width, self.height))

            # Create the final Ren'Py render object
            final_render = renpy.Render(self.width, self.height)
            canvas_tex = renpy.display.draw.load_texture(final_canvas)
            final_render.blit(canvas_tex, (0, 0))
            
            # Render the currently equipped weapon model over the 3D scene
            current_weapon_obj = self.weapons[self.player.current_weapon_name]
            current_weapon_obj.render_to(final_render, self.width, self.height, st, at)

            # --- 6. RENDER HUD AND EFFECTS ---
            hp_text = Text("HP: {}".format(self.player.health), style="default", size=32)
            hp_render = renpy.render(hp_text, self.width, self.height, st, at)
            final_render.blit(hp_render, (15, self.height - 45))

            # Render damage flash
            if self.damage_flash_timer > 0:
                flash_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                alpha = 128 * (self.damage_flash_timer / 0.2)
                flash_surf.fill((255, 0, 0, alpha))
                final_render.blit(flash_surf, (0, 0))

            # Check for win condition (player is near an exit)
            for e in self.exits:
                if math.fabs(e[0] - self.player.x) < 0.5 and math.fabs(e[1] - self.player.y) < 0.5:
                    self.won = e[2]
            
            # Request a redraw for the next frame to create animation
            renpy.redraw(self, 0)
            return final_render
        
        def event(self, ev, x, y, st):
            """ The main event handler, called by Ren'Py for every input event. """
            global simulate_touch

            # On first event (or after returning from menu), hide mouse and grab cursor
            if not self.mouse_initialized and not simulate_touch:
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)
                self.mouse_initialized = True

            if simulate_touch:
                # On Android, fingers generate FINGER* events for true multitouch.
                if ev.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
                    self.handle_multitouch_events(ev)
                # For testing on PC, we simulate touch with mouse buttons.
                elif ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                    self.handle_mouse_simulation(ev, x, y)
            else:
                # Handle standard PC (keyboard + mouse) input.
                self.handle_pc_input(ev)

            if self.won is None:
                renpy.retain_after_load() # Prevents the game from advancing if an event is handled
            else:
                if self.mouse_initialized:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                return self.won # If an exit is reached, return the exit name to Ren'Py
        
        def update_enemies(self, dt):
            """
            Update the state and position of all enemies.
            """
            for enemy in self.enemies:
                enemy.update(dt, self.player)

        def update_projectiles(self, dt):
            """
            Update all active projectiles and remove ones that have hit something.
            """
            # We iterate over a copy of the list because we might modify it during the loop
            for p in list(self.projectiles):
                if not p.update(dt):
                    self.projectiles.remove(p)

        def handle_multitouch_events(self, ev):
            """ Handles true multitouch input from a touchscreen. """
            LOOK_THRESHOLD_X = 0.5  # The vertical line at 50% of the screen width
            finger_id = ev.finger_id
            
            # Convert normalized coordinates (0.0-1.0) to pixel coordinates
            event_x = ev.x * self.width
            event_y = ev.y * self.height

            if ev.type == pygame.FINGERDOWN:
                # Check if a move or look action is already being performed by another finger
                has_move = any(info.get('action') == 'move' for info in self.active_fingers.values())
                has_look = any(info.get('action') == 'look' for info in self.active_fingers.values())

                action = None
                # Left side of screen is for movement
                if ev.x <= LOOK_THRESHOLD_X and not has_move:
                    action = 'move'
                # Right side of screen is for looking
                elif ev.x > LOOK_THRESHOLD_X and not has_look:
                    action = 'look'

                # If the action is valid (not already taken), register the new finger
                if action:
                    self.active_fingers[finger_id] = {
                        'action': action,
                        'start_pos': (event_x, event_y),
                        'current_pos': (event_x, event_y),
                        'dx_accum': 0.0,
                    }

            elif ev.type == pygame.FINGERMOTION:
                if finger_id in self.active_fingers:
                    info = self.active_fingers[finger_id]
                    
                    # Enforce strict quadrants: if a finger strays into the other zone, deactivate it.
                    in_move_zone = ev.x <= LOOK_THRESHOLD_X
                    in_look_zone = ev.x > LOOK_THRESHOLD_X

                    finger_strayed = (info['action'] == 'move' and not in_move_zone) or \
                                     (info['action'] == 'look' and not in_look_zone)

                    if finger_strayed:
                        del self.active_fingers[finger_id]
                    else:
                        # If the finger is in its correct zone, update its state
                        if info['action'] == 'move':
                            info['current_pos'] = (event_x, event_y)
                        elif info['action'] == 'look':
                            info['dx_accum'] += ev.dx * self.width

            elif ev.type == pygame.FINGERUP:
                # Remove the finger from the active list when it's lifted
                if finger_id in self.active_fingers:
                    del self.active_fingers[finger_id]

        def handle_mouse_simulation(self, ev, x, y):
            """ Simulates the two-zone touch controls using a PC mouse. """
            button_id = getattr(ev, 'button', None)
            LOOK_THRESHOLD_PIXELS = self.width * 0.5

            if ev.type == pygame.MOUSEBUTTONDOWN:
                action = None
                # Assign action based on which button is pressed in which quadrant
                if button_id == 1 and x > LOOK_THRESHOLD_PIXELS: action = 'look'   # Left-click on right side
                elif button_id == 3 and x <= LOOK_THRESHOLD_PIXELS: action = 'move'  # Right-click on left side
                elif button_id == 2:                  # Middle-click anywhere
                    self.shoot_weapon()
                    return

                if action and button_id not in self.active_fingers:
                    self.active_fingers[button_id] = {
                        'action': action,
                        'start_pos': (x, y),
                        'current_pos': (x, y),
                        'dx_accum': 0.0
                    }

            elif ev.type == pygame.MOUSEMOTION:
                buttons_pressed = ev.buttons # (left, middle, right)
                
                # If left mouse button is held down for looking
                if buttons_pressed[0] and 1 in self.active_fingers and self.active_fingers[1]['action'] == 'look':
                    self.active_fingers[1]['dx_accum'] += ev.rel[0]
                
                # If right mouse button is held down for movement
                if buttons_pressed[2] and 3 in self.active_fingers and self.active_fingers[3]['action'] == 'move':
                    self.active_fingers[3]['current_pos'] = (x, y)

            elif ev.type == pygame.MOUSEBUTTONUP:
                if button_id in self.active_fingers:
                    del self.active_fingers[button_id]

        def update_player_from_touch_state(self):
            """
            Converts the abstract state of `active_fingers` into concrete player movement values
            (speed, direction) for the current frame.
            """
            self.player.speed = 0
            self.player.strafe_speed = 0
            self.player.dir = 0
            
            for finger_id, info in list(self.active_fingers.items()):
                if info['action'] == 'move':
                    # Calculate vector from start to current pos to create a virtual joystick
                    start_x, start_y = info['start_pos']
                    current_x, current_y = info['current_pos']
                    dx, dy = current_x - start_x, current_y - start_y
                    
                    distance = math.sqrt(dx*dx + dy*dy)
                    max_dist = 80.0 
                    dead_zone = 10.0
                    
                    if distance > dead_zone:
                        # Clamp the joystick to a maximum radius
                        if distance > max_dist:
                            dx = (dx / distance) * max_dist
                            dy = (dy / distance) * max_dist
                        
                        # Map joystick vector to player speed and strafe
                        self.player.speed += -dy / max_dist
                        self.player.strafe_speed += dx / max_dist

                elif info['action'] == 'look':
                    # Convert accumulated horizontal movement into rotation
                    self.player.dir += (info['dx_accum'] / self.width) * 25.0
                    info['dx_accum'] = 0.0 # Reset accumulator for the next frame

        def handle_pc_input(self, ev):
            """ Handles traditional PC input (WASD + Mouse). """
            # Handle mouse look
            if ev.type == pygame.MOUSEMOTION:
                sensitivity = 0.003
                self.player.rot -= ev.rel[0] * sensitivity
                self.player.planerot -= ev.rel[0] * sensitivity

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    self.mouse_initialized = False
                    return # Let Ren'Py handle the rest...

                if ev.key == pygame.K_1: self.player.current_weapon_name = "fist"
                if ev.key == pygame.K_2: self.player.current_weapon_name = "gun"

                # WASD controls
                if ev.key == pygame.K_w: self.player.speed = 1
                if ev.key == pygame.K_s: self.player.speed = -1
                if ev.key == pygame.K_a: self.player.strafe_speed = -1 # Strafe left
                if ev.key == pygame.K_d: self.player.strafe_speed = 1 # Strafe right
                # Arrow key controls (legacy)
                if ev.key == pygame.K_UP: self.player.speed = 1
                if ev.key == pygame.K_DOWN: self.player.speed = -1
                if ev.key == pygame.K_LEFT: self.player.dir = 1
                if ev.key == pygame.K_RIGHT: self.player.dir = -1
                # Actions
                if ev.key == pygame.K_SPACE:
                    self.shoot_weapon()

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1: # Left mouse button
                    self.shoot_weapon()
                        
            if ev.type == pygame.KEYUP: 
                if ev.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN): 
                    self.player.speed = 0
                if ev.key in (pygame.K_a, pygame.K_d): 
                    self.player.strafe_speed = 0
                if ev.key in (pygame.K_LEFT, pygame.K_RIGHT): 
                    self.player.dir = 0
        
        def sprite_sort_key(self, s):
            """ Used to sort sprites by distance from the player, for rendering. """
            return (s[0] - self.player.x) ** 2 + (s[1] - self.player.y) ** 2
        
        def shoot_weapon(self):
            """ 
            Handles the shooting logic based on the currently equipped weapon.
            """
            weapon = self.weapons[self.player.current_weapon_name]
            
            if weapon.playing:
                return

            weapon.play()

            if weapon.projectile_type is None: # Melee attack (fist)
                renpy.sound.play("sounds/pew.ogg", channel=1) # TODO: Replace with a punch sound
                # Sort enemies to hit the closest one first
                self.enemies.sort(key=lambda e: (e.x - self.player.x)**2 + (e.y - self.player.y)**2)
                for e in self.enemies:
                    # Check if enemy is within a 2-unit range
                    if math.sqrt((e.x - self.player.x)**2 + (e.y - self.player.y)**2) < 2.0:
                        e.health -= weapon.damage
                        if e.health <= 0:
                            renpy.sound.play("sounds/ow.ogg", channel=1)
                            self.enemies.remove(e)
                            self.sprite_positions.append((e.x, e.y, e.destroyed_texture_index))
                        break # Only hit one enemy

            elif weapon.projectile_type == 'bullet': # Pistol (gun)
                renpy.sound.play("sounds/pew.ogg", channel=1) # TODO: Replace with real a gunshot sound XD
                # Create a projectile that moves in the players direction
                bullet = Projectile(
                    wm=self,
                    x=self.player.x,
                    y=self.player.y,
                    dir_x=self.player.dirx,
                    dir_y=self.player.diry,
                    texture_index=self.bullet_texture_index,
                    damage=weapon.damage,
                    fired_by_player=True
                )
                self.projectiles.append(bullet)
