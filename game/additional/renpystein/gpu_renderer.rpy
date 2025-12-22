init 10 python:
    SLOT_MELEE   = 0
    SLOT_HANDGUN = 1
    SLOT_LONG    = 2
    SLOT_SPECIAL = 3

    renpy.register_shader("stein.raycaster", variables="""
        uniform float u_time;
        uniform vec2 u_resolution;
        uniform vec2 u_player_pos;
        uniform vec2 u_player_dir;
        uniform vec2 u_player_plane;
        uniform float u_pitch;
        uniform float u_z_offset;
        uniform float u_vertical_scale;
        uniform sampler2D u_sky_texture;
        uniform sampler2D u_map_texture;
        uniform vec2 u_map_size;
        uniform vec2 u_map_uv_scale; 
        uniform sampler2D u_wall_atlas; 
        uniform sampler2D u_floor_texture;
        uniform float u_num_textures;
        uniform sampler2D u_sprite_atlas; 
        uniform float u_num_sprite_textures;
        uniform vec4 u_sprites[64]; // x, y, texture_id, pitch_offset
        uniform int u_num_active_sprites;
        uniform float u_flash_intensity;
        uniform vec4 u_light_positions[16];
        uniform float u_num_active_lights;
        uniform float u_flashlight_active;
        uniform vec2 u_flashlight_bob;
        varying vec2 v_tex_coord;
        attribute vec2 a_tex_coord;
    """, vertex_200="""
        v_tex_coord = a_tex_coord;
    """, fragment_300="""
        const int MAX_STEPS = 128; 
        const float MAX_DIST = 60.0;

        vec2 uv = v_tex_coord;

        // RAY GENERATION (3D)
        // Player Position (Camera Origin). Z=0.5 is eye level + offsets
        vec3 rayPos = vec3(u_player_pos.x, u_player_pos.y, 0.5 + u_z_offset);
        
        // Ray Direction
        float cameraX = 2.0 * uv.x - 1.0; 
        vec2 rayDirXY = u_player_dir + u_player_plane * cameraX;
        
        // Map screen Y (0..1) to vertical view angle (slope)
        // Center (0.5) is straight ahead (slope 0)
        // 0.5 - uv.y gives range [0.5, -0.5]
        // Scale by vertical FOV (u_vertical_scale) and add pitch (look up/down)
        float screenY = (0.5 - uv.y) * 2.0; 
        float rayDirZ = (screenY / u_vertical_scale) + u_pitch;
        
        vec3 rayDir = normalize(vec3(rayDirXY, rayDirZ));

        vec2 flashDirXY = u_player_dir + (u_player_plane * u_flashlight_bob.x);
        float flashDirZ = u_pitch + u_flashlight_bob.y;
        
        vec3 flashDir = normalize(vec3(flashDirXY, flashDirZ));
        
        // DDA SETUP
        ivec3 mapPos = ivec3(floor(rayPos));
        vec3 deltaDist = abs(1.0 / rayDir);
        ivec3 stepDir;
        vec3 sideDist;
        
        if (rayDir.x < 0.0) { stepDir.x = -1; sideDist.x = (rayPos.x - float(mapPos.x)) * deltaDist.x; }
        else                { stepDir.x = 1;  sideDist.x = (float(mapPos.x) + 1.0 - rayPos.x) * deltaDist.x; }
        
        if (rayDir.y < 0.0) { stepDir.y = -1; sideDist.y = (rayPos.y - float(mapPos.y)) * deltaDist.y; }
        else                { stepDir.y = 1;  sideDist.y = (float(mapPos.y) + 1.0 - rayPos.y) * deltaDist.y; }
        
        if (rayDir.z < 0.0) { stepDir.z = -1; sideDist.z = (rayPos.z - float(mapPos.z)) * deltaDist.z; }
        else                { stepDir.z = 1;  sideDist.z = (float(mapPos.z) + 1.0 - rayPos.z) * deltaDist.z; }

        // DDA LOOP (3D)
        int hit = 0;
        int side = 0; // 0=X, 1=Y, 2=Z
        int wallID = 0;
        float rayDist = 0.0;

        for (int i = 0; i < MAX_STEPS; i++) {
            if (sideDist.x < sideDist.y) {
                if (sideDist.x < sideDist.z) {
                    rayDist = sideDist.x;
                    sideDist.x += deltaDist.x;
                    mapPos.x += stepDir.x;
                    side = 0;
                } else {
                    rayDist = sideDist.z;
                    sideDist.z += deltaDist.z;
                    mapPos.z += stepDir.z;
                    side = 2;
                }
            } else {
                if (sideDist.y < sideDist.z) {
                    rayDist = sideDist.y;
                    sideDist.y += deltaDist.y;
                    mapPos.y += stepDir.y;
                    side = 1;
                } else {
                    rayDist = sideDist.z;
                    sideDist.z += deltaDist.z;
                    mapPos.z += stepDir.z;
                    side = 2;
                }
            }
            
            if (rayDist > MAX_DIST) { hit = 2; break; } // Too far
            
            // Map Bounds Check
            if (mapPos.x < 0 || mapPos.x >= int(u_map_size.x) || mapPos.y < 0 || mapPos.y >= int(u_map_size.y)) {
                hit = 2; break; // Hit Sky
            }
            
            // Voxel Check (Only Z=0 has blocks yet)
            if (mapPos.z == 0) {
                vec2 mapUV = (vec2(mapPos.x, mapPos.y) + 0.5) / u_map_size;
                mapUV = mapUV * u_map_uv_scale;
                vec4 mapPixel = texture2D(u_map_texture, mapUV);
                if (mapPixel.r > 0.5) {
                    wallID = int(mapPixel.g * 255.0 + 0.5);
                    hit = 1;
                    break;
                }
            } else if (mapPos.z < 0) {
                if (mapPos.z == -1) {
                    wallID = 9;
                    hit = 1;
                    break;
                }
            }
        }

        vec3 color;
        
        if (hit == 1) {
            vec3 hitPos = rayPos + rayDir * rayDist;
            
            if (side == 2 && mapPos.z == -1) {
                vec2 floorUV = vec2(fract(hitPos.x), fract(hitPos.y));
                color = texture2D(u_floor_texture, floorUV, -1.0).rgb;
                color *= 0.6;
            } else {
                vec2 texUV;
                if (side == 0) { // X-Side
                    float wallX = hitPos.y; 
                    if (rayDir.x > 0.0) wallX = 1.0 - wallX;
                    texUV = vec2(fract(wallX), fract(1.0 - hitPos.z));
                } 
                else if (side == 1) { // Y-Side
                    float wallX = hitPos.x;
                    if (rayDir.y < 0.0) wallX = 1.0 - wallX;
                    texUV = vec2(fract(wallX), fract(1.0 - hitPos.z));
                }
                else { // Side 2 (Wall Top/Bottom)
                    texUV = vec2(fract(hitPos.x), fract(hitPos.y));
                }
                
                float texRes = 64.0;
                texUV = (floor(texUV * texRes) + 0.5) / texRes;
                
                float singleTexWidth = 1.0 / u_num_textures;
                float texOffset = float(wallID - 1) * singleTexWidth;
                
                float clampedU = texUV.x * (1.0 - 0.002) + 0.001;
                float finalU = texOffset + (clampedU * singleTexWidth);
                float finalV = texUV.y;
                
                if (finalV < 0.0 || finalV > 1.0) {
                    color = vec3(0.0);
                } else {
                    color = texture2D(u_wall_atlas, vec2(finalU, finalV), -4.0).rgb;
                }
            }
            
            vec3 finalColor = color;
            
            float fogDist = length(hitPos.xy - u_player_pos);
            float ambientParams = 1.0 - (fogDist / 15.0); 
            vec3 ambientLight = vec3(0.1, 0.1, 0.15); 
            ambientLight += max(0.0, ambientParams) * 0.4; 
            
            vec3 totalLight = ambientLight;

            if (u_flashlight_active > 0.5) {
                vec3 lightVec = normalize(hitPos - rayPos);
                
                float dotProd = dot(lightVec, flashDir); 
                float dist3D = distance(hitPos, rayPos);

                if (dotProd > 0.88) { 
                    float spotEffect = smoothstep(0.88, 0.95, dotProd);
                    
                    float att = 1.0 / (1.0 + dist3D * 0.1 + dist3D * dist3D * 0.02);
                    vec3 flashLightColor = vec3(0.95, 0.95, 1.0);
                    
                    totalLight += flashLightColor * att * 1.8 * spotEffect;
                }
            }

            if (u_flash_intensity > 0.01) {
                float distToPlayer = distance(hitPos.xy, u_player_pos);
                float flashAtt = 1.0 / (0.5 + (distToPlayer * distToPlayer) * 0.1);
                vec3 flashColor = vec3(1.0, 0.8, 0.4);
                totalLight += flashColor * u_flash_intensity * flashAtt * 2.0;
            }

            for (int i = 0; i < 16; i++) {
                if (float(i) >= u_num_active_lights) break;
                
                vec4 lightData = u_light_positions[i]; 
                vec2 lightPos = lightData.xy;
                float radius = lightData.z;
                float intensity = lightData.w;
                
                float distToLight = distance(hitPos.xy, lightPos);
                
                if (distToLight < radius) {
                    float att = 1.0 - (distToLight / radius);
                    att = att * att; 
                    
                    vec3 lampColor = vec3(0.2, 1.0, 0.2); 
                    totalLight += lampColor * intensity * att;
                }
            }

            float faceShadow = 1.0;
            if (side == 1) faceShadow = 0.7; 
            if (side == 2) faceShadow = 1.0; 
            
            color = finalColor * totalLight * faceShadow;

        } else {
            // Skybox
            vec2 skyUV = uv;
            // Apply pitch to skyUV.y
            skyUV.y -= u_pitch; 
            skyUV.y = clamp(skyUV.y, 0.0, 1.0);
            color = texture2D(u_sky_texture, skyUV).rgb;
        }

        // SPRITE RENDERING (Adapted for 3D)
        // We approximate 2D billboard logic using the 3D ray distance
        // Project rayDist onto the XY plane
        // Using length() is safer, technically less accurate for planar depth...
        float perpWallDist = rayDist * length(rayDir.xy); 
        
        // If we didnt hit a wall (Sky/Void), the depth is infinite
        if (hit != 1) perpWallDist = 10000.0;
        
        float currentDepth = perpWallDist;
        
        // Precalculate pitch shift in pixels for sprites
        float pitchPixeLCTRL = u_pitch * u_vertical_scale * (u_resolution.y / 2.0);

        float invDet = 1.0 / (u_player_plane.x * u_player_dir.y - u_player_dir.x * u_player_plane.y);

        for (int i = 0; i < 64; i++) {
            if (i >= u_num_active_sprites) break;
            
            vec4 spriteData = u_sprites[i];
            vec2 spritePos = spriteData.xy;
            float texID = spriteData.z;
            float spritePitch = spriteData.w; 

            float spX = spritePos.x - u_player_pos.x;
            float spY = spritePos.y - u_player_pos.y;

            float transformX = invDet * (u_player_dir.y * spX - u_player_dir.x * spY);
            float transformY = invDet * (-u_player_plane.y * spX + u_player_plane.x * spY); 

            if (transformY <= 0.1) continue;
            // Robust depth check
            if (transformY >= currentDepth) continue; 

            float spriteScreenX = (u_resolution.x / 2.0) * (1.0 + transformX / transformY);
            
            // Scale sprites down
            float spriteScale = 0.55; 
            float spriteHeight = abs(u_resolution.y / transformY) * u_vertical_scale * spriteScale; 
            float spriteWidth = spriteHeight; 

            // Sprite Anchoring Logic (Floor Alignment)
            // Calculate where the floor (Z=0) is on screen at the sprite's depth
            // Camera Height = 0.5 + u_z_offset
            float camHeight = 0.5 + u_z_offset;
            
            // Projection of floor: Center + (CamHeight / Depth * Scale * Res/2) + Pitch
            float floorPixelOffset = (camHeight / transformY) * u_vertical_scale * (u_resolution.y / 2.0);
            
            float spritePixeLCTRL = spritePitch * u_vertical_scale * (u_resolution.y / 2.0);
            
            float drawEndY = (u_resolution.y / 2.0) + floorPixelOffset + pitchPixeLCTRL - spritePixeLCTRL;
            float drawStartY = drawEndY - spriteHeight;
            
            float drawStartX = spriteScreenX - spriteWidth / 2.0;
            float drawEndX = spriteScreenX + spriteWidth / 2.0;

            float currentPixelX = uv.x * u_resolution.x; 
            float currentPixelY = uv.y * u_resolution.y;

            if (currentPixelX >= drawStartX && currentPixelX <= drawEndX) {
                float texX = (currentPixelX - drawStartX) / spriteWidth;
                
                float texY = (currentPixelY - drawStartY) / spriteHeight;
                // texY = 1.0 - texY;

                if (texY >= 0.0 && texY <= 1.0) {
                    float singleTexW = 1.0 / u_num_sprite_textures;
                    float atlasX = (texID * singleTexW) + (texX * singleTexW);
                    
                    vec4 spriteCol = texture2D(u_sprite_atlas, vec2(atlasX, texY));
                    
                    if (spriteCol.a > 0.5) {
                        
                        float sprDist = length(vec2(spX, spY)); 
                        float sprAmbParams = 1.0 - (sprDist / 15.0);
                        vec3 sprLight = vec3(0.1, 0.1, 0.15);
                        sprLight += max(0.0, sprAmbParams) * 0.4;

                        if (u_flashlight_active > 0.5) {
                            float dotProd = dot(rayDir, flashDir);
                            
                            float dist3D = transformY;
                            
                            if (dotProd > 0.88) {
                                float spotEffect = smoothstep(0.88, 0.95, dotProd);
                                float att = 1.0 / (1.0 + dist3D * 0.1 + dist3D * dist3D * 0.02);
                                vec3 flashLightColor = vec3(0.95, 0.95, 1.0);
                                
                                sprLight += flashLightColor * att * 1.8 * spotEffect;
                            }
                        }

                        if (u_flash_intensity > 0.01) {
                            float flashAtt = 1.0 / (0.5 + (sprDist * sprDist) * 0.1);
                            vec3 flashColor = vec3(1.0, 0.8, 0.4);
                            sprLight += flashColor * u_flash_intensity * flashAtt * 2.0;
                        }

                        for (int j = 0; j < 16; j++) {
                            if (float(j) >= u_num_active_lights) break;
                            
                            vec4 lData = u_light_positions[j];
                            float lDist = distance(spritePos, lData.xy);
                            
                            if (lDist < lData.z) {
                                float att = 1.0 - (lDist / lData.z);
                                att = att * att;
                                vec3 lampColor = vec3(0.4, 0.9, 0.4);
                                sprLight += lampColor * lData.w * att;
                            }
                        }

                        color = spriteCol.rgb * sprLight;
                        currentDepth = transformY; 
                    }
                }
            }
        }

        gl_FragColor = vec4(color, 1.0);
    """)

    renpy.register_shader("stein.motion_blur", variables="""
        uniform sampler2D tex0;
        uniform float u_blur_amount;
        varying vec2 v_tex_coord;
    """, fragment_200="""
        vec2 mb_uv = v_tex_coord;
        vec4 mb_color = texture2D(tex0, mb_uv);
        
        if (abs(u_blur_amount) > 0.001) {
            float blur = u_blur_amount * 0.02;
            vec4 sum = vec4(0.0);
            
            // 5-tap optimization
            sum += texture2D(tex0, vec2(mb_uv.x - blur * 2.0, mb_uv.y)) * 0.1;
            sum += texture2D(tex0, vec2(mb_uv.x - blur * 1.0, mb_uv.y)) * 0.25;
            sum += texture2D(tex0, vec2(mb_uv.x, mb_uv.y)) * 0.3;
            sum += texture2D(tex0, vec2(mb_uv.x + blur * 1.0, mb_uv.y)) * 0.25;
            sum += texture2D(tex0, vec2(mb_uv.x + blur * 2.0, mb_uv.y)) * 0.1;
            
            gl_FragColor = sum;
        } else {
            gl_FragColor = mb_color;
        }
    """)

    renpy.register_shader("stein.muzzle_flash", variables="""
        varying vec2 v_tex_coord;
        attribute vec2 a_tex_coord;
        uniform float u_flash_progress; 
        uniform float u_flash_angle;
        uniform vec3 u_flash_color;
    """, vertex_200="""
        v_tex_coord = a_tex_coord;
    """, fragment_200="""
        // Center UVs to [-1, 1] range
        vec2 mf_uv = (v_tex_coord - 0.5) * 2.0; 
        
        // Internal rotation
        float mf_s = sin(u_flash_angle);
        float mf_c = cos(u_flash_angle);
        mf_uv = mat2(mf_c, -mf_s, mf_s, mf_c) * mf_uv;
        
        float mf_dist = length(mf_uv);
        float mf_angle = atan(mf_uv.y, mf_uv.x);
        
        float mf_spikes = abs(sin(mf_angle * 4.0)) * 0.4 + abs(sin(mf_angle * 9.0)) * 0.6;
        
        float mf_core = exp(-mf_dist * 5.0) * 2.5;
        float mf_rays = exp(-mf_dist * (4.0 + 8.0 * (1.0 - mf_spikes))) * 1.2;
        
        float mf_mask = smoothstep(1.0, 0.2, mf_dist);
        
        float mf_intensity = (mf_core + mf_rays) * (1.0 - u_flash_progress);
        mf_intensity = clamp(mf_intensity * mf_mask, 0.0, 1.0);
        
        gl_FragColor = vec4(u_flash_color * mf_intensity, mf_intensity);
    """)

    import math
    import pygame
    import time

    if renpy.android:
        simulate_touch = True
    else:
        simulate_touch = False

    config.pygame_events.extend([
        pygame.FINGERMOTION, pygame.FINGERDOWN, pygame.FINGERUP,
        pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP,
        pygame.JOYHATMOTION, pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED
    ])

    renpy.music.register_channel("gun_sfx", mixer="sfx", loop=False)
    renpy.music.register_channel("shotgun_sfx", mixer="sfx", loop=False)
    renpy.music.register_channel("enemy_sfx", mixer="sfx", loop=False)

    texWidth = 64
    texHeight = 64
    twoPI = math.pi * 2

    class DamageIndicator(object):
        def __init__(self, angle, duration=2.0):
            self.angle = angle
            self.duration = duration
            self.max_duration = duration

    class Player(object):
        def __init__(self, wm, x, y, dirx, diry, planex, planey):
            self.wm = wm
            self.x = x; self.y = y
            self.dirx = float(dirx); self.diry = float(diry)
            self.planex = float(planex); self.planey = float(planey)
            self.health = 100
            self.pitch = 0.0
            self.current_weapon_name = "fist"
            self.rot = math.atan2(diry, dirx)
            self.planerot = math.atan2(planey, planex)
            self.dir = 0; self.speed = 0; self.strafe_speed = 0
            self.moveSpeed = 2.5; self.rotSpeed = 90 * math.pi / 180
            self.mapWidth = wm.mapWidth; self.mapHeight = wm.mapHeight
            self.z = 0.0; self.velocity_z = 0.0
            self.GRAVITY = 35.0; self.JUMP_FORCE = 8.5; self.CROUCH_DEPTH = -0.4
            self.is_grounded = True; self.is_crouching = False
            self.crouch_timer = 0.0; self.crouch_duration = 0.06

        def get_ground_height_at(self, x, y): return 0.0

        def trigger_jump(self):
            if self.is_grounded and not self.is_crouching:
                self.is_crouching = True; self.crouch_timer = self.crouch_duration

        def update_physics(self, dt):
            if self.is_crouching:
                self.crouch_timer -= dt
                progress = 1.0 - (self.crouch_timer / self.crouch_duration)
                self.z = self.get_ground_height_at(self.x, self.y) + (self.CROUCH_DEPTH * math.sin(progress * math.pi))
                if self.crouch_timer <= 0:
                    self.is_crouching = False; self.is_grounded = False; self.velocity_z = self.JUMP_FORCE
            if not self.is_grounded:
                self.velocity_z -= self.GRAVITY * dt
                self.z += self.velocity_z * dt
                floor_h = self.get_ground_height_at(self.x, self.y)
                if self.z <= floor_h:
                    self.z = floor_h; self.velocity_z = 0.0; self.is_grounded = True

        def move(self, dt):
            self.update_physics(dt)
            moveStep = self.speed * self.moveSpeed * dt
            strafeStep = self.strafe_speed * self.moveSpeed * dt
            self.rot += self.dir * self.rotSpeed * dt
            self.rot %= twoPI
            self.planerot += self.dir * self.rotSpeed * dt
            self.planerot %= twoPI
            newX = self.x + math.cos(self.rot) * moveStep + math.cos(self.planerot) * strafeStep
            newY = self.y + math.sin(self.rot) * moveStep + math.sin(self.planerot) * strafeStep
            self.dirx = math.cos(self.rot); self.diry = math.sin(self.rot)
            self.planex = math.cos(self.planerot); self.planey = math.sin(self.planerot)
            position = self.wm.checkCollision(self.x, self.y, newX, newY, 0.45)
            self.x = position[0]; self.y = position[1]

    class Projectile(object):
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
            
            if self.fired_by_player:
                self.speed = 100.0 
            else:
                self.speed = 12.0

        def update(self, dt):
            distance_to_travel = self.speed * dt
            
            step_size = 0.4
            dist_traveled = 0.0

            while dist_traveled < distance_to_travel:
                step = min(step_size, distance_to_travel - dist_traveled)
                
                self.x += self.dir_x * step
                self.y += self.dir_y * step
                dist_traveled += step

                if self.wm.isBlocking(self.x, self.y): 
                    return False

                if not self.fired_by_player:
                    player = self.wm.player
                    if math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2) < 0.5:
                        player.health -= self.damage
                        self.wm.add_damage_indicator(-self.dir_x, -self.dir_y)
                        self.wm.damage_flash_timer = 0.2
                        renpy.sound.play("sounds/ow.ogg", channel="audio")
                        return False
                else:
                    for enemy in list(self.wm.enemies):
                        if math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2) < 0.5:
                            if hasattr(self, 'pitch'):
                                safe_dist = max(0.1, math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2))
                                enemy_vis_height = self.wm.height / safe_dist
                                calc_height = min(enemy_vis_height, self.wm.height * 1.2)
                                if abs(self.pitch) > (calc_height / 2.0) * 0.2: 
                                    continue

                            taken = True
                            if hasattr(enemy, 'take_damage'): 
                                taken = enemy.take_damage(self.damage)
                            else:
                                enemy.health -= self.damage
                            
                            if taken:
                                self.wm.hit_marker_timer = 0.15
                                renpy.sound.play("sounds/ow.ogg", channel="audio")
                                if enemy.health <= 0:
                                    if self.wm.is_arena_mode: persistent.stein_kills += 1
                                    if enemy in self.wm.enemies: self.wm.enemies.remove(enemy)
                                    self.wm.sprite_positions.append((enemy.x, enemy.y, enemy.destroyed_texture_index))
                                    if renpy.random.random() < 0.40:
                                        self.wm.sprite_positions.append((enemy.x, enemy.y, 7)) # Medkit
                                    
                                    if self.wm.is_arena_mode:
                                        drop_prob = 1.0 if enemy.coin_index == 12 else 0.35
                                        if renpy.random.random() < drop_prob:
                                            self.wm.sprite_positions.append((enemy.x, enemy.y, enemy.coin_index)) # Coins

                                        if not renpy.store.stein_has_shotgun:
                                            if renpy.random.random() < (0.25 if enemy.coin_index == 12 else 0.10):
                                                self.wm.sprite_positions.append((enemy.x, enemy.y, 13)) # Shotgun
                                        
                                        if not renpy.store.stein_has_minigun:
                                            if renpy.random.random() < 0.10:
                                                self.wm.sprite_positions.append((enemy.x, enemy.y, 15)) # Minigun

                                return False
            return True

    class BaseEnemy(object):
        def __init__(self, wm, x, y, health=100):
            self.wm = wm
            self.x = x; self.y = y; self.health = health
            self.state = 'idle'
            self.last_known_x = None; self.last_known_y = None
            self.texture_index = 0; self.destroyed_texture_index = 0
            self.moveSpeed = 1.5; self.rotSpeed = 75 * math.pi / 180
            self.attack_range = 8.0; self.sight_range = 15.0
            if self.wm.is_arena_mode: self.attack_range = 24.0; self.sight_range = 30.0
            self.attack_cooldown = 1.5; self.damage = 10; self.coin_index = 11
            self.attack_timer = 1.0
            self.mapWidth = wm.mapWidth; self.mapHeight = wm.mapHeight

        def update(self, dt, player):
            self.attack_timer = max(0, self.attack_timer - dt)
            player_x, player_y = player.x, player.y
            dist_to_player = math.sqrt((player_x - self.x)**2 + (player_y - self.y)**2)
            has_los = self.has_line_of_sight(player_x, player_y)

            if has_los: self.last_known_x = player_x; self.last_known_y = player_y

            if self.state == 'idle':
                if dist_to_player < self.sight_range and has_los: self.state = 'chasing'
            elif self.state == 'chasing':
                target_x, target_y = player_x, player_y
                if not has_los:
                    if self.last_known_x is not None:
                        target_x, target_y = self.last_known_x, self.last_known_y
                        if math.sqrt((target_x - self.x)**2 + (target_y - self.y)**2) < 1.0:
                            self.state = 'idle'; self.last_known_x = None; return
                    else: self.state = 'idle'; return
                
                should_move = True
                if has_los:
                    if dist_to_player < self.attack_range:
                        if dist_to_player < self.attack_range * 0.5: should_move = False
                        if self.attack_timer == 0: self.attack(player)
                    else: should_move = True
                if should_move: self.move(dt, target_x, target_y)

        def attack(self, player): self.attack_timer = self.attack_cooldown

        def check_wall_collision(self, x, y, radius=0.3):
            if self.wm.isBlocking(x, y): return True
            if self.wm.isBlocking(x + radius, y): return True
            if self.wm.isBlocking(x - radius, y): return True
            if self.wm.isBlocking(x, y + radius): return True
            if self.wm.isBlocking(x, y - radius): return True
            return False

        def move(self, dt, target_x, target_y):
            dx = target_x - self.x; dy = target_y - self.y
            angle = math.atan2(dy, dx)
            look_dist = 1.2; radius = 0.35
            ahead_x = self.x + math.cos(angle) * look_dist
            ahead_y = self.y + math.sin(angle) * look_dist
            
            if self.check_wall_collision(ahead_x, ahead_y, radius):
                offsets = [-0.785, 0.785, -1.57, 1.57]
                found_path = False
                for off in offsets:
                    test_angle = angle + off
                    tx = self.x + math.cos(test_angle) * look_dist
                    ty = self.y + math.sin(test_angle) * look_dist
                    if not self.check_wall_collision(tx, ty, radius):
                        angle = test_angle; found_path = True; break
                if not found_path: angle += 2.0

            moveStep = self.moveSpeed * dt
            vx = math.cos(angle) * moveStep; vy = math.sin(angle) * moveStep
            if not self.check_wall_collision(self.x + vx, self.y, radius): self.x += vx
            if not self.check_wall_collision(self.x, self.y + vy, radius): self.y += vy

        def has_line_of_sight(self, target_x, target_y):
            ray_start_x, ray_start_y = self.x, self.y
            ray_dir_x = target_x - ray_start_x; ray_dir_y = target_y - ray_start_y
            ray_len = math.sqrt(ray_dir_x**2 + ray_dir_y**2)
            if ray_len == 0: return True
            ray_dir_x /= ray_len; ray_dir_y /= ray_len
            if ray_dir_x == 0: ray_dir_x = 1e-9
            if ray_dir_y == 0: ray_dir_y = 1e-9
            delta_dist_x = abs(1 / ray_dir_x); delta_dist_y = abs(1 / ray_dir_y)
            map_x, map_y = int(ray_start_x), int(ray_start_y)
            if ray_dir_x < 0: step_x = -1; side_dist_x = (ray_start_x - map_x) * delta_dist_x
            else: step_x = 1; side_dist_x = (map_x + 1.0 - ray_start_x) * delta_dist_x
            if ray_dir_y < 0: step_y = -1; side_dist_y = (ray_start_y - map_y) * delta_dist_y
            else: step_y = 1; side_dist_y = (map_y + 1.0 - ray_start_y) * delta_dist_y
            
            current_dist = 0
            while current_dist < ray_len:
                if side_dist_x < side_dist_y: side_dist_x += delta_dist_x; map_x += step_x; current_dist = side_dist_x
                else: side_dist_y += delta_dist_y; map_y += step_y; current_dist = side_dist_y
                if self.wm.isBlocking(map_x, map_y): return False
            return True

    class Guard(BaseEnemy):
        def __init__(self, wm, x, y, texture_index, destroyed_texture_index, health=100):
            super(Guard, self).__init__(wm, x, y, health)
            self.texture_index = texture_index; self.destroyed_texture_index = destroyed_texture_index
            self.moveSpeed = 1.5; self.damage = 10; self.bullet_texture_index = 6

        def attack(self, player):
            super(Guard, self).attack(player)
            dir_x = player.x - self.x; dir_y = player.y - self.y
            dist = math.sqrt(dir_x**2 + dir_y**2)
            if dist > 0: dir_x /= dist; dir_y /= dist
            self.wm.projectiles.append(Projectile(self.wm, self.x, self.y, dir_x, dir_y, self.bullet_texture_index, self.damage, fired_by_player=False))
            renpy.sound.play("sounds/e-gunshot.ogg", channel="audio")

    class Yuritler(Guard):
        def __init__(self, wm, x, y, health=150):
            super(Yuritler, self).__init__(wm, x, y, 9, 10, health)
            self.damage = 5; self.moveSpeed = 1.8; self.attack_cooldown = 1.0; self.coin_index = 12
        
        def attack(self, player):
            self.attack_timer = self.attack_cooldown
            dir_x = player.x - self.x; dir_y = player.y - self.y
            dist = math.sqrt(dir_x**2 + dir_y**2)
            if dist > 0:
                base_angle = math.atan2(dir_y, dir_x)
                for i in range(4):
                    offset = (i / 3.0 - 0.5) * 0.2
                    p_dirx = math.cos(base_angle + offset); p_diry = math.sin(base_angle + offset)
                    self.wm.projectiles.append(Projectile(self.wm, self.x, self.y, p_dirx, p_diry, self.bullet_texture_index, self.damage, fired_by_player=False))
            renpy.sound.play("sounds/e-gunshot.ogg", channel="audio")

    class EliteGuard(Guard):
        def __init__(self, wm, x, y, health=100):
            super(EliteGuard, self).__init__(wm, x, y, 4, 5, health)
            self.damage = 3; self.attack_cooldown = 0.1
            self.burst_limit = 10; self.shots_fired_in_burst = 0
            self.is_reloading = False; self.reload_time = 5.0; self.reload_timer = 0.0

        def update(self, dt, player):
            if self.is_reloading:
                self.reload_timer -= dt
                if self.reload_timer <= 0: self.is_reloading = False; self.shots_fired_in_burst = 0; self.attack_timer = 0.5
            super(EliteGuard, self).update(dt, player)

        def attack(self, player):
            if self.is_reloading: return
            self.attack_timer = self.attack_cooldown
            dir_x = player.x - self.x; dir_y = player.y - self.y
            dist = math.sqrt(dir_x**2 + dir_y**2)
            if dist > 0: dir_x /= dist; dir_y /= dist
            self.wm.projectiles.append(Projectile(self.wm, self.x, self.y, dir_x, dir_y, self.bullet_texture_index, self.damage, fired_by_player=False))
            renpy.sound.play("sounds/e-gunshot.ogg", channel="audio")
            self.shots_fired_in_burst += 1
            if self.shots_fired_in_burst >= self.burst_limit: self.is_reloading = True; self.reload_timer = self.reload_time

    class Sniper(Guard):
        def __init__(self, wm, x, y, health=100):
            super(Sniper, self).__init__(wm, x, y, 4, 5, health)
            self.damage = 20; self.attack_cooldown = 1.5; self.moveSpeed = 3.0; self.bullet_texture_index = 14
            self.dodge_cooldown = 4.0; self.dodge_timer = 0.0

        def update(self, dt, player):
            self.dodge_timer = max(0, self.dodge_timer - dt)
            super(Sniper, self).update(dt, player)

        def take_damage(self, amount):
            if self.dodge_timer <= 0:
                self.dodge_timer = self.dodge_cooldown
                player = self.wm.player
                dx = player.x - self.x; dy = player.y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    ndx = dx / dist; ndy = dy / dist
                    strafe_x = -ndy; strafe_y = ndx
                    dodge_distance = 1.5
                    tx = self.x + strafe_x * dodge_distance; ty = self.y + strafe_y * dodge_distance
                    if not self.check_wall_collision(tx, ty, 0.35): self.x = tx; self.y = ty
                    else:
                        tx = self.x - strafe_x * dodge_distance; ty = self.y - strafe_y * dodge_distance
                        if not self.check_wall_collision(tx, ty, 0.35): self.x = tx; self.y = ty
                return False
            self.health -= amount
            return True

    class Weapon(object):
        def __init__(self, name, category, 
            normal_frameCount=5, normal_fps=15, normal_flash_frame=0, normal_name=None,
            ads_enter_frameCount=0, ads_enter_fps=20, ads_enter_name=None,
            ads_fire_frameCount=0, ads_fire_fps=15, ads_fire_flash_frame=0, ads_fire_name=None,
            run_enter_frameCount=0, run_enter_fps=15, run_enter_flash_frame=0, run_enter_name=None,
            zoom_factor=11, damage=25, projectile_type=None, cooldown=0.5, 
            ads_idle=None, ads_fire=None, loop_frames=None, 
            flash_offset=(0,0), flash_ads_offset=(0,0), flash_size=1.0, flash_color=(1.0, 0.9, 0.7),
            frameCount=None, ads_name=None, ads_frameCount=None 
            ):
            
            self.name = name
            self.category = category
            
            if frameCount is not None: normal_frameCount = frameCount
            if ads_frameCount is not None: ads_fire_frameCount = ads_frameCount
            if ads_name is not None: ads_fire_name = ads_name

            self.damage = damage; self.projectile_type = projectile_type; self.cooldown = cooldown
            self.loop_frames = loop_frames
            
            self.flash_config = {
                'offset_normal': flash_offset,
                'offset_ads': flash_ads_offset,
                'size': flash_size,
                'color': flash_color,
                'frame_normal': normal_flash_frame,
                'frame_ads': ads_fire_flash_frame,
                'frame_run': run_enter_flash_frame
            }
            
            self.playing = False
            self.frame_index = 0
            self.oldst = None
            self.last_fired = 0.0
            self.current_flash_rot = 0.0
            
            # --- Animation Data ---
            self.anims = {
                'normal': [],
                'ads_enter': [],
                'ads_fire': [],
                'run_enter': []
            }
            
            self.fps = {
                'normal': normal_fps,
                'ads_enter': ads_enter_fps,
                'ads_fire': ads_fire_fps,
                'run_enter': run_enter_fps
            }
            
            # Load Normal
            base_normal = normal_name if normal_name else name
            for i in range(normal_frameCount): 
                self.anims['normal'].append(Transform("pics/weapons/%s%s.webp" % (base_normal, i+1), xysize=(1280, 720)))
                
            # Load ADS Enter
            if ads_enter_frameCount > 0:
                base_enter = ads_enter_name if ads_enter_name else (name + "_ads_enter")
                for i in range(ads_enter_frameCount):
                    self.anims['ads_enter'].append(Transform("pics/weapons/%s%s.webp" % (base_enter, i+1), xysize=(1280, 720)))

            # Load ADS Fire
            if ads_fire_frameCount > 0:
                base_ads_fire = ads_fire_name if ads_fire_name else (name + "_ads")
                for i in range(ads_fire_frameCount):
                    self.anims['ads_fire'].append(Transform("pics/weapons/%s%s.webp" % (base_ads_fire, i+1), xysize=(1280, 720)))
            
            # Load Run Enter
            if run_enter_frameCount > 0:
                base_run = run_enter_name if run_enter_name else (name + "_run")
                for i in range(run_enter_frameCount):
                    self.anims['run_enter'].append(Transform("pics/weapons/%s%s.webp" % (base_run, i+1), xysize=(1280, 720)))
            
            self.ads_idle_img = Transform(ads_idle, xysize=(1280, 720)) if ads_idle else None
            self.ads_fire_static = Transform(ads_fire, xysize=(1280, 720)) if ads_fire else None
            
            # State: 'hip', 'entering_ads', 'ads'
            self.aim_state = 'hip'
            self.anim_state = 'idle' # 'idle', 'playing'
            
            self.flash_base = Transform(Image("pics/items/sight.png"), size=(512, 512))

        def play(self):
            if self.anim_state != 'playing':
                self.anim_state = 'playing'
                self.frame_index = 0
                self.oldst = None
                self.current_flash_rot = renpy.random.random() * math.pi * 2.0

        def render_to(self, r, width, height, st, at, is_ads=False, is_firing=False, movement_state=None):
            if self.oldst is None: self.oldst = st
            dt = st - self.oldst
            
            is_running = movement_state.get('is_running', False) if movement_state else False

            if is_firing:
                is_running = False
            
            if is_ads:
                if self.aim_state in ('entering_run', 'running', 'exiting_run'):
                    self.aim_state = 'hip'

                if self.aim_state == 'hip':
                    if self.anims['ads_enter']:
                        self.aim_state = 'entering_ads'
                        self.frame_index = 0
                        self.anim_state = 'idle'
                        self.oldst = st
                    else:
                        self.aim_state = 'ads'
            elif is_running and self.anims.get('run_enter'):
                if self.aim_state in ('hip', 'exiting_run'):
                    if self.aim_state == 'hip' and self.anim_state == 'playing':
                        pass
                    else:
                        self.aim_state = 'entering_run'
                        self.frame_index = 0
                        self.anim_state = 'idle'
                        self.oldst = st
                elif self.aim_state in ('ads', 'entering_ads'):
                    self.aim_state = 'hip'
            else:
                if is_firing and self.aim_state in ('running', 'entering_run', 'exiting_run'):
                    self.aim_state = 'hip'
                elif self.aim_state in ('running', 'entering_run'):
                    self.aim_state = 'exiting_run'
                    self.frame_index = 0
                    self.oldst = st

                if self.aim_state != 'hip' and self.aim_state != 'exiting_run':
                    self.aim_state = 'hip'

            current_img = None
            frame_duration = 0.1
            active_anim_list = []
            
            # Determine which animation list to use and frame duration
            if self.aim_state == 'entering_ads':
                active_anim_list = self.anims['ads_enter']
                frame_duration = 1.0 / self.fps['ads_enter']
                
                if dt >= frame_duration:
                    self.oldst = st
                    self.frame_index += 1
                    if self.frame_index >= len(active_anim_list):
                        self.aim_state = 'ads'
                        self.frame_index = 0
            
            if self.aim_state == 'entering_run':
                active_anim_list = self.anims['run_enter']
                frame_duration = 1.0 / self.fps['run_enter']
                
                if dt >= frame_duration:
                    self.oldst = st
                    self.frame_index += 1
                    if self.frame_index >= len(active_anim_list):
                        self.aim_state = 'running'
                        self.frame_index = len(active_anim_list) - 1
            
            if self.aim_state == 'exiting_run':
                active_anim_list = self.anims['run_enter']
                frame_duration = 1.0 / self.fps['run_enter']
                
                if dt >= frame_duration:
                    self.oldst = st
                    self.frame_index += 1
                    if self.frame_index >= len(active_anim_list):
                        self.aim_state = 'hip'
                        self.frame_index = 0
            
            if self.aim_state == 'hip':
                if self.anim_state == 'playing':
                    active_anim_list = self.anims['normal']
                    frame_duration = 1.0 / self.fps['normal']
                    
                    if dt >= frame_duration:
                        self.oldst = st
                        if self.loop_frames and is_firing:
                            if self.frame_index == self.loop_frames[-1]: self.frame_index = self.loop_frames[0]
                            else: self.frame_index += 1
                        else:
                            self.frame_index += 1
                        
                        if self.frame_index >= len(active_anim_list):
                            self.frame_index = 0
                            self.anim_state = 'idle'
                    
                    if active_anim_list:
                        safe_idx = min(self.frame_index, len(active_anim_list)-1)
                        current_img = active_anim_list[safe_idx]
                else:
                    if self.anims['normal']:
                        current_img = self.anims['normal'][0]
            
            elif self.aim_state == 'ads':
                if self.anim_state == 'playing':
                    active_anim_list = self.anims['ads_fire']
                    if active_anim_list:
                        frame_duration = 1.0 / self.fps['ads_fire']
                        if dt >= frame_duration:
                            self.oldst = st
                            self.frame_index += 1
                            if self.frame_index >= len(active_anim_list):
                                self.frame_index = 0
                                self.anim_state = 'idle'
                        
                        safe_idx = min(self.frame_index, len(active_anim_list)-1)
                        current_img = active_anim_list[safe_idx]
                    else:
                        current_img = self.ads_fire_static if (self.ads_fire_static and is_firing) else self.ads_idle_img
                else:
                    current_img = self.ads_idle_img
            
            elif self.aim_state == 'entering_ads':
                if active_anim_list:
                    safe_idx = min(self.frame_index, len(active_anim_list)-1)
                    current_img = active_anim_list[safe_idx]

            elif self.aim_state == 'entering_run':
                if active_anim_list:
                    safe_idx = min(self.frame_index, len(active_anim_list)-1)
                    current_img = active_anim_list[safe_idx]

            elif self.aim_state == 'exiting_run':
                run_list = self.anims['run_enter']
                if run_list:
                    rev_idx = len(run_list) - 1 - self.frame_index
                    safe_idx = max(0, min(rev_idx, len(run_list)-1))
                    current_img = run_list[safe_idx]
            
            elif self.aim_state == 'running':
                if self.anims['run_enter']:
                    current_img = self.anims['run_enter'][-1]

            # Render Weapon
            if current_img:
                eileen = renpy.render(current_img, 1280, 720, st, at)
                ew, eh = eileen.get_size()
                
                # Bobbing
                offset_x = 0; offset_y = 0
                if movement_state and movement_state.get('is_moving', False) and self.aim_state in ('hip', 'entering_run', 'running', 'exiting_run'):
                    bob_speed = 15.0 if movement_state.get('is_running', False) else 10.0
                    bob_amp_x = 50.0 if movement_state.get('is_running', False) else 20.0
                    offset_x = math.sin(st * bob_speed) * bob_amp_x
                    offset_y = abs(math.cos(st * bob_speed)) * (bob_amp_x / 2.0)
                
                if self.projectile_type and self.anim_state == 'playing':
                    should_flash = False
                    flash_config_key = 'normal'
                    
                    if self.aim_state == 'hip':
                        if self.frame_index == self.flash_config['frame_normal']:
                            should_flash = True
                            flash_config_key = 'normal'
                    elif self.aim_state == 'ads':
                        if self.frame_index == self.flash_config['frame_ads']:
                            should_flash = True
                            flash_config_key = 'ads'
                    
                    import time
                    time_diff = time.time() - self.last_fired
                    flash_dur = 0.06
                    
                    if should_flash or (time_diff < flash_dur): 
                        base_x = self.flash_config['offset_ads'][0] if (self.aim_state == 'ads') else self.flash_config['offset_normal'][0]
                        base_y = self.flash_config['offset_ads'][1] if (self.aim_state == 'ads') else self.flash_config['offset_normal'][1]
                        
                        fx = base_x + offset_x
                        fy = base_y + offset_y
                        
                        progress = time_diff / flash_dur
                        
                        f_t = Transform(
                            child=self.flash_base,
                            shader="stein.muzzle_flash",
                            u_flash_progress=progress,
                            u_flash_color=self.flash_config['color'],
                            u_flash_angle=self.current_flash_rot,
                            zoom=self.flash_config['size'],
                            additive=1.0
                        )
                        f_r = renpy.render(f_t, width, height, st, at)
                        fw, fh = f_r.get_size()
                        r.blit(f_r, (width/2 + fx - fw/2, height + fy - fh/2))

                r.blit(eileen, (width/2 - ew/2 + offset_x, height - eh + offset_y))

    class RaycastLayer(renpy.Displayable):
        def __init__(self, controller, **kwargs):
            super(RaycastLayer, self).__init__(**kwargs)
            self.c = controller
            # We use an Image instead of Solid to ensure a_tex_coord attributes are generated for the shader
            self.base_displayable = Transform(Image("pics/background.png"), size=(self.c.internal_width, self.c.internal_height))

        def render(self, width, height, st, at):
            c = self.c
            
            # Bobbing Logic
            bob_offset = 0.0
            
            fl_bob_x = 0.0
            fl_bob_y = 0.0
            
            is_moving = abs(c.player.speed) > 0.1 or abs(c.player.strafe_speed) > 0.1
            is_running = c.kb_running or c.gp_running
            effective_aiming = c.is_aiming or c.gp_aiming
            
            if is_moving and c.player.is_grounded and not effective_aiming:
                bob_speed = 10.0
                bob_amp = 0.01
                
                fl_amp_x = 0.05
                fl_amp_y = 0.03
                
                if is_running:
                    bob_speed = 15.0
                    bob_amp = 0.02
                    fl_amp_x = 0.08 
                    fl_amp_y = 0.05

                bob_offset = math.sin(st * bob_speed) * bob_amp
                
                fl_bob_x = math.sin(st * bob_speed) * fl_amp_x
                fl_bob_y = abs(math.cos(st * bob_speed)) * fl_amp_y

            sprite_data = []
            if hasattr(c, 'sprite_positions') and c.sprite_positions:
                for spr in c.sprite_positions:
                    sprite_data.append((spr[0], spr[1], float(spr[2]), 0.0))
            elif hasattr(renpy.store, 'stein_sprites'):
                for spr in renpy.store.stein_sprites:
                    sprite_data.append((spr[0], spr[1], float(spr[2]), 0.0))

            if hasattr(c, 'enemies'):
                for enemy in c.enemies:
                    sprite_data.append((enemy.x, enemy.y, float(enemy.texture_index), 0.0))
            
            if hasattr(c, 'projectiles'):
                for p in c.projectiles:
                    if getattr(p, 'is_invisible', False): continue
                    # Normalize pitch to match camera pitch logic (slope)
                    pitch = getattr(p, 'pitch', 0.0) / float(height)
                    sprite_data.append((p.x, p.y, float(p.texture_index), pitch))
            
            flash_intensity = 0.0
            
            import time 
            current_sys_time = time.time()
            
            current_weapon = c.weapons[c.player.current_weapon_name]
            
            time_since_shot = current_sys_time - current_weapon.last_fired
            
            if current_weapon.projectile_type and time_since_shot < 0.1:
                flash_intensity = 1.0 - (time_since_shot / 0.1)
                flash_intensity = max(0.0, min(1.0, flash_intensity))
            
            MAX_LIGHTS = 16
            lamp_id = 2.0 
            
            potential_lights = []
            if hasattr(c, 'sprite_positions'):
                for spr in c.sprite_positions:
                    if spr[2] == lamp_id: 
                        potential_lights.append((spr[0], spr[1]))
            
            def dist_sq_lights(pos): return (pos[0] - c.player.x)**2 + (pos[1] - c.player.y)**2
            potential_lights.sort(key=dist_sq_lights)
            
            final_lights_data = []
            for i in range(MAX_LIGHTS):
                if i < len(potential_lights):
                    lx, ly = potential_lights[i]
                    final_lights_data.append((lx, ly, 6.5, 1.8)) 
                else:
                    final_lights_data.append((0.0, 0.0, 0.0, 0.0))

            def get_dist_sq(s):
                return (s[0] - c.player.x)**2 + (s[1] - c.player.y)**2
            sprite_data.sort(key=get_dist_sq, reverse=True)

            MAX_SPRITES = 64
            num_active = len(sprite_data)
            if num_active > MAX_SPRITES:
                sprite_data = sprite_data[:MAX_SPRITES]
                num_active = MAX_SPRITES
            
            while len(sprite_data) < MAX_SPRITES:
                sprite_data.append((0.0, 0.0, 0.0, 0.0))

            child_render = renpy.render(self.base_displayable, width, height, st, at)
            child_render.add_shader("stein.raycaster")
            
            # ADS Zoom Logic
            is_aiming = c.is_aiming or c.gp_aiming
            zoom_factor = 0.6 if is_aiming else 1.0
            
            # Aspect Ratio Correction for 3D
            # Ensure square voxels by matching Vertical FOV to Horizontal FOV
            aspect_ratio = float(width) / float(height)
            plane_len = math.sqrt(c.player.planex**2 + c.player.planey**2)
            if plane_len == 0: plane_len = 0.66 # Fallback
            
            # vertical_scale = (Aspect / Plane) * (1 / Zoom)
            # Higher scale = Narrower Vertical FOV
            vertical_scale = (aspect_ratio / plane_len) / zoom_factor
            
            # Apply zoom to plane
            plane_x = c.player.planex * zoom_factor
            plane_y = c.player.planey * zoom_factor

            child_render.add_uniform('u_resolution', (float(width), float(height)))
            child_render.add_uniform('u_time', st)
            child_render.add_uniform('u_player_pos', (c.player.x, c.player.y))
            child_render.add_uniform('u_player_dir', (c.player.dirx, c.player.diry))
            child_render.add_uniform('u_player_plane', (plane_x, plane_y))
            
            # Head Bobbing applied to pitch
            child_render.add_uniform('u_pitch', (c.player.pitch / float(height)) + bob_offset)
            child_render.add_uniform('u_z_offset', c.player.z)
            child_render.add_uniform('u_vertical_scale', vertical_scale)
            child_render.add_uniform('u_sky_texture', c.sky_texture)

            child_render.add_uniform('u_map_size', (float(c.map_w), float(c.map_h)))
            child_render.add_uniform('u_map_uv_scale', c.map_uv_scale)
            child_render.add_uniform('u_map_texture', c.map_texture)
            
            child_render.add_uniform('u_wall_atlas', c.wall_atlas)
            child_render.add_uniform('u_floor_texture', c.floor_texture)
            child_render.add_uniform('u_num_textures', c.num_textures)
            
            child_render.add_uniform('u_sprite_atlas', c.sprite_atlas)
            child_render.add_uniform('u_num_sprite_textures', c.num_sprite_textures)
            child_render.add_uniform('u_sprites', sprite_data)
            child_render.add_uniform('u_num_active_sprites', num_active)

            child_render.add_uniform('u_flash_intensity', flash_intensity)
            child_render.add_uniform('u_flashlight_active', 1.0 if c.flashlight_on else 0.0)
            
            child_render.add_uniform('u_flashlight_bob', (fl_bob_x, fl_bob_y))
            
            child_render.add_uniform('u_light_positions', final_lights_data)
            child_render.add_uniform('u_num_active_lights', float(min(len(potential_lights), MAX_LIGHTS)))

            renpy.redraw(self, 0.01)
            return child_render

    class GPURenpystein(renpy.Displayable):
        def __init__(self, width, height, worldMap, exits=[], internal_width=None, internal_height=None, **kwargs):
            super(GPURenpystein, self).__init__(**kwargs)
            self.width = width
            self.height = height
            self.map_data = worldMap
            self.worldMap = worldMap 
            self.mapWidth = len(worldMap)
            self.mapHeight = len(worldMap[0]) if self.mapWidth > 0 else 0
            self.map_w = self.mapWidth
            self.map_h = self.mapHeight
            
            self.fps_frame_count = 0
            self.fps_timer_accum = 0.0

            self.exits = exits
            
            self.is_arena_mode = getattr(renpy.store, 'is_arena_mode', False)
            self.internal_width = internal_width if internal_width is not None else width
            self.internal_height = internal_height if internal_height is not None else height
            self.damage_flash_timer = 0.0
            self.return_value = None
            self.heal_flash_timer = 0.0
            self.hit_marker_timer = 0.0
            self.damage_indicators = []
            
            self.pickup_msg = ""
            self.pickup_msg_timer = 0.0
            
            self.map_texture = self.create_map_texture()
            self.wall_atlas, self.num_textures = self.create_wall_atlas()
            self.floor_texture = self.load_floor_texture()
            self.sprite_atlas, self.num_sprite_textures = self.create_sprite_atlas()
            self.solid_base = renpy.display.imagelike.Solid("#000", xsize=width, ysize=height)
            
            with renpy.open_file("pics/background.png") as f:
                bg_surf = pygame.image.load(f).convert_alpha()
            bg_surf = pygame.transform.scale(bg_surf, (width, height))
            self.sky_texture = renpy.display.draw.load_texture(bg_surf)

            self.player = Player(self, renpy.store.player_x, renpy.store.player_y, renpy.store.player_dirx, renpy.store.player_diry, renpy.store.player_planex, renpy.store.player_planey)
            
            self.oldst = None
            self.last_rot = None
            self.active_fingers = {}
            self.mouse_initialized = False
            
            # Inputs
            self.kb_speed = 0.0
            self.kb_strafe = 0.0
            self.kb_dir = 0.0
            self.gp_speed = 0.0
            self.gp_strafe = 0.0
            self.gp_dir = 0.0
            self.touch_speed = 0.0
            self.touch_strafe = 0.0
            self.touch_dir = 0.0
            
            self.is_aiming = False
            self.gp_aiming = False
            self.gp_firing = False
            self.mouse_firing = False
            self.gp_running = False
            self.kb_running = False
            
            self.flashlight_on = False 
            self.prev_btn_flashlight = False
            
            self.raycast_layer = RaycastLayer(self)
            
            pygame.joystick.init()
            self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
            for joy in self.joysticks:
                joy.init()

            self.gun_dmg = 50; self.shotgun_dmg = 35; self.minigun_dmg = 40
            if self.is_arena_mode:
                self.gun_dmg += 50 * (persistent.stein_pistol_level * 0.01)
                self.shotgun_dmg += 35 * (persistent.stein_shotgun_level * 0.01)
                self.minigun_dmg += 3 * (persistent.stein_minigun_level * 0.10)

            self.weapon_library = {}
            
            def register_weapon(w_obj):
                self.weapon_library[w_obj.name] = w_obj

            ### example of new guns registrations

            # register_weapon(Weapon("gun", SLOT_HANDGUN, damage=self.gun_dmg, projectile_type='bullet', cooldown=0.38, flash_offset=(0, -170), flash_ads_offset=(0, -360), flash_size=1.0, ads_idle="pics/weapons/gun_ads1.webp",
            #     # Normal configs
            #     normal_frameCount=11,
            #     normal_fps=60,
            #     normal_flash_frame=2,
            
            #     # ADS transition
            #     ads_enter_frameCount=14,
            #     ads_enter_fps=60,
            #     ads_enter_name="gun_raise",
        
            #     # ADS shooting animation
            #     ads_fire_frameCount=9,
            #     ads_fire_fps=60,
            #     ads_fire_flash_frame=1,
            # ))

            register_weapon(Weapon("gun", SLOT_HANDGUN, damage=self.gun_dmg, projectile_type='bullet', cooldown=0.38, flash_offset=(0, -170), flash_ads_offset=(0, -360), flash_size=1.0, ads_idle="pics/weapons/gun_ads1.webp",
                # Normal configs
                normal_frameCount=11,
                normal_fps=60,
                normal_flash_frame=2,
            
                # ADS transition
                ads_enter_frameCount=14,
                ads_enter_fps=60,
                ads_enter_name="gun_raise",
        
                # ADS shooting animation
                ads_fire_frameCount=9,
                ads_fire_fps=60,
                ads_fire_flash_frame=1,
            ))

            register_weapon(Weapon("shotgun", SLOT_LONG, damage=self.shotgun_dmg, projectile_type='shotgun', cooldown=1.4, flash_offset=(0, -170), flash_ads_offset=(0, -340), flash_size=1.0, ads_idle="pics/weapons/shotgun_ads1.webp",
                # Normal configs
                normal_frameCount=39,
                normal_fps=60,
                normal_flash_frame=1,
            
                # ADS transition (normal-ads)
                ads_enter_frameCount=5,
                ads_enter_fps=60,
                ads_enter_name="shotgun_raised",
        
                # ADS shooting animation
                ads_fire_frameCount=45,
                ads_fire_fps=60,
                ads_fire_flash_frame=1,

                # Run enter (normal-running)
                run_enter_frameCount=5,
                run_enter_fps=60,
                run_enter_name="shotgun_run",
            ))

            register_weapon(Weapon("fist", SLOT_MELEE, 5, 1, damage=25, cooldown=0.5))

            # register_weapon(Weapon("gun", SLOT_HANDGUN, 5, 1, damage=self.gun_dmg, projectile_type='bullet', cooldown=0.6, 
            #     ads_idle="pics/weapons/beta_gun_s.png", ads_fire="pics/weapons/beta_gun_s_f.png", 
            #     flash_offset=(0, -170), flash_ads_offset=(0, -360), flash_size=1.0))

            # register_weapon(Weapon("shotgun", SLOT_LONG, 5, 1, damage=self.shotgun_dmg, projectile_type='shotgun', cooldown=1.0, 
            #     flash_offset=(0, -170), flash_ads_offset=(0, -170), flash_size=1.5, flash_color=(1.0, 0.6, 0.2)))
            
            register_weapon(Weapon("minigun", SLOT_SPECIAL, 5, 1, damage=self.minigun_dmg, projectile_type='bullet', cooldown=0.05, 
                loop_frames=[2, 3], flash_offset=(0, -180), flash_ads_offset=(0, -180)))
            
            self.inventory = [None, None, None, None] # [Melee, Handgun, Long, Special]
            
            self.weapons = self.weapon_library

            self.current_slot_index = SLOT_MELEE

            self.equip_weapon("fist")
            self.equip_weapon("gun")
            
            if renpy.store.stein_has_shotgun:
                self.equip_weapon("shotgun")
            
            if renpy.store.stein_has_minigun:
                self.equip_weapon("minigun")

            self.current_slot_index = SLOT_HANDGUN
            self.update_current_weapon_ref()
            
            self.bullet_texture_index = 6
            self.sight_d = Image("pics/items/sight.png")
            with renpy.open_file("pics/gui/damage_x.png") as f:
                self.hit_marker_img = pygame.image.load(f).convert_alpha()
            with renpy.open_file("pics/gui/arrow_d.png") as f:
                arrow_surf = pygame.image.load(f).convert_alpha()
            self.arrow_img = pygame.transform.scale(arrow_surf, (30, 30))

            self.projectiles = []
            self.enemies = []
            self.sprite_positions = renpy.store.stein_sprites
            
            self.inter_round_timer = getattr(renpy.store, 'stein_inter_round_timer', 0.0)
            self.current_round = getattr(renpy.store, 'stein_current_round', 0)
            self.sniper_count = getattr(renpy.store, 'stein_sniper_count', 0)
            self.yuritler_count = getattr(renpy.store, 'stein_yuritler_count', 0)
            self.spawn_points = getattr(renpy.store, 'arena_spawn_points', [])
            
            if hasattr(renpy.store, 'stein_enemies'):
                for e_data in renpy.store.stein_enemies:
                    x, y, tex, dead_tex = e_data[0], e_data[1], e_data[2], e_data[3]
                    health = e_data[4] if len(e_data) > 4 else 100
                    type_id = e_data[5] if len(e_data) > 5 else 0
                    
                    if type_id == 1: new_e = Yuritler(self, x, y, health=health)
                    elif type_id == 2: new_e = EliteGuard(self, x, y, health=health)
                    elif type_id == 3: new_e = Sniper(self, x, y, health=health)
                    else: new_e = Guard(self, x, y, tex, dead_tex, health=health)
                    
                    self.enemies.append(new_e)

            if self.is_arena_mode and self.current_round == 0:
                self.start_next_round()

        def equip_weapon(self, weapon_name):
            if weapon_name in self.weapon_library:
                w_obj = self.weapon_library[weapon_name]
                self.inventory[w_obj.category] = w_obj
                if self.inventory[self.current_slot_index] == w_obj:
                    self.update_current_weapon_ref()

        def update_current_weapon_ref(self):
            weapon = self.inventory[self.current_slot_index]
            if weapon:
                self.player.current_weapon_name = weapon.name
            else:
                self.current_slot_index = SLOT_MELEE
                self.player.current_weapon_name = self.inventory[SLOT_MELEE].name

        def switch_to_slot(self, slot_idx):
            if 0 <= slot_idx < 4:
                if self.inventory[slot_idx] is not None:
                    self.current_slot_index = slot_idx
                    self.update_current_weapon_ref()

        def cycle_weapon(self):
            start_idx = self.current_slot_index
            for i in range(1, 4):
                next_idx = (start_idx + i) % 4
                if self.inventory[next_idx] is not None:
                    self.switch_to_slot(next_idx)
                    return

        def start_next_round(self):
            self.current_round += 1
            # renpy.sound.play("sounds/music/round_start.ogg", channel="audio")
            
            # Clean up bodies
            # Original uses: [s for s in self.sprite_positions if s[2] != 5] (Guard dead texture is 5)
            # Guard/Elite/Sniper dead: 5. Yuritler dead: 10
            self.sprite_positions = [s for s in self.sprite_positions if s[2] not in (5, 10)]
            
            if not self.spawn_points:
                self.spawn_points = [(1.5, 1.5), (self.mapWidth-1.5, 1.5), (self.mapWidth/2.0, self.mapHeight/2.0)]

            # Spawn Standard Guards
            for _ in range(self.current_round):
                if not self.spawn_points: break
                sx, sy = renpy.random.choice(self.spawn_points)
                
                x = sx + 0.5 + (renpy.random.random() - 0.5) * 0.6
                y = sy + 0.5 + (renpy.random.random() - 0.5) * 0.6
                
                new_enemy = Guard(self, x, y, 4, 5, health=100)
                new_enemy.state = 'chasing'
                new_enemy.moveSpeed += (renpy.random.random() - 0.5) * 0.2
                self.enemies.append(new_enemy)

            # Spawn Yuritler
            spawn_yuritler = False
            if self.current_round % 10 == 0:
                spawn_yuritler = True
            elif self.current_round % 2 == 0:
                if renpy.random.random() < 0.15:
                    spawn_yuritler = True
            
            if spawn_yuritler:
                if self.spawn_points:
                    self.yuritler_count += 1
                    sx, sy = renpy.random.choice(self.spawn_points)
                    x = sx + 0.5 + (renpy.random.random() - 0.5) * 0.6
                    y = sy + 0.5 + (renpy.random.random() - 0.5) * 0.6
                    
                    boss_hp = 150 + ((self.yuritler_count - 1) * 50)
                    boss = Yuritler(self, x, y, health=boss_hp)
                    boss.state = 'chasing'
                    self.enemies.append(boss)

            # pawn Elite Guards (Every 5 Rounds)
            if self.current_round % 5 == 0:
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

            # Spawn Snipers (Odd Rounds, 50% chance)
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
            
            self.inter_round_timer = 0.0

        def create_wall_atlas(self):
            image_paths = [  
                "pics/walls/eagle.png", "pics/walls/redbrick.png",
                "pics/walls/purplestone.png", "pics/walls/greystone.png",
                "pics/walls/bluestone.png", "pics/walls/mossy.png",
                "pics/walls/wood.png", "pics/walls/colorstone.png",
                "pics/walls/cement.png",
            ]
            
            surfaces = []
            for path in image_paths:
                with renpy.open_file(path) as f:
                    surf = pygame.image.load(f).convert_alpha()
                    surf = pygame.transform.scale(surf, (64, 64))
                    surfaces.append(surf)
            
            if not surfaces:
                # fallback por si acaso
                fallback = pygame.Surface((64, 64)); fallback.fill((255,0,255))
                return renpy.display.draw.load_texture(fallback), 1.0

            num_tex = len(surfaces)
            w, h = surfaces[0].get_size()
            atlas_w = w * num_tex
            atlas_h = h
            
            # Atlas surface (RGBA 32bit)
            atlas = pygame.Surface((atlas_w, atlas_h), flags=pygame.SRCALPHA, depth=32)
            
            # DEBUG
            atlas.fill((255, 255, 255, 255))
            
            for i, surf in enumerate(surfaces):
                atlas.blit(surf, (i * w, 0))
            
            print(f"RenPyStein GPU: Wall Atlas Created. Size: {atlas_w}x{atlas_h}. Textures: {num_tex}")
            return renpy.display.draw.load_texture(atlas), float(num_tex)

        def load_floor_texture(self):
            try:
                with renpy.open_file("pics/walls/cement.png") as f:
                    surf = pygame.image.load(f).convert_alpha()
                    surf = pygame.transform.scale(surf, (64, 64))
                    return renpy.display.draw.load_texture(surf)
            except:
                fallback = pygame.Surface((64, 64))
                fallback.fill((100, 100, 100))
                return renpy.display.draw.load_texture(fallback)

        def create_sprite_atlas(self):
            sprite_paths = [  
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
                "pics/items/coins.png", 
                "pics/items/random_gun_i.png",
                "pics/items/bullet_red.png",
                "pics/items/minigun.png",
            ]
            
            surfaces = []
            for path in sprite_paths:
                with renpy.open_file(path) as f:
                    surf = pygame.image.load(f).convert_alpha()
                    surf = pygame.transform.scale(surf, (64, 64))
                    surfaces.append(surf)
            
            if not surfaces:
                fallback = pygame.Surface((64, 64)); fallback.fill((0,255,0))
                return renpy.display.draw.load_texture(fallback), 1.0

            num_tex = len(surfaces)
            w, h = surfaces[0].get_size()
            atlas_w = w * num_tex
            atlas_h = h
            
            atlas = pygame.Surface((atlas_w, atlas_h), flags=pygame.SRCALPHA, depth=32)
            atlas.fill((0,0,0,0))
            
            for i, surf in enumerate(surfaces):
                atlas.blit(surf, (i * w, 0))
            
            print(f"RenPyStein GPU: Sprite Atlas Created. Size: {atlas_w}x{atlas_h}. Textures: {num_tex}")
            return renpy.display.draw.load_texture(atlas), float(num_tex)

        def create_map_texture(self):
            def next_power_of_two(n):
                if n == 0: return 1
                return 2**math.ceil(math.log(n, 2))
            
            x_len = len(self.map_data)
            y_len = len(self.map_data[0]) if x_len > 0 else 0
            w_pot = max(64, next_power_of_two(x_len))
            h_pot = max(64, next_power_of_two(y_len))

            surf = pygame.Surface((w_pot, h_pot), flags=pygame.SRCALPHA, depth=32)
            surf.fill((0,0,0,255))
            
            for map_x, row in enumerate(self.map_data):
                for map_y, tile in enumerate(row):
                    if tile > 0:
                        surf.set_at((map_x, map_y), (255, tile, 0, 255))
                    else:
                        surf.set_at((map_x, map_y), (0, 0, 0, 255))
            
            tex = renpy.display.draw.load_texture(surf)
            self.map_uv_scale = (float(x_len) / float(w_pot), float(y_len) / float(h_pot))
            return tex

        def render(self, width, height, st, at):
            if self.oldst is None: self.oldst = st
            dtime = st - self.oldst
            self.oldst = st

            self.fps_frame_count += 1
            self.fps_timer_accum += dtime
            
            if self.fps_timer_accum >= 0.5:
                current_fps = int(self.fps_frame_count / self.fps_timer_accum)
                renpy.store.stein_current_fps = current_fps
                self.fps_frame_count = 0
                self.fps_timer_accum = 0.0

            if simulate_touch: self.update_player_from_touch_state()
            else: self.touch_speed = 0.0; self.touch_strafe = 0.0; self.touch_dir = 0.0
            self.poll_gamepad()

            total_speed = self.kb_speed + self.gp_speed + self.touch_speed
            total_strafe = self.kb_strafe + self.gp_strafe + self.touch_strafe
            total_dir = self.kb_dir + self.gp_dir + self.touch_dir
            
            effective_aiming = self.is_aiming or self.gp_aiming
            is_running = self.kb_running or self.gp_running
            if effective_aiming: is_running = False
            
            if is_running: self.player.moveSpeed = 4.0 
            elif effective_aiming: self.player.moveSpeed = 1.5 
            else: self.player.moveSpeed = 2.5 

            self.player.speed = max(-1.0, min(1.0, total_speed))
            self.player.strafe_speed = max(-1.0, min(1.0, total_strafe))
            self.player.dir = total_dir 
            self.player.move(dtime)
            
            self.update_logic(dtime)

            renpy.store.player_x = self.player.x
            renpy.store.player_y = self.player.y
            renpy.store.player_dirx = self.player.dirx
            renpy.store.player_diry = self.player.diry
            renpy.store.player_planex = self.player.planex
            renpy.store.player_planey = self.player.planey

            # RENDER
            retro_w = self.internal_width
            retro_h = self.internal_height
            
            # Motion Blur Calculation
            if self.last_rot is None: self.last_rot = self.player.rot
            rot_diff = self.player.rot - self.last_rot
            if rot_diff > math.pi: rot_diff -= 2 * math.pi
            elif rot_diff < -math.pi: rot_diff += 2 * math.pi
            self.last_rot = self.player.rot
            
            blur_strength = getattr(persistent, "stein_motion_blur_strength", 0.0)
            blur_amount = 0.0
            
            if blur_strength > 0.0:
                blur_amount = max(-0.15, min(0.15, rot_diff)) * blur_strength * 20.0

            scale = float(width) / float(retro_w)
            
            # Flatten the raycast layer to ensure the 3D shader is baked before applying motion blur
            flat_layer = renpy.display.layout.Flatten(self.raycast_layer)
            
            t_args = {
                'child': flat_layer,
                'zoom': scale,
                'nearest': True
            }
            
            if abs(blur_amount) > 0.005:
                t_args['shader'] = "stein.motion_blur"
                t_args['u_blur_amount'] = blur_amount

            t = Transform(**t_args)
            
            main_scene_render = renpy.render(t, width, height, st, at)
            
            r = renpy.Render(width, height)
            r.blit(main_scene_render, (0,0))
            
            # Damage flash + Low Health Tint
            if self.damage_flash_timer > 0:
                self.damage_flash_timer = max(0, self.damage_flash_timer - dtime)

            flash_alpha = 0
            if self.damage_flash_timer > 0:
                flash_alpha = int(140 * (self.damage_flash_timer / 0.2))
            
            health_alpha = 0
            if self.player.health < 70:
                severity = (70.0 - self.player.health) / 70.0
                health_alpha = int(severity * 160)
            
            final_red_alpha = min(255, max(flash_alpha, health_alpha))

            if final_red_alpha > 0:
                flash_d = renpy.display.imagelike.Solid((255, 0, 0, final_red_alpha))
                flash_r = renpy.render(flash_d, width, height, st, at)
                r.blit(flash_r, (0,0))

            if self.heal_flash_timer > 0:
                self.heal_flash_timer = max(0, self.heal_flash_timer - dtime)
                alpha = int(128 * (self.heal_flash_timer / 0.2))
                if alpha > 0:
                    heal_d = renpy.display.imagelike.Solid((0, 255, 0, alpha))
                    heal_r = renpy.render(heal_d, width, height, st, at)
                    r.blit(heal_r, (0,0))

            # Crosshair
            sight_r = renpy.render(self.sight_d, width, height, st, at)
            sw, sh = sight_r.get_size()
            r.blit(sight_r, (width/2 - sw/2, height/2 - sh/2))
            
            # Hit Marker
            if self.hit_marker_timer > 0:
                hm_w, hm_h = self.hit_marker_img.get_size()
                hm_tex = renpy.display.draw.load_texture(self.hit_marker_img)
                r.blit(hm_tex, (width/2 - hm_w/2, height/2 - hm_h/2))

            if self.pickup_msg_timer > 0:
                self.pickup_msg_timer -= dtime 
                
                alpha_val = 255
                if self.pickup_msg_timer < 0.5:
                    alpha_val = int(255 * (self.pickup_msg_timer / 0.5))
                
                if alpha_val > 0:
                    pickup_text = Text(self.pickup_msg, size=40, color="#FFFF00", outlines=[(3, "#000", 0, 0)])
                    pt_render = renpy.render(pickup_text, width, height, st, at)
                    pw, ph = pt_render.get_size()
                    
                    r.blit(pt_render, (width/2 - pw/2, height * 0.20))

            # hp_color = "#FFF"
            # if self.player.health < 30: hp_color = "#F00"
            # elif self.player.health < 60: hp_color = "#FF0"
            
            # hud_text = Text(_("HP: {}%  |  WEAPON: {}").format(int(self.player.health), self.player.current_weapon_name.upper()), size=36, color=hp_color, outlines=[(2, "#000", 0, 0)])
            # hud_r = renpy.render(hud_text, width, height, st, at)
            # r.blit(hud_r, (30, height - 60))

            if self.is_arena_mode:
                arena_text = Text(_("ROUND: {}  |  KILLS: {}  |  COINS: {}").format(self.current_round, persistent.stein_kills, renpy.store.stein_session_coins), size=28, color="#FFD700", outlines=[(2, "#000", 0, 0)])
                arena_r = renpy.render(arena_text, width, height, st, at)
                aw, ah = arena_r.get_size()
                r.blit(arena_r, (width - aw - 30, height - 60))
                
                # Next Round Timer
                if self.inter_round_timer > 0 and self.current_round > 0:
                    timer_text = Text(_("NEXT ROUND IN: {:.1f}").format(self.inter_round_timer), size=48, color="#F00", outlines=[(2, "#000", 0, 0)])
                    timer_r = renpy.render(timer_text, width, height, st, at)
                    tw, th = timer_r.get_size()
                    r.blit(timer_r, (width/2 - tw/2, 100))

            # Damage indicators
            center_x = width / 2; center_y = height / 2; indicator_radius = 200
            for ind in list(self.damage_indicators):
                ind.duration -= dtime
                if ind.duration <= 0: self.damage_indicators.remove(ind); continue
                diff = self.player.rot - ind.angle
                ix = center_x + indicator_radius * math.sin(diff)
                iy = center_y - indicator_radius * math.cos(diff)
                rot_img = pygame.transform.rotate(self.arrow_img, -math.degrees(diff))
                rot_img.set_alpha(int(255 * (ind.duration / ind.max_duration)))
                ind_tex = renpy.display.draw.load_texture(rot_img)
                iw, ih = ind_tex.get_size()
                r.blit(ind_tex, (ix - iw/2, iy - ih/2))

            # Game over checks
            if self.player.health <= 0:
                self.player.health = 0
                pygame.mouse.set_visible(True); pygame.event.set_grab(False)
                if self.return_value is None:
                    if self.is_arena_mode:
                        renpy.store.last_arena_round = self.current_round
                        renpy.store.new_highscore = False
                        if self.current_round > persistent.sayoristein_arena_highscore:
                            persistent.sayoristein_arena_highscore = self.current_round
                            renpy.store.new_highscore = True
                        self.return_value = 'game_over_arena'
                    else:
                        self.return_value = 'game_over'

            for e in self.exits:
                if math.fabs(e[0] - self.player.x) < 0.5 and math.fabs(e[1] - self.player.y) < 0.5:
                    pygame.mouse.set_visible(True); pygame.event.set_grab(False)
                    if self.return_value is None:
                        self.return_value = e[2]

            # Weapon
            movement_state = {
                'is_moving': abs(self.player.speed) > 0.1 or abs(self.player.strafe_speed) > 0.1, 
                'is_running': self.kb_running or self.gp_running
            }
            is_firing = self.mouse_firing or self.gp_firing
            current_weapon_obj = self.weapons[self.player.current_weapon_name]
            current_weapon_obj.render_to(r, width, height, st, at, is_ads=self.is_aiming or self.gp_aiming, is_firing=is_firing, movement_state=movement_state)
            
            if self.return_value:
                renpy.timeout(0)

            renpy.redraw(self, 0.01) 
            return r

        def update_logic(self, dt):
            self.hit_marker_timer = max(0, self.hit_marker_timer - dt)
            self.check_item_pickup()
            for enemy in self.enemies: enemy.update(dt, self.player)
            for p in list(self.projectiles):
                if not p.update(dt): self.projectiles.remove(p)
            if self.mouse_firing or self.gp_firing: self.shoot_weapon()

            if self.is_arena_mode:
                if self.inter_round_timer > 0:
                    self.inter_round_timer -= dt
                    if self.inter_round_timer <= 0:
                        self.start_next_round()
                elif len(self.enemies) == 0 and self.current_round > 0:
                    self.inter_round_timer = 10.0

            renpy.store.stein_current_round = self.current_round
            renpy.store.stein_inter_round_timer = self.inter_round_timer
            renpy.store.stein_sniper_count = self.sniper_count
            renpy.store.stein_yuritler_count = self.yuritler_count

        def check_item_pickup(self):
            for sprite in list(self.sprite_positions):
                sprite_x, sprite_y, texture_index = sprite
                dist = math.sqrt((self.player.x - sprite_x)**2 + (self.player.y - sprite_y)**2)
                if dist < 0.8:
                    picked = False
                    if texture_index == 7 and self.player.health < 100:
                        self.player.health = min(100, self.player.health + 25); picked = True
                        self.heal_flash_timer = 0.2
                    elif texture_index in (11, 12):
                        renpy.store.stein_session_coins += 100; picked = True
                    elif texture_index == 13 and not renpy.store.stein_has_shotgun:
                        renpy.store.stein_has_shotgun = True; picked = True
                        self.pickup_msg = "SHOTGUN ACQUIRED"
                        self.pickup_msg_timer = 3.0
                    elif texture_index == 15 and not renpy.store.stein_has_minigun:
                        renpy.store.stein_has_minigun = True; picked = True
                        self.pickup_msg = "MINIGUN ACQUIRED"
                        self.pickup_msg_timer = 3.0
                    if picked: self.sprite_positions.remove(sprite)

        def shoot_weapon(self):
            weapon = self.weapons[self.player.current_weapon_name]
            if time.time() - weapon.last_fired < weapon.cooldown: return
            weapon.last_fired = time.time()
            weapon.play()
            
            dx = self.player.dirx
            dy = self.player.diry 
            pitch = self.player.pitch
            is_ads = self.is_aiming or self.gp_aiming
            
            bullet_invisible = True 

            if weapon.projectile_type == 'shotgun':
                import random
                spread_mult = 0.1 if is_ads else 0.2
                for _ in range(5):
                    spread = (random.random() - 0.5) * spread_mult
                    angle = self.player.rot + spread
                    pdx = math.cos(angle)
                    pdy = math.sin(angle)
                    self.projectiles.append(Projectile(self, self.player.x, self.player.y, pdx, pdy, self.bullet_texture_index, weapon.damage, fired_by_player=True, pitch=pitch, is_invisible=bullet_invisible))
                renpy.sound.play("sounds/shotgun.ogg", channel="audio")
            elif weapon.projectile_type == 'bullet':
                self.projectiles.append(Projectile(self, self.player.x, self.player.y, dx, dy, self.bullet_texture_index, weapon.damage, fired_by_player=True, pitch=pitch, is_invisible=bullet_invisible))
                renpy.sound.play("sounds/gunshot.ogg", channel="audio")
            else:
                hit = False
                # Sort enemies to hit the closest one first
                self.enemies.sort(key=lambda e: (e.x - self.player.x)**2 + (e.y - self.player.y)**2)
                
                for e in list(self.enemies):
                    dist = math.sqrt((e.x - self.player.x)**2 + (e.y - self.player.y)**2)
                    if dist < 1.5: 
                        taken = True
                        if hasattr(e, 'take_damage'):
                            taken = e.take_damage(weapon.damage)
                        else:
                            e.health -= weapon.damage

                        if taken:
                            hit = True
                            self.hit_marker_timer = 0.15
                            
                            if e.health <= 0:
                                renpy.sound.play("sounds/ow.ogg", channel="audio")
                                if self.is_arena_mode:
                                    persistent.stein_kills += 1
                                
                                if e in self.enemies:
                                    self.enemies.remove(e)
                                
                                self.sprite_positions.append((e.x, e.y, e.destroyed_texture_index))
                                
                                # Drop Medkit (40%)
                                if renpy.random.random() < 0.40:
                                    self.sprite_positions.append((e.x, e.y, 7))
                                
                                # Arena Mode Drops
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
                            
                            break

                if hit and not any(e.health <= 0 for e in self.enemies): 
                    pass

        def add_damage_indicator(self, source_dir_x, source_dir_y):
            angle = math.atan2(source_dir_y, source_dir_x)
            self.damage_indicators.append(DamageIndicator(angle))

        def isBlocking(self, x, y):
            if x < 0 or x >= self.mapWidth or y < 0 or y >= self.mapHeight: return True
            return self.worldMap[int(x)][int(y)] != 0

        def checkCollision(self, fromX, fromY, toX, toY, radius):
            pos = [fromX, fromY]
            if toY < 0 or toY >= self.mapHeight or toX < 0 or toX >= self.mapWidth: return pos
            blockX = math.floor(toX); blockY = math.floor(toY)
            if self.isBlocking(blockX, blockY): return pos
            pos[0] = toX; pos[1] = toY
            return pos

        # EVENT HANDLING
        def event(self, ev, x, y, st):
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_LCTRL or ev.key == pygame.K_RCTRL:
                    self.kb_running = True
                    raise renpy.IgnoreEvent()
            
            if ev.type == pygame.KEYUP:
                if ev.key == pygame.K_LCTRL or ev.key == pygame.K_RCTRL:
                    self.kb_running = False
                    raise renpy.IgnoreEvent()

            if self.return_value:
                return self.return_value

            global simulate_touch
            if not self.mouse_initialized and not simulate_touch:
                pygame.mouse.set_visible(False); pygame.event.set_grab(True); self.mouse_initialized = True
            if simulate_touch:
                if ev.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP): self.handle_multitouch_events(ev)
                elif ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP): self.handle_mouse_simulation(ev, x, y)
            else: self.handle_pc_input(ev)
            if ev.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP, pygame.JOYHATMOTION, pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED): self.handle_gamepad_input(ev)
            renpy.retain_after_load()

        def handle_multitouch_events(self, ev):
            LOOK_THRESHOLD_X = 0.5; finger_id = ev.finger_id; event_x = ev.x * self.width; event_y = ev.y * self.height
            if ev.type == pygame.FINGERDOWN:
                action = None
                if ev.x <= LOOK_THRESHOLD_X: action = 'move'
                elif ev.x > LOOK_THRESHOLD_X: action = 'look'
                if action: self.active_fingers[finger_id] = {'action': action, 'start_pos': (event_x, event_y), 'current_pos': (event_x, event_y), 'dx_accum': 0.0}
            elif ev.type == pygame.FINGERMOTION:
                if finger_id in self.active_fingers:
                    info = self.active_fingers[finger_id]
                    if info['action'] == 'move': info['current_pos'] = (event_x, event_y)
                    elif info['action'] == 'look': info['dx_accum'] += ev.dx * self.width
            elif ev.type == pygame.FINGERUP:
                if finger_id in self.active_fingers: del self.active_fingers[finger_id]

        def update_player_from_touch_state(self):
            self.touch_speed = 0.0; self.touch_strafe = 0.0; self.touch_dir = 0.0
            for finger_id, info in list(self.active_fingers.items()):
                if info['action'] == 'move':
                    dx = info['current_pos'][0] - info['start_pos'][0]; dy = info['current_pos'][1] - info['start_pos'][1]
                    self.touch_speed += -dy / 80.0; self.touch_strafe += dx / 80.0
                elif info['action'] == 'look':
                    self.touch_dir += (info['dx_accum'] / self.width) * 25.0; info['dx_accum'] = 0.0

        def handle_mouse_simulation(self, ev, x, y):
            LOOK_THRESHOLD_PIXELS = self.width * 0.5; button_id = getattr(ev, 'button', None)
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if button_id == 1 and x > LOOK_THRESHOLD_PIXELS: self.active_fingers[1] = {'action': 'look', 'dx_accum': 0.0}
                elif button_id == 3 and x <= LOOK_THRESHOLD_PIXELS: self.active_fingers[3] = {'action': 'move', 'start_pos':(x,y), 'current_pos':(x,y)}
            elif ev.type == pygame.MOUSEMOTION:
                if ev.buttons[0] and 1 in self.active_fingers: self.active_fingers[1]['dx_accum'] += ev.rel[0]
                if ev.buttons[2] and 3 in self.active_fingers: self.active_fingers[3]['current_pos'] = (x, y)
            elif ev.type == pygame.MOUSEBUTTONUP:
                if button_id in self.active_fingers: del self.active_fingers[button_id]

        def handle_pc_input(self, ev):
            # Handle mouse look
            if ev.type == pygame.MOUSEMOTION:
                base_sens = 0.003
                base_pitch = 0.8
                
                sensitivity = base_sens * persistent.stein_mouse_sens
                pitch_sensitivity = base_pitch * persistent.stein_mouse_sens

                if self.is_aiming:
                    sensitivity *= 0.25
                    pitch_sensitivity *= 0.5

                self.player.rot -= ev.rel[0] * sensitivity
                self.player.planerot -= ev.rel[0] * sensitivity
                
                # Pitch (vertical look)
                self.player.pitch -= ev.rel[1] * pitch_sensitivity
                self.player.pitch = max(-1000.0, min(1000.0, self.player.pitch))

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    self.mouse_initialized = False
                    return

                if ev.key == pygame.K_1: self.switch_to_slot(SLOT_MELEE)
                if ev.key == pygame.K_2: self.switch_to_slot(SLOT_HANDGUN)
                if ev.key == pygame.K_3: self.switch_to_slot(SLOT_LONG)
                if ev.key == pygame.K_4: self.switch_to_slot(SLOT_SPECIAL)

                if ev.key == pygame.K_f:
                    self.flashlight_on = not self.flashlight_on

                if ev.key == pygame.K_w: self.kb_speed = 1.0
                if ev.key == pygame.K_s: self.kb_speed = -1.0
                if ev.key == pygame.K_a: self.kb_strafe = -1.0
                if ev.key == pygame.K_d: self.kb_strafe = 1.0
                
                # Arrow key controls
                if ev.key == pygame.K_UP: self.kb_speed = 1.0
                if ev.key == pygame.K_DOWN: self.kb_speed = -1.0
                if ev.key == pygame.K_LEFT: self.kb_dir = 1.0
                if ev.key == pygame.K_RIGHT: self.kb_dir = -1.0
                
                if ev.key == pygame.K_SPACE: self.player.trigger_jump()
                
                if ev.key == pygame.K_LCTRL or ev.key == pygame.K_RCTRL:
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
                if ev.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN): self.kb_speed = 0.0
                if ev.key in (pygame.K_a, pygame.K_d): self.kb_strafe = 0.0
                if ev.key in (pygame.K_LEFT, pygame.K_RIGHT): self.kb_dir = 0.0
                if ev.key in (pygame.K_LCTRL, pygame.K_RCTRL): self.kb_running = False

        def poll_gamepad(self):
            self.gp_speed = 0.0; self.gp_strafe = 0.0; self.gp_dir = 0.0
            self.gp_aiming = False; self.gp_firing = False; self.gp_running = False
            DEADZONE = 0.25; TRIGGER_THRESHOLD = 0.6 
            is_switch_held = False

            for joy in self.joysticks:
                try:
                    if not joy.get_init(): continue
                    name = joy.get_name().lower()
                    if "accelerometer" in name or "gyro" in name: continue
                    
                    if joy.get_numaxes() > 4 and joy.get_axis(4) > TRIGGER_THRESHOLD: self.gp_aiming = True
                    if joy.get_numbuttons() > 4 and joy.get_button(4): self.gp_running = True

                    if joy.get_numaxes() > 0:
                        x = joy.get_axis(0)
                        if abs(x) > DEADZONE: self.gp_strafe += x 
                    if joy.get_numaxes() > 1:
                        y = joy.get_axis(1)
                        if abs(y) > DEADZONE: self.gp_speed -= y 
                    if joy.get_numaxes() > 2:
                        rx = joy.get_axis(2)
                        if abs(rx) > DEADZONE:
                            sens = 2.5 * persistent.stein_gamepad_sens_x
                            if self.is_aiming or self.gp_aiming: sens *= 0.25
                            self.gp_dir -= rx * sens
                    if joy.get_numaxes() > 3:
                        ry = joy.get_axis(3)
                        if abs(ry) > DEADZONE:
                            p_speed = 19.0 * persistent.stein_gamepad_sens_y
                            if self.is_aiming or self.gp_aiming: p_speed *= 0.5
                            self.player.pitch -= ry * p_speed
                            self.player.pitch = max(-1000.0, min(1000.0, self.player.pitch))

                    if joy.get_numaxes() > 5 and joy.get_axis(5) > TRIGGER_THRESHOLD: self.gp_firing = True
                    if joy.get_numbuttons() > 5 and joy.get_button(5): self.gp_firing = True
                    if joy.get_numbuttons() > 0 and joy.get_button(0): self.player.trigger_jump()
                    if joy.get_numbuttons() > 3 and joy.get_button(3): is_switch_held = True

                    btn_flashlight_held = False

                    if joy.get_numhats() > 0:
                        hat_x, hat_y = joy.get_hat(0)
                        if hat_y == 1: 
                            btn_flashlight_held = True
                    
                    if btn_flashlight_held and not self.prev_btn_flashlight:
                        self.flashlight_on = not self.flashlight_on
                    
                    self.prev_btn_flashlight = btn_flashlight_held

                except pygame.error: continue
            
            if is_switch_held and not getattr(self, 'prev_btn_weapon_switch', False):
                self.cycle_weapon()
            
            self.prev_btn_weapon_switch = is_switch_held

        def handle_gamepad_input(self, ev):
            if ev.type == pygame.JOYDEVICEADDED or ev.type == pygame.JOYDEVICEREMOVED:
                pygame.joystick.quit()
                pygame.joystick.init()
                self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
                for joy in self.joysticks: 
                    try: joy.init()
                    except: pass
