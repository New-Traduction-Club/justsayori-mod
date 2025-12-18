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
        pygame.JOYAXISMOTION,
        pygame.JOYBUTTONDOWN,
        pygame.JOYBUTTONUP,
        pygame.JOYHATMOTION,
        pygame.JOYDEVICEADDED,
        pygame.JOYDEVICEREMOVED
    ])

    # Global flag to switch between keyboard and touch/mouse controls.
    # This is controlled by the in-game UI.
    # Automatically enable touch controls on Android.
    if renpy.android:
        simulate_touch = True
    else:
        simulate_touch = False

    # --- Audio Channel Registration ---
    renpy.music.register_channel("gun_sfx", mixer="sfx", loop=False)
    renpy.music.register_channel("shotgun_sfx", mixer="sfx", loop=False)
    renpy.music.register_channel("enemy_sfx", mixer="sfx", loop=False)

    # --- Constants ---
    texWidth = 64   # Texture width in pixels
    texHeight = 64  # Texture height in pixels
    twoPI = math.pi * 2

    class DamageIndicator(object):
        """
        Visual indicator for where damage came from.
        """
        def __init__(self, angle, duration=2.0):
            self.angle = angle
            self.duration = duration
            self.max_duration = duration

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
            self.pitch = 0.0 # Vertical look offset (Y-Shearing)
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
        def __init__(self, wm, x, y, dir_x, dir_y, texture_index, damage, fired_by_player=False, is_invisible=False, pitch=0.0):
            self.wm = wm
            self.x = x
            self.y = y
            self.dir_x = dir_x
            self.dir_y = dir_y
            self.texture_index = texture_index
            self.damage = damage
            self.fired_by_player = fired_by_player
            self.is_invisible = is_invisible
            self.pitch = pitch
            self.speed = 20.0

        def update(self, dt):
            """
            Moves the projectile and checks for collisions.
            Returns:
                bool: False if the projectile should be destroyed, True otherwise.
            """
            new_x = self.x + self.dir_x * self.speed * dt
            new_y = self.y + self.dir_y * self.speed * dt

            # Check boundary limits first to avoid IndexError
            map_w = len(self.wm.worldMap)
            map_h = len(self.wm.worldMap[0])
            
            if not (0 <= int(new_x) < map_w and 0 <= int(new_y) < map_h):
                return False # Out of map bounds, destroy

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
                    
                    self.wm.add_damage_indicator(-self.dir_x, -self.dir_y)

                    self.wm.damage_flash_timer = 0.2
                    renpy.sound.play("sounds/ow.ogg", channel="audio")
                    return False # Hit the player, destroy projectile
            else:
                # Projectile from player, check against enemies
                for enemy in self.wm.enemies:
                    dist_to_enemy = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                    if dist_to_enemy < 0.5: # Enemy hitbox
                        
                        # --- 3D vertical hitbox logic (Y-Shearing) ---
                        # Check if the shot height aligns with the enemy
                        if hasattr(self, 'pitch'):
                            safe_dist = max(0.1, dist_to_enemy)
                            # Calculate projected visual height of enemy at this distance
                            # Height = ScreenHeight / Distance
                            enemy_vis_height = self.wm.internal_height / safe_dist
                            
                            calc_height = min(enemy_vis_height, self.wm.internal_height * 1.2)
                            
                            # This fits the visible sprite better, ignoring potential transparent space at the top, but not perfect
                            hit_threshold = (calc_height / 2.0) * 0.2
                            
                            if abs(self.pitch) > hit_threshold:
                                continue 
                        
                        # Handle Damage (Check for dodge)
                        taken = True
                        if hasattr(enemy, 'take_damage'):
                            taken = enemy.take_damage(self.damage)
                        else:
                            enemy.health -= self.damage
                        
                        if taken:
                            if enemy.health <= 0:
                                renpy.sound.play("sounds/ow.ogg", channel="audio")
                                if self.wm.is_arena_mode:
                                    persistent.stein_kills += 1
                                self.wm.enemies.remove(enemy)
                                self.wm.sprite_positions.append((enemy.x, enemy.y, enemy.destroyed_texture_index))
                                # 40% chance to drop a medkit
                                if renpy.random.random() < 0.40:
                                    self.wm.sprite_positions.append((enemy.x, enemy.y, 7))
                                
                                # Arena Mode: Drop coins
                                if self.wm.is_arena_mode:
                                    drop_prob = 1.0 if enemy.coin_index == 12 else 0.35
                                    if renpy.random.random() < drop_prob:
                                        self.wm.sprite_positions.append((enemy.x, enemy.y, enemy.coin_index))
                                    
                                    # Arena Mode: Drop Shotgun (10% normal, 25% boss) if not owned
                                    if not renpy.store.stein_has_shotgun:
                                        shotgun_prob = 0.25 if enemy.coin_index == 12 else 0.10
                                        if renpy.random.random() < shotgun_prob:
                                            self.wm.sprite_positions.append((enemy.x, enemy.y, 13))
                                            
                                    # Arena Mode: Drop Minigun (10% Chance) if not owned
                                    if not renpy.store.stein_has_minigun:
                                        if renpy.random.random() < 0.10:
                                            self.wm.sprite_positions.append((enemy.x, enemy.y, 15))

                            self.wm.hit_marker_timer = 0.15

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
            
            # Memory of player position
            self.last_known_x = None
            self.last_known_y = None
            
            # These will be overridden by subclasses
            self.texture_index = 0
            self.destroyed_texture_index = 0
            self.moveSpeed = 1.5 
            self.rotSpeed = 75 * math.pi / 180
            self.attack_range = 8.0
            self.sight_range = 15.0
            
            if self.wm.is_arena_mode:
                self.attack_range = 24.0
                self.sight_range = 30.0
            self.attack_cooldown = 1.5
            self.damage = 10
            self.coin_index = 11
            
            self.attack_timer = 1.0
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
            has_los = self.has_line_of_sight(player_x, player_y)

            if has_los:
                self.last_known_x = player_x
                self.last_known_y = player_y

            # State transitions
            if self.state == 'idle':
                if dist_to_player < self.sight_range and has_los:
                    self.state = 'chasing'
            
            elif self.state == 'chasing':
                target_x = player_x
                target_y = player_y
                
                # If we lost LOS, pursue last known position
                if not has_los:
                    if self.last_known_x is not None:
                        target_x = self.last_known_x
                        target_y = self.last_known_y
                        
                        # Check if we reached the last known pos
                        dist_to_last = math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2)
                        if dist_to_last < 1.0:
                            # Reached last known spot and player not seen -> Give up
                            self.state = 'idle'
                            self.last_known_x = None
                            return
                    else:
                        # No memory and no sight -> Idle
                        self.state = 'idle'
                        return

                # Move logic
                # If we have LOS, we maintain distance for attacking
                # If we don't have LOS (hunting), we move directly to the target
                
                should_move = True
                
                if has_los:
                    # In attack range?
                    if dist_to_player < self.attack_range:
                        # Too close? Backup slightly? Or just stop.
                        if dist_to_player < self.attack_range * 0.5:
                            # Maybe back away? For now just stop.
                            should_move = False
                        
                        # Attack if cooldown ready
                        if self.attack_timer == 0:
                            self.attack(player)
                    else:
                        should_move = True
                else:
                    # Hunting mode: always move towards last known pos
                    should_move = True

                if should_move:
                    self.move(dt, target_x, target_y)

        def attack(self, player):
            """
            Placeholder for the attack action. To be overridden by subclasses.
            """
            self.attack_timer = self.attack_cooldown
            # Base enemy does nothing XD
            pass

        def check_wall_collision(self, x, y, radius=0.3):
            """
            Checks if a circle at (x,y) with given radius intersects any wall.
            """
            # Check center
            if self.isBlocking(x, y): return True
            
            # Check cardinal points on rim
            if self.isBlocking(x + radius, y): return True
            if self.isBlocking(x - radius, y): return True
            if self.isBlocking(x, y + radius): return True
            if self.isBlocking(x, y - radius): return True
            
            return False

        def move(self, dt, target_x, target_y):
            """
            Moves the enemy towards a target position with advanced obstacle avoidance.
            """
            # 1. Calculate ideal direction
            dx = target_x - self.x
            dy = target_y - self.y
            angle = math.atan2(dy, dx)
            
            # 2. Obstacle Avoidance ("Whiskers")
            # Look ahead further to react sooner
            look_dist = 1.2
            radius = 0.35
            
            # Check front
            ahead_x = self.x + math.cos(angle) * look_dist
            ahead_y = self.y + math.sin(angle) * look_dist
            
            if self.check_wall_collision(ahead_x, ahead_y, radius):
                # Front blocked. Scan for openings.
                # Check diagonals (+/- 45) and sides (+/- 90)
                offsets = [-0.785, 0.785, -1.57, 1.57] # -45, +45, -90, +90
                best_angle = angle
                found_path = False
                
                for off in offsets:
                    test_angle = angle + off
                    tx = self.x + math.cos(test_angle) * look_dist
                    ty = self.y + math.sin(test_angle) * look_dist
                    
                    if not self.check_wall_collision(tx, ty, radius):
                        angle = test_angle
                        found_path = True
                        break # Take first open path
                
                # If still blocked, maybe turn around? or just wiggle
                if not found_path:
                    angle += 2.0 # Turn significantly

            # 3. Movement with Sliding (Radius Aware)
            moveStep = self.moveSpeed * dt
            vx = math.cos(angle) * moveStep
            vy = math.sin(angle) * moveStep
            
            # Try moving X
            # We add a small buffer to the check to prevent getting EXACTLY on the wall
            if not self.check_wall_collision(self.x + vx, self.y, radius):
                self.x += vx
            
            # Try moving Y
            if not self.check_wall_collision(self.x, self.y + vy, radius):
                self.y += vy

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
            renpy.sound.play("sounds/e-gunshot.ogg", channel="audio")

    class Yuritler(Guard):
        """
        The Boss Enemy: Yuritler.
        Spawns every 10 rounds in Arena Mode with scaling HP.
        """
        def __init__(self, wm, x, y, health=150):
            super(Yuritler, self).__init__(wm, x, y, 9, 10, health)
            self.damage = 5
            self.moveSpeed = 1.8 
            self.attack_cooldown = 1.0
            self.coin_index = 12

        def attack(self, player):
            """
            Yuritler's attack: fires 4 spread projectiles at the player.
            """
            self.attack_timer = self.attack_cooldown
            
            dir_x = player.x - self.x
            dir_y = player.y - self.y
            dist = math.sqrt(dir_x**2 + dir_y**2)
            
            if dist > 0:
                base_angle = math.atan2(dir_y, dir_x)
                
                num_pellets = 4
                spread_angle = 0.2
                
                for i in range(num_pellets):
                    offset = (i / float(num_pellets - 1) - 0.5) * spread_angle
                    final_angle = base_angle + offset
                    
                    p_dirx = math.cos(final_angle)
                    p_diry = math.sin(final_angle)
                    
                    bullet = Projectile(
                        wm=self.wm, 
                        x=self.x, 
                        y=self.y, 
                        dir_x=p_dirx, 
                        dir_y=p_diry, 
                        texture_index=self.bullet_texture_index, 
                        damage=self.damage,
                        fired_by_player=False
                    )
                    self.wm.projectiles.append(bullet)
            
            renpy.sound.play("sounds/e-gunshot.ogg", channel="audio")

    class EliteGuard(Guard):
        """
        An upgraded guard with a machine gun.
        Fires a 10-round burst rapidly, then reloads for 5 seconds.
        """
        def __init__(self, wm, x, y, health=100):
            super(EliteGuard, self).__init__(wm, x, y, 4, 5, health)
            self.damage = 3
            self.attack_cooldown = 0.1
            
            self.burst_limit = 10
            self.shots_fired_in_burst = 0
            self.is_reloading = False
            self.reload_time = 5.0
            self.reload_timer = 0.0

        def update(self, dt, player):
            if self.is_reloading:
                self.reload_timer -= dt
                if self.reload_timer <= 0:
                    self.is_reloading = False
                    self.shots_fired_in_burst = 0
                    self.attack_timer = 0.5 # Reload time
                
                # While reloading, behave like a normal enemy (move/chase) but don't attack
                # We call BaseEnemy.update but intercept the attack call logic effectively
                # by ensuring attack() checks is_reloading
            
            super(EliteGuard, self).update(dt, player)

        def attack(self, player):
            if self.is_reloading:
                return

            self.attack_timer = self.attack_cooldown
            
            dir_x = player.x - self.x
            dir_y = player.y - self.y
            dist = math.sqrt(dir_x**2 + dir_y**2)
            if dist > 0:
                dir_x /= dist
                dir_y /= dist

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
            
            renpy.sound.play("sounds/e-gunshot.ogg", channel="audio")

            self.shots_fired_in_burst += 1
            if self.shots_fired_in_burst >= self.burst_limit:
                self.is_reloading = True
                self.reload_timer = self.reload_time

    class Sniper(Guard):
        """
        Fast, high damage enemy that can dodge bullets XD.
        """
        def __init__(self, wm, x, y, health=100):
            super(Sniper, self).__init__(wm, x, y, 4, 5, health)
            self.damage = 20
            self.attack_cooldown = 1.5
            self.moveSpeed = 3.0
            self.bullet_texture_index = 14
            
            self.dodge_cooldown = 4.0
            self.dodge_timer = 0.0
            self.is_dodging = False

        def update(self, dt, player):
            self.dodge_timer = max(0, self.dodge_timer - dt)
            super(Sniper, self).update(dt, player)

        def take_damage(self, amount):
            """
            Custom damage handler to implement 100% dodge chance.
            Returns True if damage was taken, False if dodged.
            """
            if self.dodge_timer <= 0:
                self.dodge_timer = self.dodge_cooldown
                
                player = self.wm.player
                dx = player.x - self.x
                dy = player.y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > 0:
                    ndx = dx / dist
                    ndy = dy / dist
                    
                    strafe_x = -ndy
                    strafe_y = ndx
                    
                    dodge_distance = 1.5
                    
                    target_x = self.x + strafe_x * dodge_distance
                    target_y = self.y + strafe_y * dodge_distance
                    
                    if not self.check_wall_collision(target_x, target_y, 0.35):
                        self.x = target_x
                        self.y = target_y
                    else:
                        target_x = self.x - strafe_x * dodge_distance
                        target_y = self.y - strafe_y * dodge_distance
                        if not self.check_wall_collision(target_x, target_y, 0.35):
                            self.x = target_x
                            self.y = target_y
                
                # renpy.sound.play("", channel="audio") # TODO: add a sound
                return False
            
            self.health -= amount
            return True

        def attack(self, player):
            self.attack_timer = self.attack_cooldown
            
            dir_x = player.x - self.x
            dir_y = player.y - self.y
            dist = math.sqrt(dir_x**2 + dir_y**2)
            if dist > 0:
                dir_x /= dist
                dir_y /= dist

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
            
            renpy.sound.play("sounds/e-gunshot.ogg", channel="audio")

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
            self.sight_d = Image("pics/items/sight.png")

            with renpy.open_file("pics/gui/arrow_d.png") as f:
                arrow_surf = pygame.image.load(f).convert_alpha()
            self.arrow_img = pygame.transform.scale(arrow_surf, (30, 30))
            self.damage_indicators = []

            with renpy.open_file("pics/gui/damage_x.png") as f:
                self.hit_marker_img = pygame.image.load(f).convert_alpha()
            self.hit_marker_timer = 0.0

            # Asset paths
            self.sprite_paths = [  
                "pics/items/barrel.png", "pics/items/pillar.png",
                "pics/items/greenlight.png", "pics/items/pillar_destroyed.png",
                "pics/enemies/guard.png",
                "pics/enemies/guard_d.png",
                "pics/items/bullet.png",
                "pics/items/medkit.png",
                "pics/items/cookie.png",
                "pics/enemies/yuritler.png",
                "pics/enemies/yuritler_d.png",
                "pics/items/coins.png",
                "pics/items/coins.png", # Boss Coin
                "pics/items/random_gun_i.png",
                "pics/items/bullet_red.png",
                "pics/items/minigun.png",
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
            
            # --- Arena Mode State ---
            self.is_arena_mode = renpy.store.is_arena_mode
            self.current_round = renpy.store.stein_current_round
            self.inter_round_timer = renpy.store.stein_inter_round_timer
            self.sniper_count = renpy.store.stein_sniper_count
            self.yuritler_count = renpy.store.stein_yuritler_count
            self.spawn_points = renpy.store.arena_spawn_points
            
            self.enemies = []
            
            if self.is_arena_mode:
                if self.current_round == 0:
                    self.start_next_round()
                self.exits = []

            for e_data in renpy.store.stein_enemies:
                # e_data format: (x, y, tex, dead_tex, health, type_id)
                # Legacy support: (x, y, tex, dead_tex, health) -> Guard
                # Legacy support: (x, y, tex, dead_tex) -> Guard
                
                x, y, tex, dead_tex = e_data[0], e_data[1], e_data[2], e_data[3]
                health = e_data[4] if len(e_data) > 4 else 100
                type_id = e_data[5] if len(e_data) > 5 else 0
                
                if type_id == 1:
                    new_e = Yuritler(self, x, y, health=health)
                elif type_id == 2:
                    new_e = EliteGuard(self, x, y, health=health)
                elif type_id == 3:
                    new_e = Sniper(self, x, y, health=health)
                else:
                    new_e = Guard(self, x, y, tex, dead_tex, health=health)
                
                self.enemies.append(new_e)

            self.projectiles = []
            
            # Weapon Logic & Upgrades
            gun_dmg = 50
            shotgun_dmg = 35
            minigun_dmg = 40
            
            # Apply Upgrades only in Arena Mode
            if self.is_arena_mode:
                gun_dmg += 50 * (persistent.stein_pistol_level * 0.01)
                shotgun_dmg += 35 * (persistent.stein_shotgun_level * 0.01)
                minigun_dmg += 3 * (persistent.stein_minigun_level * 0.10)

            self.weapons = {
                "fist": Weapon("fist", 5, 1, damage=100, projectile_type=None, cooldown=0.5),
                "gun": Weapon("gun", 5, 1, damage=gun_dmg, projectile_type='bullet', cooldown=0.6, ads_idle="pics/weapons/gun_s.png", ads_fire="pics/weapons/gun_s_f.png"),
                "shotgun": Weapon("shotgun", 5, 1, damage=shotgun_dmg, projectile_type='shotgun', cooldown=1.0),
                "minigun": Weapon("minigun", 5, 1, damage=minigun_dmg, projectile_type='bullet', cooldown=0.05, loop_frames=[2, 3])
            }
            for w_name in self.weapons:
                self.weapons[w_name].last_fired = -100.0

            self.bullet_texture_index = 6 

            self.won = None
            self.damage_flash_timer = 0.0
            self.heal_flash_timer = 0.0
            self.mouse_initialized = False
            self.is_aiming = False

            # --- Input States ---
            # We separate input sources to support simultaneous usage (e.g. Touch + Gamepad)
            self.kb_speed = 0.0
            self.kb_strafe = 0.0
            self.kb_dir = 0.0
            
            self.gp_speed = 0.0
            self.gp_strafe = 0.0
            self.gp_dir = 0.0
            
            self.touch_speed = 0.0
            self.touch_strafe = 0.0
            self.touch_dir = 0.0
            
            self.gp_aiming = False
            self.mouse_firing = False
            self.gp_firing = False
            self.prev_btn_weapon_switch = False
            
            self.kb_running = False
            self.gp_running = False

            # --- Input: Joystick Initialization ---
            pygame.joystick.init()
            self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            for joy in self.joysticks:
                joy.init()
            
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
                # Update timers (damage_flash_timer, heal_flash_timer, hit_marker_timer)
                self.damage_flash_timer = max(0, self.damage_flash_timer - dtime)
                self.heal_flash_timer = max(0, self.heal_flash_timer - dtime)
                self.hit_marker_timer = max(0, self.hit_marker_timer - dtime)

                # --- Input Aggregation ---
                if simulate_touch:
                    self.update_player_from_touch_state()
                else:
                    self.touch_speed = 0.0
                    self.touch_strafe = 0.0
                    self.touch_dir = 0.0

                self.poll_gamepad()

                # This allows the Gamepad (Auxiliary System) to work alongside Keyboard or Touch
                total_speed = self.kb_speed + self.gp_speed + self.touch_speed
                total_strafe = self.kb_strafe + self.gp_strafe + self.touch_strafe
                total_dir = self.kb_dir + self.gp_dir + self.touch_dir
                
                effective_aiming = self.is_aiming or self.gp_aiming
                is_running = self.kb_running or self.gp_running
                
                if effective_aiming:
                    is_running = False
                
                if is_running:
                    self.player.moveSpeed = 4.0 # Sprint speed
                elif effective_aiming:
                    self.player.moveSpeed = 1.5 # Aiming walk speed
                else:
                    self.player.moveSpeed = 2.5 # Normal walk speed

                # Clamp values to avoid super-speed when using multiple inputs
                self.player.speed = max(-1.0, min(1.0, total_speed))
                self.player.strafe_speed = max(-1.0, min(1.0, total_strafe))
                self.player.dir = total_dir # Rotation usually doesn't need clamping, just accumulation

                # Move the player
                self.player.move(dtime)
                
                # Check for item pickups
                self.check_item_pickup()
                
                # Update enemies
                self.update_enemies(dtime)

                # Update projectiles
                self.update_projectiles(dtime)

                if self.is_arena_mode and self.inter_round_timer > 0:
                    self.inter_round_timer -= dtime
                    if self.inter_round_timer <= 0:
                        self.start_next_round()
                
                if self.is_arena_mode and len(self.enemies) == 0 and self.inter_round_timer <= 0 and self.current_round > 0:
                    self.inter_round_timer = 10.0

                if self.player.health <= 0:
                    self.player.health = 0
                    if self.is_arena_mode:
                        renpy.store.last_arena_round = self.current_round
                        renpy.store.new_highscore = False
                        if self.current_round > persistent.sayoristein_arena_highscore:
                            persistent.sayoristein_arena_highscore = self.current_round
                            renpy.store.new_highscore = True
                        self.won = 'game_over_arena'
                    else:
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
                if isinstance(enemy, Yuritler): type_id = 1
                elif isinstance(enemy, EliteGuard): type_id = 2
                elif isinstance(enemy, Sniper): type_id = 3
                else: type_id = 0
                
                enemy_tuple = (enemy.x, enemy.y, enemy.texture_index, enemy.destroyed_texture_index, enemy.health, type_id)
                current_enemies_data.append(enemy_tuple)
            renpy.store.stein_enemies = current_enemies_data
            
            renpy.store.stein_sprites = self.sprite_positions
            renpy.store.stein_current_round = self.current_round
            renpy.store.stein_inter_round_timer = self.inter_round_timer
            renpy.store.stein_sniper_count = self.sniper_count
            renpy.store.stein_yuritler_count = self.yuritler_count

            # --- 4. RENDER 3D SCENE ---
            
            # --- ADS / Zoom Logic ---
            effective_aiming = self.is_aiming or self.gp_aiming
            zoom_factor = 0.6 if effective_aiming else 1.0
            vertical_scale = 1.0 / zoom_factor
            
            # We use local plane variables for rendering to apply zoom without affecting physics
            render_planex = self.player.planex * zoom_factor
            render_planey = self.player.planey * zoom_factor

            p_dirx = self.player.dirx
            p_diry = self.player.diry
            p_x = self.player.x
            p_y = self.player.y
            world_map = self.worldMap
            i_width = self.internal_width

            is_moving = abs(self.player.speed) > 0.1 or abs(self.player.strafe_speed) > 0.1
            is_running_state = (self.kb_running or self.gp_running) and is_moving
            
            bob_offset = 0.0
            if is_moving and not effective_aiming:
                bob_speed = 10.0
                bob_amp = 1.0
                if is_running_state:
                    bob_speed = 15.0
                    bob_amp = 2.5
                
                # Calculate vertical offset using sine wave based on time
                bob_offset = math.sin(st * bob_speed) * bob_amp

            horizon_offset = self.player.pitch + bob_offset
            i_horizon_offset = int(horizon_offset)

            # Create the canvas at the internal (maybe smaller) resolution for performance
            canvas = pygame.Surface((self.internal_width, self.internal_height), pygame.SRCALPHA)
            
            # Draw background shifted by horizon offset
            canvas.blit(self.bg_surf_cached, (0, i_horizon_offset))
            
            # Fill gaps caused by shifting to prevent artifacts
            if i_horizon_offset > 0:
                # Horizon moved down (looking up) -> gap at top
                # Fill with sky solor (top-left pixel of bg)
                sky_color = self.bg_surf_cached.get_at((0,0))
                canvas.fill(sky_color, (0, 0, i_width, i_horizon_offset))
            elif i_horizon_offset < 0:
                # Horizon moved up (looking down) -> gap at bottom
                # Fill with floor color (bottom-left pixel of bg)
                floor_color = self.bg_surf_cached.get_at((0, self.internal_height - 1))
                # Fill rect: x=0, y=height+offset (offset is negative), w=width, h=-offset
                canvas.fill(floor_color, (0, self.internal_height + i_horizon_offset, i_width, -i_horizon_offset))
            
            # --- 4a. WALL CASTING ---
            zBuffer = [0.0] * i_width

            # Loop through every vertical column of the internal screen resolution.
            for x in range(i_width):
                # Calculate ray position and direction for this column
                cameraX = float(2 * x / float(i_width) - 1)
                rayDirX = p_dirx + render_planex * cameraX
                rayDirY = p_diry + render_planey * cameraX

                mapX = int(p_x)
                mapY = int(p_y)  
                
                # Length of ray from one x or y-side to next x or y-side
                if rayDirX == 0: rayDirX = 0.00001
                deltaDistX = math.sqrt(1 + (rayDirY * rayDirY) / (rayDirX * rayDirX))
                if rayDirY == 0: rayDirY = 0.00001
                deltaDistY = math.sqrt(1 + (rayDirX * rayDirX) / (rayDirY * rayDirY))
                
                # Calculate step and initial sideDist using a DDA (Digital Differential Analysis) algorithm
                if rayDirX < 0:
                    stepX = -1
                    sideDistX = (p_x - mapX) * deltaDistX
                else:
                    stepX = 1
                    sideDistX = (mapX + 1.0 - p_x) * deltaDistX
                if rayDirY < 0:
                    stepY = -1
                    sideDistY = (p_y - mapY) * deltaDistY
                else:
                    stepY = 1
                    sideDistY = (mapY + 1.0 - p_y) * deltaDistY
       
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
                    if world_map[mapX][mapY] > 0: 
                        hit = 1

                # Calculate distance to the wall (fisheye correction)
                if side == 0:
                    perpWallDist = abs((mapX - p_x + (1 - stepX) / 2) / rayDirX)
                else:
                    perpWallDist = abs((mapY - p_y + (1 - stepY) / 2) / rayDirY)
          
                if perpWallDist == 0: perpWallDist = 0.000001
                
                # Calculate height of line to draw on screen
                # Scale height to match horizontal zoom (Maintain Aspect Ratio)
                lineHeight = int((self.internal_height / perpWallDist) * vertical_scale)
                
                # FIX: Clamp lineHeight to a large but safe value.
                # When perpWallDist is near zero, lineHeight can become astronomically large,
                # crashing pygame.transform.scale with a "Size too large for scaling" error.
                if lineHeight > 30000: lineHeight = 30000
                
                if lineHeight > 0:
                    # Apply horizon offset
                    drawStart = -lineHeight / 2 + self.internal_height / 2 + horizon_offset
                    texNum = world_map[mapX][mapY] - 1
                   
                    # Calculate value of wallX (where exactly the wall was hit)
                    if side == 1:
                        wallX = p_x + ((mapY - p_y + (1 - stepY) / 2) / rayDirY) * rayDirX
                    else:
                        wallX = p_y + ((mapX - p_x + (1 - stepX) / 2) / rayDirX) * rayDirY
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

                zBuffer[x] = perpWallDist       

            # --- 4b. SPRITE CASTING ---
            renderable_enemies = [(e.x, e.y, e.texture_index) for e in self.enemies]
            renderable_projectiles = [(p.x, p.y, p.texture_index, p.pitch) for p in self.projectiles if not getattr(p, 'is_invisible', False)]
            mergedlist = self.sprite_positions + renderable_enemies + renderable_projectiles
            
            # Sort sprites from far to near to handle transparency correctly
            mergedlist.sort(key=self.sprite_sort_key, reverse=True)
            for sprite in mergedlist:
                # Translate sprite position to be relative to camera
                spriteX = sprite[0] - p_x
                spriteY = sprite[1] - p_y
              
                # Transform sprite with the inverse camera matrix (Using Zoomed Plane)
                invDet = 1.0 / (render_planex * p_diry - p_dirx * render_planey)
                transformX = invDet * (p_diry * spriteX - p_dirx * spriteY)
                transformY = invDet * (-render_planey * spriteX + render_planex * spriteY) # this is the depth inside the screen
                
                # Don't render sprites that are behind the camera plane
                if transformY <= 0.1: continue
                    
                # Calculate sprite's position and size on screen
                spritesurfaceX = (i_width / 2.0) * (1.0 + transformX / transformY)
                
                # Scale sprite height to match wall scaling
                f_spriteHeight = (self.internal_height / transformY) * vertical_scale
                f_spriteWidth = f_spriteHeight * (texWidth / texHeight)
                
                i_spriteHeight = int(f_spriteHeight)
                i_spriteWidth = int(f_spriteWidth)

                if i_spriteHeight <= 0 or i_spriteWidth <= 0: continue
                
                # Calculate drawing boundaries on the screen
                # Apply horizon fffset here as well
                pitch_shift = sprite[3] if len(sprite) > 3 else 0
                f_drawStartY = self.internal_height / 2.0 - f_spriteHeight / 2.0 + horizon_offset - pitch_shift
                f_drawStartX = spritesurfaceX - f_spriteWidth / 2.0
                i_drawStartX = int(f_drawStartX)
                i_drawEndX = int(f_drawStartX + f_spriteWidth)
                
                if i_drawEndX < 0 or i_drawStartX > i_width: continue

                # Scale the full sprite texture to its on-screen size
                source_sprite_surf = self.sprite_renders[sprite[2]]
                scaled_sprite = pygame.transform.scale(source_sprite_surf, (i_spriteWidth, i_spriteHeight))

                # Loop through the vertical stripes of the sprite on screen
                for stripe in range(i_drawStartX, i_drawEndX):
                    # Check if stripe is on screen and in front of a wall
                    if 0 <= stripe < i_width and transformY < zBuffer[stripe]:
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
            
            # Render Sight/Crosshair
            sight_r = renpy.render(self.sight_d, width, height, st, at)
            sw, sh = sight_r.get_size()
            final_render.blit(sight_r, (width/2 - sw/2, height/2 - sh/2))
            
            is_firing = self.mouse_firing or self.gp_firing
            if is_firing:
                self.shoot_weapon()

            # Pass the pre-calculated movement state to the weapon for sway
            movement_state = {
                'is_moving': is_moving,
                'is_running': is_running_state
            }

            # Render the currently equipped weapon model over the 3D scene
            current_weapon_obj = self.weapons[self.player.current_weapon_name]
            current_weapon_obj.render_to(final_render, self.width, self.height, st, at, is_ads=effective_aiming, is_firing=is_firing, movement_state=movement_state)

            # --- 6. RENDER HUD AND EFFECTS ---
            # Logic for red overlay (damage flash + low health tint)
            flash_alpha = 0
            if self.damage_flash_timer > 0:
                flash_alpha = int(140 * (self.damage_flash_timer / 0.2))

            health_alpha = 0
            # Start showing red tint below 70 HP
            if self.player.health < 70:
                severity = (70.0 - self.player.health) / 70.0
                health_alpha = int(severity * 160)

            final_red_alpha = max(flash_alpha, health_alpha)
            final_red_alpha = min(255, final_red_alpha)

            if final_red_alpha > 0:
                flash_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                flash_surf.fill((255, 0, 0, final_red_alpha))
                final_render.blit(flash_surf, (0, 0))

            # --- RENDER DAMAGE INDICATORS ---
            center_x = self.width / 2
            center_y = self.height / 2
            indicator_radius = 200

            for ind in list(self.damage_indicators):
                ind.duration -= dtime
                if ind.duration <= 0:
                    self.damage_indicators.remove(ind)
                    continue
                
                diff = self.player.rot - ind.angle
                
                # Note: Coordinate systems math (Pygame +Y is down)
                # +Sin(diff) puts it to the Right when diff is +90deg (which is correct if Player rot=0, Enemy=90deg/South)
                ix = center_x + indicator_radius * math.sin(diff)
                iy = center_y - indicator_radius * math.cos(diff)
                
                rot_degrees = -math.degrees(diff)
                
                alpha = int(255 * (ind.duration / ind.max_duration))
                
                rot_img = pygame.transform.rotate(self.arrow_img, rot_degrees)
                
                rot_img.set_alpha(alpha)
                
                ind_tex = renpy.display.draw.load_texture(rot_img)
                
                iw, ih = ind_tex.get_size()
                final_render.blit(ind_tex, (ix - iw/2, iy - ih/2))

            if self.heal_flash_timer > 0:
                heal_flash_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                alpha = 128 * (self.heal_flash_timer / 0.2)
                heal_flash_surf.fill((0, 255, 0, alpha))
                final_render.blit(heal_flash_surf, (0, 0))

            # --- RENDER HIT MARKER ---
            if self.hit_marker_timer > 0:
                hm_w, hm_h = self.hit_marker_img.get_size()
                hm_tex = renpy.display.draw.load_texture(self.hit_marker_img)
                final_render.blit(hm_tex, (self.width/2 - hm_w/2, self.height/2 - hm_h/2))

            # Check for win condition (player is near an exit)
            for e in self.exits:
                if math.fabs(e[0] - self.player.x) < 0.5 and math.fabs(e[1] - self.player.y) < 0.5:
                    self.won = e[2]

            if self.is_arena_mode:
                # Kills Counter
                kills_text = Text(__("Kills: {}").format(persistent.stein_kills), style="sayoristein_menu_button_text", size=32)
                kills_render = renpy.render(kills_text, self.width, self.height, st, at)
                final_render.blit(kills_render, (self.width - 450, self.height - 45))

                # Coins Counter
                coins_text = Text(__("Coins: {}").format(renpy.store.stein_session_coins), style="sayoristein_menu_button_text", size=32)
                coins_render = renpy.render(coins_text, self.width, self.height, st, at)
                final_render.blit(coins_render, (self.width - 650, self.height - 45))

                # Round Counter
                round_text = Text(__("Round: {}").format(self.current_round), style="sayoristein_menu_button_text", size=32)
                round_render = renpy.render(round_text, self.width, self.height, st, at)
                final_render.blit(round_render, (self.width - 250, self.height - 45))

                if self.inter_round_timer > 0 and self.current_round > 0:
                    countdown_text = Text(__("Next round in: {:.1f}").format(self.inter_round_timer), style="sayoristein_menu_button_text", size=48)
                    countdown_render = renpy.render(countdown_text, self.width, self.height, st, at)
                    text_width, text_height = countdown_render.get_size()
                    final_render.blit(countdown_render, ( (self.width - text_width) / 2, 100))
            
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
            
            if ev.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION, pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                self.handle_gamepad_input(ev)

            if self.won is None:
                renpy.retain_after_load() # Prevents the game from advancing if an event is handled
            else:
                if self.mouse_initialized:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                return self.won # If an exit is reached, return the exit name to Ren'Py

        def check_item_pickup(self):
            """
            Checks for player collision with item sprites and applies their effects.
            """
            for sprite in list(self.sprite_positions):
                sprite_x, sprite_y, texture_index = sprite
                
                if texture_index == 7:
                    dist_to_sprite = math.sqrt((self.player.x - sprite_x)**2 + (self.player.y - sprite_y)**2)
                    
                    if dist_to_sprite < 0.8:
                        if self.player.health < 100:
                            self.player.health = min(100, self.player.health + 25)
                            self.heal_flash_timer = 0.2
                            
                            # TODO: Play a pickup sound
                            # renpy.sound.play("sounds/item_pickup.ogg", channel=1)
                            
                            self.sprite_positions.remove(sprite)

                elif texture_index == 11:
                    dist_to_sprite = math.sqrt((self.player.x - sprite_x)**2 + (self.player.y - sprite_y)**2)
                    
                    if dist_to_sprite < 0.8:
                        coin_amount = renpy.random.randint(100, 500)
                        renpy.store.stein_session_coins += coin_amount
                        # renpy.sound.play("", channel="audio") # TODO: Add a pickup sound
                        self.sprite_positions.remove(sprite)

                elif texture_index == 12:
                    dist_to_sprite = math.sqrt((self.player.x - sprite_x)**2 + (self.player.y - sprite_y)**2)
                    
                    if dist_to_sprite < 0.8:
                        base_amount = renpy.random.randint(100, 500)
                        coin_amount = int(base_amount * 3.0) 
                        
                        renpy.store.stein_session_coins += coin_amount
                        # renpy.sound.play("", channel="audio") # TODO: Add a pickup sound
                        self.sprite_positions.remove(sprite)

                elif texture_index == 13: # Shotgun Pickup
                    dist_to_sprite = math.sqrt((self.player.x - sprite_x)**2 + (self.player.y - sprite_y)**2)
                    
                    if dist_to_sprite < 0.8:
                        if not renpy.store.stein_has_shotgun:
                            renpy.store.stein_has_shotgun = True
                            renpy.notify(_("You pick up the shotgun"))
                            # renpy.sound.play("", channel="audio") # TODO: Add a sound
                            self.sprite_positions.remove(sprite)

                elif texture_index == 15:
                    dist_to_sprite = math.sqrt((self.player.x - sprite_x)**2 + (self.player.y - sprite_y)**2)
                    
                    if dist_to_sprite < 0.8:
                        if not renpy.store.stein_has_minigun:
                            renpy.store.stein_has_minigun = True
                            renpy.notify(_("You pick up the minigun"))
                            # renpy.sound.play("", channel="audio") # TODO: Add a sound
                            self.sprite_positions.remove(sprite)
        
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

        def poll_gamepad(self):
            """ 
            Polls the state of all connected joysticks directly. 
            """
            self.gp_speed = 0.0
            self.gp_strafe = 0.0
            self.gp_dir = 0.0
            self.gp_aiming = False 
            self.gp_firing = False
            self.gp_running = False
            DEADZONE = 0.25
            TRIGGER_THRESHOLD = 0.6 

            is_switch_held = False

            for joy in self.joysticks:
                try:
                    if not joy.get_init():
                        continue
                    
                    # Accelerometers and Gyroscopes often appear as joysticks on Android
                    # We ignore them to prevent tilting the phone from moving the camera
                    joy_name = joy.get_name().lower()
                    if "accelerometer" in joy_name or "gyro" in joy_name or "sensor" in joy_name:
                        continue
                        
                    # Aiming Check (L2 / Left Trigger)
                    if joy.get_numaxes() > 4:
                        if joy.get_axis(4) > TRIGGER_THRESHOLD:
                            self.gp_aiming = True
                    
                    # Sprint Check (L1 / Button 4)
                    if joy.get_numbuttons() > 4:
                        if joy.get_button(4):
                            self.gp_running = True

                    # --- Left Stick (Movement) ---
                    if joy.get_numaxes() > 0:
                        x = joy.get_axis(0)
                        if abs(x) > DEADZONE:
                            self.gp_strafe += x 

                    if joy.get_numaxes() > 1:
                        y = joy.get_axis(1)
                        if abs(y) > DEADZONE:
                            self.gp_speed -= y 

                    # Mapping for Right Stick (Look)
                    # Axis 2 seems to be Right Stick X for both PC and Android
                    look_axes = [2] # Default to Axis 2 (Right Stick X)

                    for ax_idx in look_axes:
                        if joy.get_numaxes() > ax_idx:
                            rx = joy.get_axis(ax_idx)
                            if abs(rx) > DEADZONE:
                                 look_sens = 2.5
                                 if self.is_aiming or self.gp_aiming:
                                     look_sens *= 0.25
                                 self.gp_dir -= rx * look_sens
                                 break
                    
                    # Right Stick Y (look up/down) - normally axis 3
                    if joy.get_numaxes() > 3:
                        ry = joy.get_axis(3)
                        if abs(ry) > DEADZONE:
                            pitch_speed = 6.0
                            if self.is_aiming or self.gp_aiming:
                                pitch_speed *= 0.5
                            self.player.pitch -= ry * pitch_speed
                            self.player.pitch = max(-200.0, min(200.0, self.player.pitch))

                    # --- Buttons (Polling) ---
                    # Shoot (Hold allowed): Button 0 (A/Cross) or 5 (RB/R1) or Right Trigger (Axis 5)
                    shoot_pressed = False
                    if joy.get_numbuttons() > 0:
                        if joy.get_button(0) or (joy.get_numbuttons() > 5 and joy.get_button(5)):
                            shoot_pressed = True
                    
                    if joy.get_numaxes() > 5: # Check for Axis 5 (Right Trigger)
                        rt_value = joy.get_axis(5)
                        if rt_value > TRIGGER_THRESHOLD:
                            shoot_pressed = True
                    
                    if shoot_pressed:
                        self.gp_firing = True
                            
                    # Weapon Switch (Toggle): Button 3 (Y/Triangle)
                    if joy.get_numbuttons() > 3 and joy.get_button(3):
                        is_switch_held = True

                except pygame.error:
                    continue
            
            if is_switch_held and not self.prev_btn_weapon_switch:
                # Action: Cycle Weapon
                if self.player.current_weapon_name == "fist":
                    self.player.current_weapon_name = "gun"
                elif self.player.current_weapon_name == "gun":
                    if renpy.store.stein_has_shotgun:
                        self.player.current_weapon_name = "shotgun"
                    elif renpy.store.stein_has_minigun:
                        self.player.current_weapon_name = "minigun"
                    else:
                        self.player.current_weapon_name = "fist"
                elif self.player.current_weapon_name == "shotgun":
                    if renpy.store.stein_has_minigun:
                        self.player.current_weapon_name = "minigun"
                    else:
                        self.player.current_weapon_name = "fist"
                else:
                    self.player.current_weapon_name = "fist"
            
            self.prev_btn_weapon_switch = is_switch_held

        def add_damage_indicator(self, source_dir_x, source_dir_y):
            """
            Registers a damage indicator pointing to the source.
            """
            angle = math.atan2(source_dir_y, source_dir_x)
            self.damage_indicators.append(DamageIndicator(angle))

        def update_player_from_touch_state(self):
            """
            Converts the abstract state of `active_fingers` into concrete player movement values
            (speed, direction) for the current frame.
            """
            self.touch_speed = 0.0
            self.touch_strafe = 0.0
            self.touch_dir = 0.0
            
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
                        self.touch_speed += -dy / max_dist
                        self.touch_strafe += dx / max_dist

                elif info['action'] == 'look':
                    # Convert accumulated horizontal movement into rotation
                    self.touch_dir += (info['dx_accum'] / self.width) * 25.0
                    # TODO: Implement vertical look for touch
                    info['dx_accum'] = 0.0 # Reset accumulator for the next frame

        def handle_pc_input(self, ev):
            """ Handles traditional PC input (WASD + Mouse). """
            # Handle mouse look
            if ev.type == pygame.MOUSEMOTION:
                sensitivity = 0.003
                pitch_sensitivity = 0.8 
                if self.is_aiming:
                    sensitivity *= 0.25 # Reduce sensitivity when aiming
                    pitch_sensitivity *= 0.5

                self.player.rot -= ev.rel[0] * sensitivity
                self.player.planerot -= ev.rel[0] * sensitivity
                
                # Pitch (vertical look)
                self.player.pitch -= ev.rel[1] * pitch_sensitivity
                self.player.pitch = max(-200.0, min(200.0, self.player.pitch))

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    self.mouse_initialized = False
                    return # Let Ren'Py handle the rest...

                if ev.key == pygame.K_1: self.player.current_weapon_name = "fist"
                if ev.key == pygame.K_2: self.player.current_weapon_name = "gun"
                if ev.key == pygame.K_3: 
                    if renpy.store.stein_has_shotgun:
                        self.player.current_weapon_name = "shotgun"
                if ev.key == pygame.K_4: 
                    if renpy.store.stein_has_minigun:
                        self.player.current_weapon_name = "minigun"

                # WASD controls
                if ev.key == pygame.K_w: self.kb_speed = 1
                if ev.key == pygame.K_s: self.kb_speed = -1
                if ev.key == pygame.K_a: self.kb_strafe = -1 # Strafe left
                if ev.key == pygame.K_d: self.kb_strafe = 1 # Strafe right
                # Arrow key controls (legacy)
                if ev.key == pygame.K_UP: self.kb_speed = 1
                if ev.key == pygame.K_DOWN: self.kb_speed = -1
                if ev.key == pygame.K_LEFT: self.kb_dir = 1
                if ev.key == pygame.K_RIGHT: self.kb_dir = -1
                # Actions
                if ev.key == pygame.K_SPACE:
                    self.shoot_weapon()
                
                # Sprint
                if ev.key == pygame.K_LSHIFT or ev.key == pygame.K_RSHIFT:
                    self.kb_running = True

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.button == 1: # Left mouse button
                    self.mouse_firing = True
                elif ev.button == 3: # Right mouse button (Aim)
                    self.is_aiming = True
            
            if ev.type == pygame.MOUSEBUTTONUP:
                if ev.button == 1:
                    self.mouse_firing = False
                elif ev.button == 3:
                    self.is_aiming = False
                        
            if ev.type == pygame.KEYUP: 
                if ev.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN): 
                    self.kb_speed = 0
                if ev.key in (pygame.K_a, pygame.K_d): 
                    self.kb_strafe = 0
                if ev.key in (pygame.K_LEFT, pygame.K_RIGHT): 
                    self.kb_dir = 0
                if ev.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    self.kb_running = False

        def handle_gamepad_input(self, ev):
            """ Handles input from connected Gamepads/Controllers. """
            
            if ev.type == pygame.JOYDEVICEADDED or ev.type == pygame.JOYDEVICEREMOVED:
                # Re-initialize joysticks if devices change
                pygame.joystick.quit()
                pygame.joystick.init()
                self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
                for joy in self.joysticks: 
                    try: joy.init()
                    except: pass

        
        def sprite_sort_key(self, s):
            """ Used to sort sprites by distance from the player, for rendering. """
            return (s[0] - self.player.x) ** 2 + (s[1] - self.player.y) ** 2
        
        def shoot_weapon(self):
            """ 
            Handles the shooting logic based on the currently equipped weapon.
            """
            weapon = self.weapons[self.player.current_weapon_name]
            current_time = self.oldst if self.oldst else 0.0
            
            if current_time - weapon.last_fired < weapon.cooldown:
                return

            weapon.play()
            weapon.last_fired = current_time

            if weapon.projectile_type is None: # Melee attack (fist)
                renpy.sound.play("sounds/pew.ogg", channel="audio") # Using gun channel for punch for now
                # Sort enemies to hit the closest one first
                self.enemies.sort(key=lambda e: (e.x - self.player.x)**2 + (e.y - self.player.y)**2)
                for e in self.enemies:
                    # Check if enemy is within a 2-unit range
                    if math.sqrt((e.x - self.player.x)**2 + (e.y - self.player.y)**2) < 2.0:
                        
                        taken = True
                        if hasattr(e, 'take_damage'):
                            taken = e.take_damage(weapon.damage)
                        else:
                            e.health -= weapon.damage

                        if taken:
                            if e.health <= 0:
                                renpy.sound.play("sounds/ow.ogg", channel="audio")
                                if self.is_arena_mode:
                                    persistent.stein_kills += 1
                                self.enemies.remove(e)
                                self.sprite_positions.append((e.x, e.y, e.destroyed_texture_index))
                                if renpy.random.random() < 0.40:
                                    self.sprite_positions.append((e.x, e.y, 7))
                                
                                # Arena Mode: Drop coins
                                if self.is_arena_mode:
                                    drop_prob = 1.0 if e.coin_index == 12 else 0.35
                                    if renpy.random.random() < drop_prob:
                                        self.sprite_positions.append((e.x, e.y, e.coin_index))
                                    
                                    if not renpy.store.stein_has_shotgun:
                                        shotgun_prob = 0.25 if e.coin_index == 12 else 0.10
                                        if renpy.random.random() < shotgun_prob:
                                            self.sprite_positions.append((e.x, e.y, 13))
                                            
                                    if not renpy.store.stein_has_minigun:
                                        if renpy.random.random() < 0.10:
                                            self.sprite_positions.append((e.x, e.y, 15))

                            self.hit_marker_timer = 0.15

                        break # Only hit one enemy

            elif weapon.projectile_type == 'bullet': # Pistol (gun)
                renpy.sound.play("sounds/gunshot.ogg", channel="audio")
                
                invisible = self.is_aiming or self.gp_aiming

                # Create a projectile that moves in the players direction
                bullet = Projectile(
                    wm=self,
                    x=self.player.x,
                    y=self.player.y,
                    dir_x=self.player.dirx,
                    dir_y=self.player.diry,
                    texture_index=8,
                    damage=weapon.damage,
                    fired_by_player=True,
                    is_invisible=invisible,
                    pitch=self.player.pitch
                )
                self.projectiles.append(bullet)

            elif weapon.projectile_type == 'shotgun':
                renpy.sound.play("sounds/shotgun.ogg", channel="audio")
                
                # Shotgun Spread Settings
                num_pellets = 5
                spread_angle = 0.15 # Total spread in radians
                
                invisible = self.is_aiming or self.gp_aiming
                
                if self.is_aiming or self.gp_aiming:
                    spread_angle *= 0.25

                base_angle = math.atan2(self.player.diry, self.player.dirx)
                
                for i in range(num_pellets):
                    # Calculate offset angle (centered around base direction)
                    offset = (i / float(num_pellets - 1) - 0.5) * spread_angle
                    final_angle = base_angle + offset
                    
                    p_dirx = math.cos(final_angle)
                    p_diry = math.sin(final_angle)
                    
                    pellet = Projectile(
                        wm=self,
                        x=self.player.x,
                        y=self.player.y,
                        dir_x=p_dirx,
                        dir_y=p_diry,
                        texture_index=8, # Use same bullet texture for now
                        damage=weapon.damage,
                        fired_by_player=True,
                        is_invisible=invisible,
                        pitch=self.player.pitch
                    )
                    self.projectiles.append(pellet)

        def start_next_round(self):
            """
            Sets up the next round in Arena mode.
            """
            self.current_round += 1
            
            # Filter out dead bodies (index 5) but keep medkits (index 7) and other props
            self.sprite_positions = [s for s in self.sprite_positions if s[2] != 5]

            for _ in range(self.current_round):
                if not self.spawn_points: continue
                sx, sy = renpy.random.choice(self.spawn_points)
                
                x = sx + 0.5 + (renpy.random.random() - 0.5) * 0.6
                y = sy + 0.5 + (renpy.random.random() - 0.5) * 0.6
                
                new_enemy = Guard(self, x, y, 4, 5, health=100)
                
                new_enemy.state = 'chasing'
                # Add slight speed variation to prevent perfect overlapping during movement
                new_enemy.moveSpeed += (renpy.random.random() - 0.5) * 0.2
                
                self.enemies.append(new_enemy)

            # --- Spawn Yuritler ---
            spawn_yuritler = False
            
            # Guaranteed every 10 rounds
            if self.current_round % 10 == 0:
                spawn_yuritler = True
            # 15% Chance on even rounds (that aren't multiples of 10, to avoid double trigger logic though boolean handles it)
            elif self.current_round % 2 == 0:
                if renpy.random.random() < 0.15:
                    spawn_yuritler = True
            
            if spawn_yuritler:
                if self.spawn_points:
                    self.yuritler_count += 1
                    
                    sx, sy = renpy.random.choice(self.spawn_points)
                    x = sx + 0.5 + (renpy.random.random() - 0.5) * 0.6
                    y = sy + 0.5 + (renpy.random.random() - 0.5) * 0.6
                    
                    # Scaling Health: 150 base + 50 per appearance
                    # 1st time: 150 + 0 = 150
                    # 2nd time: 150 + 50 = 200
                    boss_hp = 150 + ( (self.yuritler_count - 1) * 50 )
                    
                    boss = Yuritler(self, x, y, health=boss_hp)
                    boss.state = 'chasing'
                    self.enemies.append(boss)

            # --- Spawn Elite Guards (Every 5 Rounds) ---
            if self.current_round % 5 == 0:
                # Count increases by 1 every 5 rounds (Round 5: 1, Round 10: 2, etc.)
                num_elites = self.current_round // 5
                
                for _ in range(num_elites):
                    if not self.spawn_points: break
                    sx, sy = renpy.random.choice(self.spawn_points)
                    x = sx + 0.5 + (renpy.random.random() - 0.5) * 0.6
                    y = sy + 0.5 + (renpy.random.random() - 0.5) * 0.6
                    
                    elite = EliteGuard(self, x, y, health=100)
                    elite.state = 'chasing'
                    elite.moveSpeed += (renpy.random.random() - 0.5) * 0.2
                    self.enemies.append(elite)

            # --- Spawn Snipers (50% Chance) ---
            if self.current_round % 2 != 0:
                if renpy.random.random() < 0.50:
                    self.sniper_count += 1
                    
                    for _ in range(self.sniper_count):
                        if not self.spawn_points: break
                        sx, sy = renpy.random.choice(self.spawn_points)
                        x = sx + 0.5 + (renpy.random.random() - 0.5) * 0.6
                        y = sy + 0.5 + (renpy.random.random() - 0.5) * 0.6
                        
                        sniper = Sniper(self, x, y, health=100)
                        sniper.state = 'chasing'
                        self.enemies.append(sniper)
