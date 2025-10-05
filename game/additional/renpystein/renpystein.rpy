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
            
            self.sprite_positions = renpy.store.stein_sprites
            self.exits = exits
            self.enemies = renpy.store.stein_enemies
            self.weapon = Weapon("fist", 5, 8)
            self.won = None
            
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
            
            # Update player state from touch/mouse inputs
            if simulate_touch:
                self.update_player_from_touch_state()

            # Move the player
            self.player.move(dtime)
            
            # --- 3. SAVE PERSISTENT STATE ---
            # After moving, save the player's current state. This makes the game "survive" reloads.
            renpy.store.player_x = self.player.x
            renpy.store.player_y = self.player.y
            renpy.store.player_dirx = self.player.dirx
            renpy.store.player_diry = self.player.diry
            renpy.store.player_planex = self.player.planex
            renpy.store.player_planey = self.player.planey

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
            mergedlist = self.sprite_positions + self.enemies
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
            
            # Render the weapon model over the 3D scene
            self.weapon.render_to(final_render, self.width, self.height, st, at)
            
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

            if simulate_touch:
                # On Android, fingers generate FINGER* events for true multitouch.
                if ev.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
                    self.handle_multitouch_events(ev)
                # For testing on PC, we simulate touch with mouse buttons.
                elif ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                    self.handle_mouse_simulation(ev, x, y)
            else:
                # Handle standard keyboard input.
                self.handle_keyboard_events(ev)

            if self.won is None:
                renpy.retain_after_load() # Prevents the game from advancing if an event is handled
            else:
                return self.won # If an exit is reached, return the exit name to Ren'Py
        
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

        def handle_keyboard_events(self, ev):
            """ Handles traditional keyboard input. """
            if ev.type not in (pygame.KEYDOWN, pygame.KEYUP):
                return

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_UP: self.player.speed = 1
                if ev.key == pygame.K_DOWN: self.player.speed = -1
                if ev.key == pygame.K_LEFT: self.player.dir = 1
                if ev.key == pygame.K_RIGHT: self.player.dir = -1
                if ev.key == pygame.K_a: self.player.strafe_speed = 1 # Strafe left
                if ev.key == pygame.K_d: self.player.strafe_speed = -1 # Strafe right
                if ev.key == pygame.K_SPACE:
                    self.shoot_weapon()
                        
            if ev.type == pygame.KEYUP: 
                if ev.key in (pygame.K_UP, pygame.K_DOWN): self.player.speed = 0
                if ev.key in (pygame.K_LEFT, pygame.K_RIGHT): self.player.dir = 0
                if ev.key in (pygame.K_a, pygame.K_d): self.player.strafe_speed = 0
        
        def sprite_sort_key(self, s):
            """ Used to sort sprites by distance from the player, for rendering. """
            return (s[0] - self.player.x) ** 2 + (s[1] - self.player.y) ** 2
        
        def shoot_weapon(self):
            """ Handles the shooting logic. """
            self.weapon.play()
            self.enemies.sort(key=self.sprite_sort_key) # Sort enemies to hit the closest one
            renpy.sound.play("sounds/pew.ogg", channel=1) 
            for e in self.enemies:
                # Simple distance check for a hit
                if math.fabs(e[0] - self.player.x) < 1.2 and math.fabs(e[1] - self.player.y) < 1.2:
                    renpy.sound.play("sounds/ow.ogg", channel=1)
                    # When an enemy is hit, remove it from the active enemies list
                    # and add a "destroyed" sprite in its place.
                    self.enemies.remove(e)
                    self.sprite_positions.append((e[0], e[1], e[3]))
                    break
