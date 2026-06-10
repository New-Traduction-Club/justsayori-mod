# TODO:
######## Android

# if a xbox gamepad is connected in android, the Axis are mapped like Xbox PC, but
# the other buttons are normally Android gamepad, not like PC.

# Other Android gamepad are mapped like:

### Joysticks

# LeftUp=A4 0 to minus 1
# LeftDown=A4 0 to 1
# LeftLeft=A0 0 to minus 1
# LeftRight=A0 0 to 1

# RightUp=A3 0 to minus 1
# RightDown=A3 0 to 1
# RightLeft=A2 0 to minus 1
# RightRight=A2 0 to 1

### Buttons

# L3=B7
# R3=B8
# Select=B4
# Start=B6
# A=B0
# B=B1
# X=B2
# Y=B3
# L1=B9
# L2=B15
# R1=B10
# R2=B16

### D-Pad
# Up=B11
# Down=B12
# Left=B13
# Right=B14

init -50 python:
    import ctypes
    import sys
    import os

    class RayResult(ctypes.Structure):
        _fields_ = [
            ("hit", ctypes.c_int),
            ("map_x", ctypes.c_int), ("map_y", ctypes.c_int), ("map_z", ctypes.c_int),
            ("side", ctypes.c_int),
            ("step_x", ctypes.c_int), ("step_y", ctypes.c_int), ("step_z", ctypes.c_int)
        ]

    class EnemyData(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_double),
            ("y", ctypes.c_double),
            ("z", ctypes.c_double),
            ("dir_x", ctypes.c_double),
            ("dir_y", ctypes.c_double),
            ("hp", ctypes.c_double),
            ("state", ctypes.c_int),
            ("texture_idx", ctypes.c_int),
            ("timer", ctypes.c_double),
            ("move_speed", ctypes.c_double),
            ("enemy_type", ctypes.c_int)
        ]

    class PlayerData(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_double),
            ("y", ctypes.c_double),
            ("z", ctypes.c_double),
            ("vel_z", ctypes.c_double),
            ("rot", ctypes.c_double),
            ("is_grounded", ctypes.c_int),
            ("is_crouching", ctypes.c_int)
        ]

    class MoveResult(ctypes.Structure):
        _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

    class ProjectileData(ctypes.Structure):
        _fields_ = [
            ("x", ctypes.c_double), ("y", ctypes.c_double), ("z", ctypes.c_double),
            ("dir_x", ctypes.c_double), ("dir_y", ctypes.c_double), ("dir_z", ctypes.c_double),
            ("speed", ctypes.c_double),
            ("active", ctypes.c_int),      # 1/0
            ("texture_idx", ctypes.c_int),
            ("pitch", ctypes.c_double),
            ("damage", ctypes.c_int),
            ("from_player", ctypes.c_int)  # 1/0
        ]

    class SteinWrapper:
        ray_out_array = (ctypes.c_int * 8)()
        ray_out_ptr = ctypes.addressof(ray_out_array)
        
        move_out_array = (ctypes.c_double * 2)()
        move_out_ptr = ctypes.addressof(move_out_array)

        @staticmethod
        def update_projectiles_native(proj_addr, count, dt, map_addr, w, h, layers, min_layer):
            stein_lib.update_projectiles_c(
                proj_addr, count, dt, 
                map_addr, w, h, layers, min_layer
            )

        @staticmethod
        def prepare_scene_sprites(px, py, proj_ptr, max_projs, enemy_ptr, num_enemies, static_ptr, num_statics, out_ptr, max_sprites):
            return stein_lib.prepare_scene_sprites_c(
                px, py,
                proj_ptr, max_projs,
                enemy_ptr, num_enemies,
                static_ptr, num_statics,
                out_ptr, max_sprites
            )

        @staticmethod
        def check_line_of_sight(sx, sy, z, tx, ty, map_addr, w, h, layers, min_layer):
            result = stein_lib.check_line_of_sight_c(
                sx, sy, z, tx, ty,
                map_addr, w, h, layers, min_layer
            )
            return result == 1

        @staticmethod
        def get_map_height(x, y, check_z, map_addr, w, h, layers, min_layer):
            return stein_lib.get_map_height_c(
                x, y, check_z, 
                map_addr, w, h, layers, min_layer
            )

        @staticmethod
        def cast_ray_fast(*args):
            stein_lib.cast_ray_c(*args, SteinWrapper.ray_out_ptr)
            if SteinWrapper.ray_out_array[0]:
                return (True, *SteinWrapper.ray_out_array[1:])
            return (False, 0, 0, 0, 0, 0, 0, 0)

        @staticmethod
        def resolve_movement(*args):
            stein_lib.resolve_movement_c(*args, SteinWrapper.move_out_ptr)
            return (SteinWrapper.move_out_array[0], SteinWrapper.move_out_array[1])

        @staticmethod
        def update_player_complete(player_addr, dt, speed, strafe, turn, move_speed, rot_speed, map_addr, w, h, layers, min_layer):
            stein_lib.update_player_complete_c(
                player_addr, dt, 
                speed, strafe, turn, 
                move_speed, rot_speed,
                map_addr, w, h, layers, min_layer
            )

    stein_lib = None
    library_path = None
    USING_CYTHON = False
    STEIN_NATIVE_AVAILABLE = False
    STEIN_NATIVE_ERROR = None

    try:
        if renpy.android:
            library_path = "libstein_core.so"
        
        elif renpy.windows:
            library_path = os.path.join(config.gamedir, "additional", "renpystein", "stein_core.dll")
            if not os.path.exists(library_path):
                library_path = os.path.join(config.gamedir, "stein_core.dll")

        elif renpy.linux:
            library_path = os.path.join(config.gamedir, "additional", "renpystein", "stein_core.so")

        if library_path:
            stein_lib = ctypes.CDLL(library_path)
            
            stein_lib.cast_ray_c.argtypes = [
                ctypes.c_double, ctypes.c_double, ctypes.c_double,
                ctypes.c_double, ctypes.c_double, ctypes.c_double,
                ctypes.c_void_p,
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                ctypes.c_double,
                ctypes.c_void_p
            ]
            stein_lib.cast_ray_c.restype = None

            stein_lib.resolve_movement_c.argtypes = [
                ctypes.c_double, ctypes.c_double, ctypes.c_double,
                ctypes.c_double, ctypes.c_double, ctypes.c_double,
                ctypes.c_void_p,
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                ctypes.c_void_p
            ]
            stein_lib.resolve_movement_c.restype = None

            stein_lib.check_line_of_sight_c.argtypes = [
                ctypes.c_double, ctypes.c_double, ctypes.c_double, # Start X, Y, Z
                ctypes.c_double, ctypes.c_double,                  # Target X, Y
                ctypes.c_void_p,                                   # Map Pointer
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int # Map Data
            ]
            stein_lib.check_line_of_sight_c.restype = ctypes.c_int

            stein_lib.get_map_height_c.argtypes = [
                ctypes.c_double, ctypes.c_double, ctypes.c_double, # x, y, check_z
                ctypes.c_void_p,                                   # map_ptr
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int # w, h, layers, min
            ]
            stein_lib.get_map_height_c.restype = ctypes.c_double

            stein_lib.update_projectiles_c.argtypes = [
                ctypes.c_void_p, ctypes.c_int, ctypes.c_double, # array, count, dt
                ctypes.c_void_p,                                # map_ptr
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
            ]
            stein_lib.update_projectiles_c.restype = None

            stein_lib.prepare_scene_sprites_c.argtypes = [
                ctypes.c_double, ctypes.c_double,
                ctypes.c_void_p, ctypes.c_int,
                ctypes.c_void_p, ctypes.c_int,
                ctypes.c_void_p, ctypes.c_int,
                ctypes.c_void_p, ctypes.c_int
            ]
            stein_lib.prepare_scene_sprites_c.restype = ctypes.c_int

            stein_lib.update_enemies_c.argtypes = [
                ctypes.c_void_p,    # enemies_addr (pointer to array)
                ctypes.c_int,       # count
                ctypes.c_double, ctypes.c_double, ctypes.c_double, # player x, y, z
                ctypes.c_double,    # dt
                ctypes.c_void_p,    # flat_map_addr
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int # map dimensions
            ]
            stein_lib.update_enemies_c.restype = None

            stein_lib.check_hitscan_c.argtypes = [
                ctypes.c_double, ctypes.c_double, ctypes.c_double, # ray origin
                ctypes.c_double, ctypes.c_double, ctypes.c_double, # ray dir
                ctypes.c_void_p,    # enemies_addr
                ctypes.c_int,       # count
                ctypes.c_double,    # max_dist
                ctypes.c_double     # damage
            ]
            stein_lib.check_hitscan_c.restype = ctypes.c_int # Returns index of hit enemy (-1 if none)

            stein_lib.update_player_physics_c.argtypes = [
                ctypes.c_void_p,    # player_addr (pointer to PlayerData struct)
                ctypes.c_double,    # dt
                ctypes.c_void_p,    # flat_map_addr
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int # map dimensions
            ]
            stein_lib.update_player_physics_c.restype = None

            stein_lib.update_player_complete_c.argtypes = [
                ctypes.c_void_p,    # player_addr
                ctypes.c_double,    # dt
                ctypes.c_double, ctypes.c_double, ctypes.c_double, # inputs: speed, strafe, turn
                ctypes.c_double, ctypes.c_double, # stats: move_speed, rot_speed
                ctypes.c_void_p,    # map_addr
                ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
            ]
            stein_lib.update_player_complete_c.restype = None

            SteinWrapper.stein_lib = stein_lib

            sys.modules["stein_core"] = SteinWrapper
            print(f"Sayoristein: Native motor loaded in {library_path}")
            USING_CYTHON = True
            STEIN_NATIVE_AVAILABLE = True

    except Exception as e:
        STEIN_NATIVE_ERROR = str(e)
        print(f"Sayoristein Error Loading Library: {e}")

    stein_native_available = STEIN_NATIVE_AVAILABLE
    stein_native_error = STEIN_NATIVE_ERROR

init -10 python:
    import sys
    import os
    import ctypes
    import array

    core_path = os.path.join(config.gamedir, "core")
    if core_path not in sys.path:
        sys.path.append(core_path)

    try:
        import stein_core
        stein_native_available = True
        stein_native_error = None
    except ImportError as e:
        stein_core = None
        stein_native_available = False
        if not stein_native_error:
            stein_native_error = str(e)
        print("Sayoristein disabled: native stein_core library is not available.")


    def flatten_world_map(world_map, width, height, min_layer, max_layer):
        num_layers = max_layer - min_layer + 1
        total_size = width * height * num_layers
        
        flat = array.array('i', [0] * total_size)
        
        if isinstance(world_map, dict):
            for z, grid in world_map.items():
                layer_idx = z - min_layer
                if layer_idx < 0 or layer_idx >= num_layers: continue
                
                base_idx = layer_idx * width * height
                for x in range(min(len(grid), width)):
                    row = grid[x]
                    for y in range(min(len(row), height)):
                        if row[y] > 0:
                            flat[base_idx + (x * height) + y] = row[y]
                            
        elif isinstance(world_map, list):
            layer_idx = 0 - min_layer
            if 0 <= layer_idx < num_layers:
                base_idx = layer_idx * width * height
                for x in range(min(len(world_map), width)):
                    row = world_map[x]
                    for y in range(min(len(row), height)):
                        if row[y] > 0:
                            flat[base_idx + (x * height) + y] = row[y]

        return flat

    SLOT_MELEE   = 0
    SLOT_HANDGUN = 1
    SLOT_LONG    = 2
    SLOT_SPECIAL = 3

    renpy.register_shader("stein.raycaster", variables="""
        uniform float u_volumetric_clouds;
        uniform float u_rain_intensity;
        uniform float u_snow_intensity;
        uniform float u_wetness;
        uniform float u_time_of_day;
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
        uniform float u_map_layer_norm_height;
        uniform float u_map_layer_base_y;
        uniform float u_map_layer_count;
        uniform vec2 u_map_tex_pixel_size;
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
        uniform float u_soft_shadows;
        uniform float u_enable_shadows;
        uniform float u_max_dist;
        uniform float u_simple_floor;
        uniform vec3 u_ambient_color;
        uniform vec3 u_ambient_near_color;
        varying vec2 v_tex_coord;
        attribute vec2 a_tex_coord;
    """, vertex_200="""
        v_tex_coord = a_tex_coord;
    """, fragment_functions="""
        float hash(vec2 p) {
            p = fract(p * vec2(123.34, 456.21));
            p += dot(p, p + 45.32);
            return fract(p.x * p.y);
        }

        float noise(vec2 p) {
            vec2 i = floor(p);
            vec2 f = fract(p);
            f = f * f * (3.0 - 2.0 * f);
            float a = hash(i);
            float b = hash(i + vec2(1.0, 0.0));
            float c = hash(i + vec2(0.0, 1.0));
            float d = hash(i + vec2(1.0, 1.0));
            return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
        }

        float fbm(vec2 p) {
            float v = 0.0;
            float a = 0.5;
            for (int i = 0; i < 5; i++) {
                v += a * noise(p);
                p *= 2.0;
                a *= 0.5;
            }
            return v;
        }

        float ripple_layer(vec2 uv, float t) {
            vec2 p = uv * 5.0;
            vec2 g = floor(p);
            vec2 f = fract(p) - 0.5;
            
            vec2 rand_offset = (vec2(hash(g), hash(g + 11.5)) - 0.5) * 0.8;
            f -= rand_offset;
            
            float h = hash(g + vec2(3.0, 7.0));
            float t_local = fract(t * 1.2 + h * 10.0);
            
            float d = length(f);
            float r = 0.5 * t_local;
            
            float circle = smoothstep(0.05, 0.0, abs(d - r));
            float fade = 1.0 - t_local;
            
            return circle * fade;
        }

        float rain_layer(vec2 uv, float t) {
            vec2 st = uv;
            st.x *= 20.0; 
            st.y *= 0.5;  
            
            vec2 g = floor(st);
            
            float col_offset = hash(vec2(g.x, 0.0)); 
            float y_move = st.y + t + col_offset * 10.0;
            
            float cell_y = floor(y_move);
            float cell_fract = fract(y_move);
            
            float h = hash(vec2(g.x, cell_y));
            
            if (h < 0.85) return 0.0;
            
            float drop = 1.0 - cell_fract; 
            float beam = smoothstep(0.4, 0.5, fract(st.x)) * smoothstep(0.6, 0.5, fract(st.x));
            
            return drop * beam;
        }

        float intersectPyramid(vec3 ro, vec3 rd, out vec3 outNormal) {
            float tMin = 10000.0;
            bool hit = false;
            
            vec3 N[4]; float D[4];
            N[0] = vec3(1.0, 0.0, 1.0); D[0] = -1.0;
            N[1] = vec3(-1.0, 0.0, 1.0); D[1] = 0.0;
            N[2] = vec3(0.0, 1.0, 1.0); D[2] = -1.0;
            N[3] = vec3(0.0, -1.0, 1.0); D[3] = 0.0;
            
            for(int i=0; i<4; i++) {
                float denom = dot(rd, N[i]);
                if (denom < -0.0001) {
                    float t = -(dot(ro, N[i]) + D[i]) / denom;
                    if (t > 0.0) {
                        vec3 p = ro + rd * t;
                        if (p.z >= 0.0 && p.z <= 0.5) {
                            float h = 0.5 - p.z;
                            if (p.x >= 0.5 - h - 0.01 && p.x <= 0.5 + h + 0.01 &&
                                p.y >= 0.5 - h - 0.01 && p.y <= 0.5 + h + 0.01) {
                                if (t < tMin) {
                                    tMin = t;
                                    outNormal = normalize(N[i]);
                                    hit = true;
                                }
                            }
                        }
                    }
                }
            }
            if (hit) return tMin;
            return -1.0;
        }
    """, fragment_300="""
        const int MAX_STEPS = 128; 
        
        vec2 stein_uv = v_tex_coord;

        // RAY GENERATION (3D)
        // Player Position (Camera Origin). Z=0.5 is eye level + offsets
        vec3 rayPos = vec3(u_player_pos.x, u_player_pos.y, 0.5 + u_z_offset);
        
        // Pitch Angle
        float pitchAngle = atan(u_pitch);
        float cp = cos(pitchAngle);
        float sp = sin(pitchAngle);
        vec3 rightAxis = normalize(vec3(u_player_plane, 0.0));

        // Ray Direction
        float cameraX = 2.0 * stein_uv.x - 1.0; 
        float screenY = (0.5 - stein_uv.y) * 2.0; 
        
        vec3 baseDir = vec3(u_player_dir, 0.0) + vec3(u_player_plane, 0.0) * cameraX + vec3(0.0, 0.0, 1.0) * (screenY / u_vertical_scale);
        
        vec3 rayDir = baseDir * cp + cross(rightAxis, baseDir) * sp + rightAxis * dot(rightAxis, baseDir) * (1.0 - cp);
        rayDir = normalize(rayDir);

        vec3 flashBase = vec3(u_player_dir, 0.0) + vec3(u_player_plane, 0.0) * u_flashlight_bob.x + vec3(0.0, 0.0, 1.0) * u_flashlight_bob.y;
        vec3 flashDir = flashBase * cp + cross(rightAxis, flashBase) * sp + rightAxis * dot(rightAxis, flashBase) * (1.0 - cp);
        flashDir = normalize(flashDir);
        
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
        vec3 hitNormal = vec3(0.0);

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
            
            if (rayDist > u_max_dist) { hit = 2; break; } // Too far
            
            // Map Bounds Check
            bool inside = (mapPos.x >= 0 && mapPos.x < int(u_map_size.x) && mapPos.y >= 0 && mapPos.y < int(u_map_size.y));
            
            // Voxel Check
            if (inside) {
                int layer = int(mapPos.z);
                int layer_idx = layer - int(u_map_layer_base_y);
                
                if (layer_idx >= 0 && layer_idx < int(u_map_layer_count)) {
                    float u = (float(mapPos.x) + 0.5) * u_map_tex_pixel_size.x;
                    float v_base = float(layer_idx) * u_map_layer_norm_height;
                    float v_local = (float(mapPos.y) + 0.5) * u_map_tex_pixel_size.y;
                    
                    vec2 mapUV = vec2(u, v_base + v_local);
                    vec4 mapPixel = texture2D(u_map_texture, mapUV);
                    if (mapPixel.r > 0.5) {
                        int id = int(mapPixel.g * 255.0 + 0.5);
                        if (id == 20) {
                            vec3 norm;
                            float t = intersectPyramid(rayPos - vec3(mapPos), rayDir, norm);
                            if (t > 0.0 && t >= rayDist - 0.01) {
                                rayDist = t;
                                wallID = id;
                                hit = 1;
                                hitNormal = norm;
                                break;
                            }
                        } else {
                            wallID = id;
                            hit = 1;
                            break;
                        }
                    }
                }
            }
        }

        vec3 color;
        
        if (hit == 1) {
            vec3 hitPos = rayPos + rayDir * rayDist;
            
            vec2 texUV;
            if (wallID == 20) {
                if (abs(hitNormal.x) > 0.5) {
                    texUV = vec2(fract(hitPos.y), fract(hitPos.z * 2.0));
                } else {
                    texUV = vec2(fract(hitPos.x), fract(hitPos.z * 2.0));
                }
            } else {
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
                color = texture2D(u_wall_atlas, vec2(finalU, finalV), 0.0).rgb;
            }
            
            vec3 finalColor = color;
            
            float fogDist = length(hitPos.xy - u_player_pos);
            
            vec3 ambientLight = u_ambient_color; 
            
            // float personalLight = max(0.0, 1.0 - (fogDist / 4.0)); 
            // ambientLight += u_ambient_near_color * personalLight;
            
            vec3 totalLight = ambientLight;

            if (u_flashlight_active > 0.5) {
                vec3 flashPos = rayPos;

                vec3 lightVec = normalize(hitPos - flashPos);
                
                float dotProd = dot(lightVec, flashDir); 
                float dist3D = distance(hitPos, flashPos);

                if (dotProd > 0.82) { 
                    float spotEffect = smoothstep(0.82, 0.92, dotProd);
                    
                    float att = 1.0 / (1.5 + dist3D * 0.03 + dist3D * dist3D * 0.002);
                    vec3 flashLightColor = vec3(0.95, 0.95, 1.0);
                    
                    totalLight += flashLightColor * att * 2.2 * spotEffect;
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
                    float visibility = 1.0;
                    
                    if (u_enable_shadows > 0.5) {
                        visibility = 0.0;
                        int samples = 1;
                        float spread = 0.0;
                        
                        if (u_soft_shadows > 0.5) {
                            samples = 9;
                            spread = 0.55;
                        }
                        
                        vec2 dirToLight = normalize(lightPos - hitPos.xy);
                        vec2 perp = vec2(-dirToLight.y, dirToLight.x) * spread;
                        
                        for (int k = 0; k < 9; k++) {
                            if (k >= samples) break;
                            
                            float offScale = 0.0;
                            if (k == 1) offScale = 1.0;
                            if (k == 2) offScale = -1.0;
                            if (k == 3) offScale = 0.5;
                            if (k == 4) offScale = -0.5;
                            if (k == 5) offScale = 0.75;
                            if (k == 6) offScale = -0.75;
                            if (k == 7) offScale = 0.25;
                            if (k == 8) offScale = -0.25;
                            
                            vec2 offset = perp * offScale;
                            
                            vec2 targetPos = lightPos + offset;
                            vec2 rayDir = normalize(targetPos - hitPos.xy);
                            float rayDist = distance(targetPos, hitPos.xy);
                            
                            float stepSize = 0.2;
                            int steps = int(rayDist / stepSize);
                            vec2 checkPos = hitPos.xy + rayDir * 0.1;
                            bool hitWall = false;
                            
                            for(int s=0; s<64; s++) { 
                                if (s >= steps) break;
                                checkPos += rayDir * stepSize;
                                
                                if (abs(floor(checkPos.x) - float(mapPos.x)) < 0.1 && abs(floor(checkPos.y) - float(mapPos.y)) < 0.1) continue;

                                vec2 mapUV = (floor(checkPos) + 0.5) / u_map_size;
                                mapUV *= u_map_uv_scale;
                                vec4 shadowMapPixel = texture2D(u_map_texture, mapUV);
                                if (shadowMapPixel.r > 0.5) {
                                    // Check id to avoid pyramid casting cube shadows
                                    int sID = int(shadowMapPixel.g * 255.0 + 0.5);
                                    if (sID != 20) {
                                        hitWall = true;
                                        break;
                                    }
                                }
                            }
                            
                            if (!hitWall) visibility += 1.0;
                        }
                        
                        visibility /= float(samples);
                    }

                    if (visibility > 0.0) {
                        float att = 1.0 - (distToLight / radius);
                        att = att * att; 
                        
                        vec3 lampColor = vec3(0.2, 1.0, 0.2); 
                        totalLight += lampColor * intensity * att * visibility;
                    }
                }
            }

            float faceShadow = 1.0;
            if (wallID == 20) {
                faceShadow = 0.6 + 0.4 * hitNormal.z;
            } else {
                if (side == 1) faceShadow = 0.7; 
                if (side == 2) faceShadow = 1.0; 
            }
            
            color = finalColor * totalLight * faceShadow;

        } else {
            if (u_volumetric_clouds > 0.5) {
                vec3 skyColorTop;
                vec3 skyColorBottom;
                vec3 cloudColor;
                
                // Day Cycle Colors
                vec3 nightTop = vec3(0.0, 0.0, 0.1);
                vec3 nightBot = vec3(0.05, 0.05, 0.2);
                vec3 nightCloud = vec3(0.1, 0.1, 0.15);

                vec3 dayTop = vec3(0.0, 0.4, 0.8);
                vec3 dayBot = vec3(0.6, 0.8, 1.0);
                vec3 dayCloud = vec3(1.0, 1.0, 1.0);

                vec3 sunsetTop = vec3(0.2, 0.1, 0.4);
                vec3 sunsetBot = vec3(1.0, 0.4, 0.2);
                vec3 sunsetCloud = vec3(1.0, 0.6, 0.5);

                float t = mod(u_time_of_day, 24.0); // Ensure 0-24 range

                
                if (t < 5.0) {
                    skyColorTop = nightTop; skyColorBottom = nightBot; cloudColor = nightCloud;
                } else if (t < 8.0) {
                    float p = (t - 5.0) / 3.0;
                    skyColorTop = mix(nightTop, dayTop, p);
                    skyColorBottom = mix(nightBot, dayBot, p);
                    cloudColor = mix(nightCloud, dayCloud, p);
                } else if (t < 16.0) {
                    skyColorTop = dayTop; skyColorBottom = dayBot; cloudColor = dayCloud;
                } else if (t < 19.0) {
                    float p = (t - 16.0) / 3.0;
                    skyColorTop = mix(dayTop, sunsetTop, p);
                    skyColorBottom = mix(dayBot, sunsetBot, p);
                    cloudColor = mix(dayCloud, sunsetCloud, p);
                } else if (t < 21.0) {
                    float p = (t - 19.0) / 2.0;
                    skyColorTop = mix(sunsetTop, nightTop, p);
                    skyColorBottom = mix(sunsetBot, nightBot, p);
                    cloudColor = mix(sunsetCloud, nightCloud, p);
                } else {
                    skyColorTop = nightTop; skyColorBottom = nightBot; cloudColor = nightCloud;
                }

                float skyGradient = smoothstep(-0.5, 0.5, rayDir.z);
                vec3 skyBase = mix(skyColorBottom, skyColorTop, skyGradient);
                
                color = skyBase;

                if (rayDir.z > 0.01) {
                    vec2 cloudUV = rayDir.xy / rayDir.z;
                    cloudUV += u_time * 0.05;
                    
                    float n = fbm(cloudUV * 0.5);
                    float c = smoothstep(0.4, 0.8, n);
                    c *= smoothstep(0.0, 0.2, rayDir.z);
                    
                    float brightness = 1.0;
                    if (t < 6.0 || t > 20.0) brightness = 0.3;
                    else if (t < 8.0) brightness = mix(0.3, 1.0, (t - 6.0) / 2.0);
                    else if (t > 18.0) brightness = mix(1.0, 0.3, (t - 18.0) / 2.0);
                    
                    color = mix(color, cloudColor * brightness, c);
                }
                
                float starVisibility = 0.0;
                if (t < 6.0) starVisibility = 1.0;
                else if (t < 7.0) starVisibility = 1.0 - (t - 6.0);
                else if (t > 20.0) starVisibility = (t - 20.0) / 1.0;
                if (t > 21.0) starVisibility = 1.0;

                if (starVisibility > 0.01 && rayDir.z > 0.01) {
                    vec2 starUV = rayDir.xy / (1.0 + rayDir.z);
                    
                    float scale = 300.0; 
                    vec2 gridUV = starUV * scale;
                    vec2 gridID = floor(gridUV);
                    vec2 gridLocal = fract(gridUV) - 0.5;
                    
                    float h = hash(gridID);
                    
                    if (h > 0.97) {
                        // Stable random position in cell
                        float r1 = hash(gridID + vec2(12.34, 56.78));
                        float r2 = hash(gridID + vec2(90.12, 34.56));
                        vec2 pos = (vec2(r1, r2) - 0.5) * 0.7;
                        
                        float dist = length(gridLocal - pos);
                        
                        float brightness = smoothstep(0.4, 0.1, dist);
                        
                        float twinkle = 0.7 + 0.3 * sin(u_time * 2.0 + h * 50.0);
                        
                        // Horizon fade
                        float fade = smoothstep(0.01, 0.1, rayDir.z);
                        
                        color += vec3(brightness * twinkle * fade * starVisibility);
                    }
                }
            } else {
                // Skybox
                vec2 skyUV = stein_uv;
                // Apply pitch to skyUV.y
                skyUV.y -= u_pitch; 
                skyUV.y = clamp(skyUV.y, 0.0, 1.0);
                color = texture2D(u_sky_texture, skyUV).rgb;
            }
        }

        // SPRITE RENDERING (Adapted for 3D)
        // We approximate 2D billboard logic using the 3D ray distance
        
        // Calculate Camera Forward Vector (Rotated)
        vec3 forwardUnrot = vec3(u_player_dir, 0.0);
        vec3 forwardRot = forwardUnrot * cp + cross(rightAxis, forwardUnrot) * sp + rightAxis * dot(rightAxis, forwardUnrot) * (1.0 - cp);
        
        float perpWallDist = dot(rayDir * rayDist, forwardRot);
        
        // If we didnt hit a wall (Sky/Void), the depth is infinite
        if (hit != 1) perpWallDist = 10000.0;
        
        float currentDepth = perpWallDist;
        
        // Precalculate pitch shift in pixels for sprites
        // float pitchPixeLCTRL = u_pitch * u_vertical_scale * (u_resolution.y / 2.0);

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
            
            // Apply Pitch Rotation to Sprite Position
            float camHeight = 0.5 + u_z_offset;
            float spriteZ = -camHeight;
            
            float rotY = transformY * cp + spriteZ * sp;
            float rotZ = -transformY * sp + spriteZ * cp;

            if (rotY <= 0.1) continue;
            // Robust depth check
            if (rotY >= currentDepth) continue; 

            float spriteScreenX = (u_resolution.x / 2.0) * (1.0 + transformX / rotY);
            
            // Scale sprites down
            float spriteScale = 0.55; 
            float spriteHeight = abs(u_resolution.y / rotY) * u_vertical_scale * spriteScale; 
            float spriteWidth = spriteHeight; 

            // Sprite Anchoring Logic (Floor Alignment)
            // Calculate Screen Y of the floor (rotZ)
            float screenY_floor = (rotZ / rotY) * u_vertical_scale;
            float pixelY_floor = (0.5 - screenY_floor / 2.0) * u_resolution.y;
            
            float spritePixeLCTRL = spritePitch * u_vertical_scale * (u_resolution.y / 2.0);
            
            float drawEndY = pixelY_floor - spritePixeLCTRL;
            float drawStartY = drawEndY - spriteHeight;
            
            float drawStartX = spriteScreenX - spriteWidth / 2.0;
            float drawEndX = spriteScreenX + spriteWidth / 2.0;

            float currentPixelX = stein_uv.x * u_resolution.x; 
            float currentPixelY = stein_uv.y * u_resolution.y;

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
                        
                        vec3 sprLight = u_ambient_color;
                        // float sprPersonal = max(0.0, 1.0 - (sprDist / 4.0));
                        // sprLight += u_ambient_near_color * sprPersonal;

                        if (u_flashlight_active > 0.5) {
                            float dotProd = dot(rayDir, flashDir);
                            
                            float dist3D = transformY;
                            
                            if (dotProd > 0.82) {
                                float spotEffect = smoothstep(0.82, 0.92, dotProd);
                                float att = 1.0 / (1.5 + dist3D * 0.03 + dist3D * dist3D * 0.002);
                                vec3 flashLightColor = vec3(0.95, 0.95, 1.0);
                                
                                sprLight += flashLightColor * att * 2.2 * spotEffect;
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
                                float visibility = 1.0;
                                
                                if (u_enable_shadows > 0.5) {
                                    visibility = 0.0;
                                    int samples = 1;
                                    float spread = 0.0;
                                    
                                    if (u_soft_shadows > 0.5) {
                                        samples = 9;
                                        spread = 0.55;
                                    }
                                    
                                    vec2 dirToLight = normalize(lData.xy - spritePos);
                                    vec2 perp = vec2(-dirToLight.y, dirToLight.x) * spread;
                                    
                                    for (int k = 0; k < 9; k++) {
                                        if (k >= samples) break;
                                        
                                        float offScale = 0.0;
                                        if (k == 1) offScale = 1.0;
                                        if (k == 2) offScale = -1.0;
                                        if (k == 3) offScale = 0.5;
                                        if (k == 4) offScale = -0.5;
                                        if (k == 5) offScale = 0.75;
                                        if (k == 6) offScale = -0.75;
                                        if (k == 7) offScale = 0.25;
                                        if (k == 8) offScale = -0.25;
                                        
                                        vec2 offset = perp * offScale;
                                        
                                        vec2 targetPos = lData.xy + offset;
                                        vec2 rayDir = normalize(targetPos - spritePos);
                                        float rayDist = distance(targetPos, spritePos);
                                        
                                        float stepSize = 0.2;
                                        int steps = int(rayDist / stepSize);
                                        vec2 checkPos = spritePos + rayDir * 0.1;
                                        bool hitWall = false;
                                        
                                        for(int s=0; s<64; s++) {
                                            if (s >= steps) break;
                                            checkPos += rayDir * stepSize;
                                            
                                            vec2 mapUV = (floor(checkPos) + 0.5) / u_map_size;
                                            mapUV *= u_map_uv_scale;
                                            vec4 smp = texture2D(u_map_texture, mapUV);
                                            if (smp.r > 0.5) {
                                                int sid = int(smp.g * 255.0 + 0.5);
                                                if (sid != 20) {
                                                    hitWall = true;
                                                    break;
                                                }
                                            }
                                        }
                                        
                                        if (!hitWall) visibility += 1.0;
                                    }
                                    
                                    visibility /= float(samples);
                                }

                                if (visibility > 0.0) {
                                    float att = 1.0 - (lDist / lData.z);
                                    att = att * att;
                                    vec3 lampColor = vec3(0.4, 0.9, 0.4);
                                    sprLight += lampColor * lData.w * att * visibility;
                                }
                            }
                        }

                        color = spriteCol.rgb * sprLight;
                        currentDepth = transformY; 
                    }
                }
            }
        }

        if (u_rain_intensity > 0.0) {
            float rainVal = 0.0;
            for (int i=1; i<=4; i++) {
                float dist = float(i) * 2.5; 
                if (dist > currentDepth) break;
                
                vec3 p = rayPos + rayDir * dist;
                
                vec2 uv1 = vec2(p.y, p.z) * vec2(1.0, 2.0); // YZ Plane
                vec2 uv2 = vec2(p.x, p.z) * vec2(1.0, 2.0); // XZ Plane
                
                float t = u_time * 15.0;
                float n1 = rain_layer(uv1, t);
                float n2 = rain_layer(uv2, t);
                
                float blend = abs(rayDir.x);
                float n = mix(n2, n1, blend);
                
                // Distance Fade
                float fade = 1.0 - (dist / 12.0);
                if (fade < 0.0) fade = 0.0;
                
                rainVal += n * fade;
            }
            color = mix(color, vec3(0.7, 0.8, 0.9), rainVal * u_rain_intensity * 0.4);
        }

        if (u_snow_intensity > 0.0) {
            float snowVal = 0.0;
            for (int i=1; i<=4; i++) {
                float dist = float(i) * 2.0; 
                if (dist > currentDepth) break;
                
                vec3 p = rayPos + rayDir * dist;
                
                vec2 uv1 = vec2(p.y, p.z) * 0.8; 
                vec2 uv2 = vec2(p.x, p.z) * 0.8;
                
                float t = u_time * 2.0;
                uv1.y += t;
                uv2.y += t;
                
                uv1.x += sin(u_time + p.z) * 0.2;
                uv2.x += cos(u_time + p.z) * 0.2;
                
                float n1 = noise(uv1);
                float n2 = noise(uv2);
                
                float blend = abs(rayDir.x);
                float n = mix(n2, n1, blend);
                
                float s = smoothstep(0.95, 1.0, n);
                
                float fade = 1.0 - (dist / 10.0);
                if (fade < 0.0) fade = 0.0;
                
                snowVal += s * fade;
            }
            color = mix(color, vec3(1.0), snowVal * u_snow_intensity * 0.8);
        }

        gl_FragColor = vec4(color, 1.0);
    """)

    renpy.register_shader("stein.motion_blur", variables="""
        uniform sampler2D tex0;
        uniform float u_blur_amount;
        varying vec2 v_tex_coord;
    """, fragment_200="""
        vec2 stein_mb_uv = v_tex_coord;
        vec4 mb_color = texture2D(tex0, stein_mb_uv);
        
        if (abs(u_blur_amount) > 0.001) {
            float blur = u_blur_amount * 0.02;
            vec4 sum = vec4(0.0);
            
            // 5-tap optimization
            sum += texture2D(tex0, vec2(stein_mb_uv.x - blur * 2.0, stein_mb_uv.y)) * 0.1;
            sum += texture2D(tex0, vec2(stein_mb_uv.x - blur * 1.0, stein_mb_uv.y)) * 0.25;
            sum += texture2D(tex0, vec2(stein_mb_uv.x, stein_mb_uv.y)) * 0.3;
            sum += texture2D(tex0, vec2(stein_mb_uv.x + blur * 1.0, stein_mb_uv.y)) * 0.25;
            sum += texture2D(tex0, vec2(stein_mb_uv.x + blur * 2.0, stein_mb_uv.y)) * 0.1;
            
            gl_FragColor = sum;
        } else {
            gl_FragColor = mb_color;
        }
    """)

    renpy.register_shader("stein.weapon_fx", variables="""
        varying vec2 v_tex_coord;
        attribute vec2 a_tex_coord;
        uniform float u_flash_progress; 
        uniform float u_flash_angle;
        uniform vec3 u_flash_color;
        uniform float u_heat_distortion;
        uniform float u_enable_smoke;
    """, vertex_200="""
        v_tex_coord = a_tex_coord;
    """, fragment_200="""
        // Center UVs to [-1, 1] range
        vec2 stein_w_uv = (v_tex_coord - 0.5) * 2.0; 
        
        // Internal rotation
        float s = sin(u_flash_angle);
        float c = cos(u_flash_angle);
        vec2 rotated_uv = mat2(c, -s, s, c) * stein_w_uv;
        
        float dist = length(rotated_uv);
        float angle = atan(rotated_uv.y, rotated_uv.x);
        
        // MUZZLE FLASH
        // Flash happens in the first 4% of the duration (1.5s * 0.04 = 0.06s)
        float flash_p = u_flash_progress * 25.0; 
        float flash_intensity = 0.0;
        
        if (flash_p < 1.0) {
            float spikes = abs(sin(angle * 4.0)) * 0.4 + abs(sin(angle * 9.0)) * 0.6;
            float core = exp(-dist * 5.0) * 2.5;
            float rays = exp(-dist * (4.0 + 8.0 * (1.0 - spikes))) * 1.2;
            float mask = smoothstep(1.0, 0.2, dist);
            
            flash_intensity = (core + rays) * (1.0 - flash_p);
            flash_intensity = clamp(flash_intensity * mask, 0.0, 1.0);
        }

        // BARREL SMOKE
        // Simulates smoke emanating from the hot barrel and rising up
        float smoke_alpha = 0.0;
        if (u_enable_smoke > 0.5 && u_flash_progress > 0.02) {
            float smoke_p = (u_flash_progress - 0.02) / 0.98;
            
            // Use unrotated UV so smoke always rises UP relative to screen
            vec2 stream_uv = stein_w_uv;
            
            // Detach from bottom logic (Smoke moves up/away from barrel)
            // We mask out the bottom part, and this mask moves up over time
            // uv.y is negative for up, 0 is center
            float detach_y = -0.1 - (smoke_p * 1.2);
            
            // Mask: Visible if y < detach_y (above the cut-off point)
            // We use smoothstep for a soft bottom edge
            float detach_mask = smoothstep(detach_y + 0.3, detach_y, stream_uv.y);
            
            // Wiggle the stream (turbulence)
            float wiggle = sin(stream_uv.y * 12.0 + u_flash_progress * 15.0) * 0.04;
            stream_uv.x += wiggle;
            
            // Stream shape
            float stream_width = 0.04 + abs(stream_uv.y) * 0.15; 
            float stream_shape = smoothstep(stream_width, 0.0, abs(stream_uv.x));
            
            // Top fade
            float height_mask = smoothstep(-0.95, -0.2, stream_uv.y); 
            
            // Scroll noise up through the stream
            float noise_y = stein_w_uv.y + u_flash_progress * 3.0;
            float noise = sin(stein_w_uv.x * 40.0) * sin(noise_y * 12.0);
            
            // Overall fade out over time
            float fade_out = 1.0 - smoothstep(0.2, 0.9, smoke_p);
            
            smoke_alpha = stream_shape * detach_mask * height_mask * (0.6 + 0.4 * noise) * fade_out * 0.8;
        }

        // HEAT DISTORTION
        float heat_val = 0.0;
        /*
        if (u_heat_distortion > 0.5) {
            float heat_prog = u_flash_progress * 3.0;
            if (heat_prog < 1.0) {
                float wave = sin(rotated_uv.x * 10.0 + heat_prog * 10.0) * 0.1;
                float heat_d = length(rotated_uv + vec2(wave, heat_prog * 0.5));
                float heat_ring = smoothstep(0.05, 0.0, abs(heat_d - 0.4 - heat_prog * 0.3));
                float turb = sin(angle * 20.0 + heat_prog * 20.0);
                heat_val = heat_ring * 0.4 * (1.0 - heat_prog) * (0.5 + 0.5 * turb);
            }
        }
        
        heat_val *= (1.0 - smoke_alpha * 1.5);
        heat_val = max(0.0, heat_val);
        */

        // Combine
        vec3 final_color = u_flash_color * flash_intensity;
        float final_alpha = flash_intensity;
        
        // Add Heat
        final_color += vec3(heat_val);
        final_alpha = max(final_alpha, heat_val);
        
        // Add Smoke
        vec3 smoke_col = vec3(0.95, 0.95, 1.0); // White/Grey smoke
        
        // Mix Smoke
        final_color = mix(final_color, smoke_col, smoke_alpha);
        final_alpha = max(final_alpha, smoke_alpha);
        
        gl_FragColor = vec4(final_color, final_alpha);
    """)

    renpy.register_shader("stein.bloom", variables="""
        uniform sampler2D tex0;
        uniform vec2 u_resolution;
        varying vec2 v_tex_coord;
    """, fragment_200="""
        vec2 stein_bloom_uv = v_tex_coord;
        vec4 source = texture2D(tex0, stein_bloom_uv);
        
        float bloomSpread = 4.0;
        float threshold = 0.8;
        float intensity = 0.5;

        vec4 sum = vec4(0.0);
        vec2 size = vec2(1.0) / u_resolution;

        for (float i = -1.0; i <= 1.0; i++) {
            for (float j = -1.0; j <= 1.0; j++) {
                vec2 offset = vec2(i, j) * bloomSpread * size;
                vec4 col = texture2D(tex0, stein_bloom_uv + offset);
                
                float brightness = dot(col.rgb, vec3(0.2126, 0.7152, 0.0722));
                if (brightness > threshold) {
                    sum += col * brightness; 
                }
            }
        }
        
        sum = sum / 9.0;
        gl_FragColor = source + (sum * intensity);
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
            self.fly_mode = False

        def get_ground_height_at(self, x, y, check_z=None):
            if check_z is None: check_z = self.z
            
            map_address, _ = self.wm.flat_map_buffer.buffer_info()
            
            return stein_core.get_map_height(
                x, y, check_z,
                map_address,
                self.wm.mapWidth, self.wm.mapHeight,
                self.wm.num_layers, self.wm.min_layer
            )

        def trigger_jump(self):
            if self.is_grounded and not self.is_crouching:
                self.is_crouching = True; self.crouch_timer = self.crouch_duration

        def update_physics(self, dt):
            if self.fly_mode:
                self.is_grounded = False
                self.velocity_z = 0.0
                
                fly_speed = 5.0
                if self.wm.kb_running: fly_speed = 10.0
                
                if self.wm.kb_fly_up:
                    self.z += fly_speed * dt
                if self.wm.kb_fly_down:
                    self.z -= fly_speed * dt
                return

            floor_h = self.get_ground_height_at(self.x, self.y)
            
            if self.is_crouching:
                self.crouch_timer -= dt
                progress = 1.0 - (self.crouch_timer / self.crouch_duration)
                target_z = floor_h + (self.CROUCH_DEPTH * math.sin(progress * math.pi))
                self.z = target_z 
                
                if self.crouch_timer <= 0:
                    self.is_crouching = False; self.is_grounded = False; self.velocity_z = self.JUMP_FORCE
                    self.z = max(self.z, floor_h)
            
            p_data = self.wm.player_data
            p_data.x = self.x
            p_data.y = self.y
            p_data.z = self.z
            p_data.vel_z = self.velocity_z
            p_data.rot = self.rot
            p_data.is_grounded = 1 if self.is_grounded else 0
            p_data.is_crouching = 1 if self.is_crouching else 0

        def resolve_wall_collision(self, radius):
            if self.fly_mode: return

            # Right
            if self.wm.isBlocking(math.floor(self.x + radius), math.floor(self.y), self.z):
                self.x = math.floor(self.x + radius) - radius - 0.001
            # Left
            elif self.wm.isBlocking(math.floor(self.x - radius), math.floor(self.y), self.z):
                self.x = math.floor(self.x - radius) + 1.0 + radius + 0.001
            
            # Down
            if self.wm.isBlocking(math.floor(self.x), math.floor(self.y + radius), self.z):
                self.y = math.floor(self.y + radius) - radius - 0.001
            # Up
            elif self.wm.isBlocking(math.floor(self.x), math.floor(self.y - radius), self.z):
                self.y = math.floor(self.y - radius) + 1.0 + radius + 0.001

        def move(self, dt):
            self.update_physics(dt)

            if self.fly_mode:
                moveStep = self.speed * self.moveSpeed * dt
                strafeStep = self.strafe_speed * self.moveSpeed * dt
                self.rot += self.dir * self.rotSpeed * dt
                self.rot %= twoPI
                
                vx = math.cos(self.rot) * moveStep + math.sin(self.rot) * strafeStep
                vy = math.sin(self.rot) * moveStep - math.cos(self.rot) * strafeStep
                
                self.x += vx
                self.y += vy
            else:
                # Use the new C implementation
                map_address, _ = self.wm.flat_map_buffer.buffer_info()
                
                SteinWrapper.update_player_complete(
                    self.wm.player_ptr,
                    dt,
                    float(self.speed),        # input_speed
                    float(self.strafe_speed), # input_strafe
                    float(self.dir),          # input_turn
                    float(self.moveSpeed),
                    float(self.rotSpeed),
                    map_address,
                    self.wm.mapWidth, self.wm.mapHeight,
                    self.wm.num_layers, self.wm.min_layer
                )
                
                p_data = self.wm.player_data
                self.x = p_data.x
                self.y = p_data.y
                self.z = p_data.z
                self.velocity_z = p_data.vel_z
                self.rot = p_data.rot
                self.is_grounded = (p_data.is_grounded == 1)
                
                if self.z < -25.0:
                    self.z = 10.0; self.velocity_z = 0.0

            self.dirx = math.cos(self.rot)
            self.diry = math.sin(self.rot)
            
            self.planex = math.cos(self.rot - 1.5708) * 0.66 
            self.planey = math.sin(self.rot - 1.5708) * 0.66

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
                self.z = self.wm.player.z + 0.5
                self.dir_z = (pitch / float(self.wm.height))
            else:
                self.speed = 12.0
                ground_h = self.wm.player.get_ground_height_at(x, y, check_z=self.wm.player.z)
                self.z = ground_h + 0.5
                
                p_x = self.wm.player.x
                p_y = self.wm.player.y
                p_z = self.wm.player.z + 0.3
                
                dist_2d = math.sqrt((p_x - x)**2 + (p_y - y)**2)
                if dist_2d > 0:
                    self.dir_z = (p_z - self.z) / dist_2d
                else:
                    self.dir_z = 0.0

        def update(self, dt):
            distance_to_travel = self.speed * dt
            
            step_size = 0.4
            dist_traveled = 0.0

            while dist_traveled < distance_to_travel:
                step = min(step_size, distance_to_travel - dist_traveled)
                
                self.x += self.dir_x * step
                self.y += self.dir_y * step
                self.z += self.dir_z * step
                dist_traveled += step

                if self.wm.isBlocking(math.floor(self.x), math.floor(self.y), self.z): 
                    return False
                
                ground_h = self.wm.player.get_ground_height_at(self.x, self.y, check_z=self.z)
                if self.z < ground_h:
                    return False

                if not self.fired_by_player:
                    player = self.wm.player
                    if math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2) < 0.5:
                        if self.z >= player.z and self.z <= player.z + 0.9:
                            if not self.wm.builder_mode:
                                player.health -= self.damage
                                self.wm.add_damage_indicator(-self.dir_x, -self.dir_y)
                                self.wm.damage_flash_timer = 0.2
                                self.wm.time_since_last_damage = 0.0
                                renpy.sound.play("sounds/ow.ogg", channel="audio")
                            return False
                else:
                    for enemy in list(self.wm.enemies):
                        if math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2) < 0.5:
                            e_ground = self.wm.player.get_ground_height_at(enemy.x, enemy.y, check_z=enemy.y) # Enemy doesnt have Z, assume ground
                            e_ground = self.wm.player.get_ground_height_at(enemy.x, enemy.y, check_z=self.z) 
                            
                            if self.z >= e_ground and self.z <= e_ground + 0.9:
                                if hasattr(self, 'pitch'):
                                    pass

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
                                        
                                        if self.wm.is_arena_mode:
                                            drop_prob = 1.0 if enemy.coin_index == 12 else 0.35
                                            if renpy.random.random() < drop_prob:
                                                self.wm.sprite_positions.append((enemy.x, enemy.y, enemy.coin_index)) # Coins

                                        # Weapon drops removed as per request (by Fran)
                                        # if not renpy.store.stein_has_shotgun:
                                        #     if renpy.random.random() < (0.25 if enemy.coin_index == 12 else 0.10):
                                        #         self.wm.sprite_positions.append((enemy.x, enemy.y, 13)) # Shotgun
                                        
                                        # if not renpy.store.stein_has_minigun:
                                        #     if renpy.random.random() < 0.10:
                                        #         self.wm.sprite_positions.append((enemy.x, enemy.y, 15)) # Minigun

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
            map_address, _ = self.wm.flat_map_buffer.buffer_info()
            
            
            check_z = self.wm.player.z + 0.5
            
            return stein_core.check_line_of_sight(
                self.x, self.y, check_z,
                target_x, target_y,
                map_address,
                self.wm.mapWidth, self.wm.mapHeight, 
                self.wm.num_layers, self.wm.min_layer
            )

    class Guard(BaseEnemy):
        def __init__(self, wm, x, y, texture_index, destroyed_texture_index, health=100):
            super(Guard, self).__init__(wm, x, y, health)
            self.texture_index = texture_index; self.destroyed_texture_index = destroyed_texture_index
            self.moveSpeed = 1.5; self.damage = 10; self.bullet_texture_index = 6

        def attack(self, player):
            super(Guard, self).attack(player)
            
            dir_x = player.x - self.x
            dir_y = player.y - self.y
            dist = math.sqrt(dir_x**2 + dir_y**2)
            
            if dist > 0:
                dir_x /= dist
                dir_y /= dist
            
            self.wm.spawn_projectile(
                self.x, self.y, self.wm.player.z + 0.5, 
                dir_x, dir_y, 0.0,
                12.0, 
                self.bullet_texture_index, 
                self.damage, 
                False
            )
            
            renpy.sound.play("sounds/e-gunshot.ogg", channel="audio")

    class Yuritler(Guard):
        def __init__(self, wm, x, y, health=150):
            super(Yuritler, self).__init__(wm, x, y, 9, 10, health)
            self.damage = 5; self.moveSpeed = 1.8; self.attack_cooldown = 1.0; self.coin_index = 12
        
        def attack(self, player):
            self.attack_timer = self.attack_cooldown
            dir_x = player.x - self.x
            dir_y = player.y - self.y
            dist = math.sqrt(dir_x**2 + dir_y**2)
            
            if dist > 0:
                base_angle = math.atan2(dir_y, dir_x)
                for i in range(4):
                    offset = (i / 3.0 - 0.5) * 0.2
                    p_dirx = math.cos(base_angle + offset)
                    p_diry = math.sin(base_angle + offset)
                    
                    self.wm.spawn_projectile(
                        self.x, self.y, self.wm.player.z + 0.5,
                        p_dirx, p_diry, 0.0,
                        12.0,
                        self.bullet_texture_index, 
                        self.damage, 
                        False
                    )
            
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
            
            self.wm.spawn_projectile(self.x, self.y, self.wm.player.z + 0.5, dir_x, dir_y, 0.0, 12.0, self.bullet_texture_index, self.damage, False)
            
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
            
            self.flash_base = Transform(Image("pics/items/sight.webp"), size=(512, 512))

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
                
                # Bobbing & Breathing Logic
                offset_x = 0; offset_y = 0
                is_moving = movement_state and movement_state.get('is_moving', False)
                
                if is_moving and self.aim_state in ('hip', 'entering_run', 'running', 'exiting_run'):
                    bob_speed = 15.0 if movement_state.get('is_running', False) else 10.0
                    bob_amp_x = 50.0 if movement_state.get('is_running', False) else 20.0
                    offset_x = math.sin(st * bob_speed) * bob_amp_x
                    offset_y = abs(math.cos(st * bob_speed)) * (bob_amp_x / 2.0)
                
                elif self.aim_state == 'ads':
                    # ADS Breathing
                    breath_speed = 1.5
                    breath_amp_x = 1.5
                    breath_amp_y = 2.5
                    offset_x = math.sin(st * breath_speed) * breath_amp_x
                    # Ensure y offset is always positive (moves down) to avoid revealing bottom cut
                    offset_y = (math.sin(st * breath_speed * 1.1) + 1.0) * 0.5 * breath_amp_y
                    
                elif self.aim_state == 'hip' and not is_moving:
                    # Idle Breathing
                    breath_speed = 2.0
                    breath_amp_x = 4.0
                    breath_amp_y = 6.0
                    offset_x = math.sin(st * breath_speed) * breath_amp_x
                    # Ensure y offset is always positive
                    offset_y = (math.sin(st * breath_speed * 0.95) + 1.0) * 0.5 * breath_amp_y
                
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
                    flash_dur = 1.0
                    
                    if should_flash or (time_diff < flash_dur): 
                        base_x = self.flash_config['offset_ads'][0] if (self.aim_state == 'ads') else self.flash_config['offset_normal'][0]
                        base_y = self.flash_config['offset_ads'][1] if (self.aim_state == 'ads') else self.flash_config['offset_normal'][1]
                        
                        fx = base_x + offset_x
                        fy = base_y + offset_y
                        
                        progress = time_diff / flash_dur
                        
                        f_t = Transform(
                            child=self.flash_base,
                            shader="stein.weapon_fx",
                            u_flash_progress=progress,
                            u_flash_color=self.flash_config['color'],
                            u_flash_angle=self.current_flash_rot,
                            u_heat_distortion=1.0 if getattr(persistent, "stein_heat_distortion", True) else 0.0,
                            u_enable_smoke=1.0 if getattr(persistent, "stein_lighting_quality", 0) == 0 else 0.0,
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
            self.base_displayable = Transform(Image("pics/background.webp"), size=(self.c.internal_width, self.c.internal_height))

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

            renderer = renpy.render(self.base_displayable, width, height, st, at)
            renderer.add_shader("stein.raycaster")

            
            static_count = 0
            for i, sp in enumerate(c.sprite_positions):
                if i >= 50: break
                idx = i * 4
                c.static_data_buffer[idx] = sp[0]
                c.static_data_buffer[idx+1] = sp[1]
                c.static_data_buffer[idx+2] = float(sp[2])
                c.static_data_buffer[idx+3] = 0.0
                static_count += 1

            active_sprites = SteinWrapper.prepare_scene_sprites(
                c.player.x, c.player.y,
                c.proj_ptr, c.MAX_PROJECTILES,
                c.enemy_ptr, len(c.enemies), # Use the main EnemyData* array
                c.static_data_ptr, static_count,
                c.shader_sprite_ptr, 64
            )

            renderer.add_uniform("u_num_active_sprites", active_sprites)
            renderer.add_uniform("u_sprites", c.shader_sprite_buffer)

            # ADS Zoom Logic
            is_aiming = c.is_aiming or c.gp_aiming
            zoom_factor = 0.6 if is_aiming else 1.0
            
            aspect_ratio = float(width) / float(height)
            plane_len = math.sqrt(c.player.planex**2 + c.player.planey**2)
            if plane_len == 0: plane_len = 0.66
            vertical_scale = (aspect_ratio / plane_len) / zoom_factor
            
            plane_x = c.player.planex * zoom_factor
            plane_y = c.player.planey * zoom_factor

            renderer.add_uniform('u_resolution', (float(width), float(height)))
            renderer.add_uniform('u_time', st)
            renderer.add_uniform('u_player_pos', (c.player.x, c.player.y))
            renderer.add_uniform('u_player_dir', (c.player.dirx, c.player.diry))
            renderer.add_uniform('u_player_plane', (plane_x, plane_y))
            renderer.add_uniform('u_pitch', (c.player.pitch / float(height)) + bob_offset)
            renderer.add_uniform('u_z_offset', c.player.z)
            renderer.add_uniform('u_vertical_scale', vertical_scale)
            renderer.add_uniform('u_sky_texture', c.sky_texture)
            renderer.add_uniform('u_volumetric_clouds', 1.0 if persistent.stein_volumetric_clouds else 0.0)
            
            rain_int = 0.0; snow_int = 0.0
            if hasattr(c, 'weather_state'):
                if c.weather_state == "rain": rain_int = 1.0
                elif c.weather_state == "snow": snow_int = 1.0
            renderer.add_uniform('u_rain_intensity', rain_int)
            renderer.add_uniform('u_snow_intensity', snow_int)
            renderer.add_uniform('u_wetness', getattr(c, 'wetness', 0.0))
            
            current_hour = 0.0
            current_ambient = c.lighting_preset['ambient_base']
            current_ambient_near = c.lighting_preset['ambient_near']

            if c.is_arena_mode:
                elapsed_hours = st * 0.04
                current_hour = (c.arena_start_hour + elapsed_hours) % 24.0
                
                def lerp_col(c1, c2, t):
                    return (
                        c1[0] + (c2[0] - c1[0]) * t,
                        c1[1] + (c2[1] - c1[1]) * t,
                        c1[2] + (c2[2] - c1[2]) * t
                    )

                night_amb = (0.05, 0.05, 0.1)
                day_amb = (1.0, 1.0, 1.0)
                sunset_amb = (0.7, 0.6, 0.5)

                if current_hour < 5.0:
                    current_ambient = night_amb
                elif current_hour < 8.0:
                    p = (current_hour - 5.0) / 3.0
                    current_ambient = lerp_col(night_amb, day_amb, p)
                elif current_hour < 16.0:
                    current_ambient = day_amb
                elif current_hour < 19.0:
                    p = (current_hour - 16.0) / 3.0
                    current_ambient = lerp_col(day_amb, sunset_amb, p)
                elif current_hour < 21.0:
                    p = (current_hour - 19.0) / 2.0
                    current_ambient = lerp_col(sunset_amb, night_amb, p)
                else:
                    current_ambient = night_amb
                
                current_ambient_near = (0.0, 0.0, 0.0)
            else:
                current_hour = float(c.lighting_preset.get('time_id', 0.0))
            renderer.add_uniform('u_time_of_day', current_hour)

            renderer.add_uniform('u_ambient_color', current_ambient)
            renderer.add_uniform('u_ambient_near_color', current_ambient_near)

            renderer.add_uniform('u_map_size', (float(c.map_w), float(c.map_h)))
            renderer.add_uniform('u_map_uv_scale', c.map_uv_scale)
            renderer.add_uniform('u_map_texture', c.map_texture)
            renderer.add_uniform('u_map_layer_norm_height', c.map_layer_norm_height)
            renderer.add_uniform('u_map_layer_base_y', float(c.min_layer))
            renderer.add_uniform('u_map_layer_count', float(c.num_layers))
            renderer.add_uniform('u_map_tex_pixel_size', c.map_tex_pixel_size)
            renderer.add_uniform('u_wall_atlas', c.wall_atlas)
            renderer.add_uniform('u_floor_texture', c.floor_texture)
            renderer.add_uniform('u_num_textures', float(c.num_textures))
            renderer.add_uniform('u_sprite_atlas', c.sprite_atlas)
            renderer.add_uniform('u_num_sprite_textures', float(c.num_sprite_textures))

            renderer.add_uniform('u_flashlight_active', 1.0 if c.flashlight_on else 0.0)
            renderer.add_uniform('u_flashlight_bob', (fl_bob_x, fl_bob_y))
            
            renderer.add_uniform('u_soft_shadows', 1.0 if getattr(persistent, "stein_soft_shadows", True) else 0.0)
            renderer.add_uniform('u_enable_shadows', 1.0 if getattr(persistent, "stein_enable_shadows", True) else 0.0)
            renderer.add_uniform('u_max_dist', 500.0 if c.builder_mode else 60.0)
            renderer.add_uniform('u_simple_floor', 1.0 if getattr(persistent, "stein_simple_floor", False) else 0.0)
            
            # Flash
            import time
            current_weapon = c.weapons[c.player.current_weapon_name]
            flash_intensity = 0.0
            if current_weapon.projectile_type and (time.time() - current_weapon.last_fired) < 0.1:
                flash_intensity = 1.0 - ((time.time() - current_weapon.last_fired) / 0.1)
            renderer.add_uniform('u_flash_intensity', flash_intensity)
            renderer.add_uniform('u_flash_color', (1.0, 0.8, 0.4))

            renderer.add_uniform('u_light_positions', [0.0] * 64)
            renderer.add_uniform('u_num_active_lights', 0.0)

            renpy.redraw(self, 0.000001)
            return renderer

    class GPURenpystein(renpy.Displayable):
        def __init__(self, width, height, worldMap, exits=[], internal_width=None, internal_height=None, lighting_preset=None, **kwargs):
            super(GPURenpystein, self).__init__(**kwargs)
            self.width = width
            self.height = height
            self.map_data = worldMap
            self.worldMap = worldMap 
            
            if isinstance(worldMap, dict):
                max_x = 0
                max_y = 0
                for grid in worldMap.values():
                    if len(grid) > max_x: max_x = len(grid)
                    if len(grid) > 0 and len(grid[0]) > max_y: max_y = len(grid[0])
                self.mapWidth = max_x
                self.mapHeight = max_y
            else:
                self.mapWidth = len(worldMap)
                self.mapHeight = len(worldMap[0]) if self.mapWidth > 0 else 0
            
            self.map_w = self.mapWidth
            self.map_h = self.mapHeight
            
            self.lighting_preset = lighting_preset if lighting_preset else {
                'ambient_base': (0.02, 0.02, 0.05),
                'ambient_near': (0.05, 0.05, 0.08),
                'sky_texture': "pics/background.webp",
                'time_id': 0.0
            }

            self.is_arena_mode = getattr(renpy.store, 'is_arena_mode', False)

            self.arena_start_hour = 12.0
            if self.is_arena_mode:
                roll = renpy.random.random()
                if roll < 0.33:
                    self.arena_start_hour = 12.0 # Day
                elif roll < 0.66:
                    self.arena_start_hour = 18.0 # Sunset
                else:
                    self.arena_start_hour = 2.0 # Night

            self.weather_state = "none"
            self.weather_timer = 0.0
            self.next_weather_check = 5.0
            self.wetness = 0.0

            self.fps_frame_count = 0
            self.fps_timer_accum = 0.0

            self.exits = exits
            
            self.internal_width = internal_width if internal_width is not None else width
            self.internal_height = internal_height if internal_height is not None else height
            self.damage_flash_timer = 0.0
            self.return_value = None
            self.heal_flash_timer = 0.0
            self.hit_marker_timer = 0.0
            self.damage_indicators = []
            self.time_since_last_damage = 0.0
            
            self.pickup_msg = ""
            self.pickup_msg_timer = 0.0
            
            self.map_texture = self.create_map_texture()
            self.wall_atlas, self.num_textures = self.create_wall_atlas()
            self.floor_texture = self.load_floor_texture()
            self.sprite_atlas, self.num_sprite_textures = self.create_sprite_atlas()
            self.solid_base = renpy.display.imagelike.Solid("#000", xsize=width, ysize=height)
            
            sky_path = self.lighting_preset.get('sky_texture', "pics/background.webp")
            try:
                with renpy.open_file(sky_path) as f:
                    bg_surf = pygame.image.load(f).convert_alpha()
            except:
                # Fallback
                with renpy.open_file("pics/background.webp") as f:
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
            self.kb_fly_up = False
            self.kb_fly_down = False
            self.builder_mode = False
            self.selected_voxel = 1
            
            if config.developer:
                self.builder_mode = True
                self.player.fly_mode = True
                self.pickup_msg = "BUILDER MODE ON (DEV)"
                self.pickup_msg_timer = 3.0
            
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
            # Damage upgrades removed as per request
            # if self.is_arena_mode:
            #     self.gun_dmg += 50 * (persistent.stein_pistol_level * 0.01)
            #     self.shotgun_dmg += 35 * (persistent.stein_shotgun_level * 0.01)
            #     self.minigun_dmg += 3 * (persistent.stein_minigun_level * 0.10)

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

            register_weapon(Weapon("shotgun", SLOT_LONG, damage=self.shotgun_dmg, projectile_type='shotgun', cooldown=1.4, flash_offset=(75, -260), flash_ads_offset=(0, -340), flash_size=1.0, ads_idle="pics/weapons/shotgun_ads1.webp",
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
            self.sight_d = Image("pics/items/sight.webp")
            with renpy.open_file("pics/gui/damage_x.webp") as f:
                self.hit_marker_img = pygame.image.load(f).convert_alpha()
            with renpy.open_file("pics/gui/arrow_d.webp") as f:
                arrow_surf = pygame.image.load(f).convert_alpha()
            self.arrow_img = pygame.transform.scale(arrow_surf, (30, 30))

            self.max_entities = 1024
            
            self.max_enemies = 1024
            self.enemy_array = (EnemyData * self.max_enemies)()
            self.enemy_ptr = ctypes.addressof(self.enemy_array)
            ctypes.memset(self.enemy_ptr, 0, ctypes.sizeof(self.enemy_array))

            self.player_data = PlayerData()
            self.player_ptr = ctypes.addressof(self.player_data)

            self.sort_buffer = (ctypes.c_int * self.max_entities)()
            
            self.shader_sprite_buffer = (ctypes.c_float * 256)()
            
            self.entities_buffer = (ctypes.c_double * (self.max_entities * 4))()
            self.entities_ptr = ctypes.addressof(self.entities_buffer)
            
            self.shader_sprite_ptr = ctypes.addressof(self.shader_sprite_buffer)

            self.sort_ptr = ctypes.addressof(self.sort_buffer)

            self.MAX_PROJECTILES = 256
            self.proj_array = (ProjectileData * self.MAX_PROJECTILES)()
            self.proj_ptr = ctypes.addressof(self.proj_array)

            self.enemy_data_buffer = (ctypes.c_double * (50 * 4))() 
            self.enemy_data_ptr = ctypes.addressof(self.enemy_data_buffer)
            
            self.static_data_buffer = (ctypes.c_double * (50 * 4))()
            self.static_data_ptr = ctypes.addressof(self.static_data_buffer)
            
            for i in range(self.MAX_PROJECTILES):
                self.proj_array[i].active = 0

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

        def spawn_projectile(self, x, y, z, dx, dy, dz, speed, tex_id, damage, is_player, pitch=0.0):
            for i in range(self.MAX_PROJECTILES):
                if self.proj_array[i].active == 0:
                    p = self.proj_array[i]
                    p.x = x; p.y = y; p.z = z
                    p.dir_x = dx; p.dir_y = dy; p.dir_z = dz
                    p.speed = speed
                    p.texture_idx = tex_id
                    p.damage = damage
                    p.from_player = 1 if is_player else 0
                    p.pitch = pitch
                    p.active = 1
                    return

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
                "pics/items/barrel.webp", "pics/items/pillar.webp",
                "pics/items/greenlight.webp", "pics/items/pillar_destroyed.webp",
                "pics/enemies/guard.webp",
                "pics/enemies/guard_d.webp",
                "pics/items/bullet.webp",
                "pics/items/medkit.webp",
                "pics/items/cookie.webp",
                "pics/enemies/yuritler.webp",
                "pics/enemies/yuritler_d.webp",
                "pics/items/coins.webp",
                "pics/items/coins.webp", 
                "pics/items/random_gun_i.webp",
                "pics/items/bullet_red.webp",
                "pics/items/minigun.webp",
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
            
            if isinstance(self.map_data, list):
                layers = {0: self.map_data}
            else:
                layers = self.map_data

            # Find max dimensions
            max_x = 0
            max_y = 0
            min_z = 0
            max_z = 0
            
            if layers:
                min_z = min(layers.keys())
                max_z = max(layers.keys())
                for z, grid in layers.items():
                    if len(grid) > max_x: max_x = len(grid)
                    if len(grid) > 0 and len(grid[0]) > max_y: max_y = len(grid[0])
            
            self.map_w = max_x
            self.map_h = max_y
            self.min_layer = min_z
            self.max_layer = max_z
            self.num_layers = max_z - min_z + 1

            self.flat_map_buffer = flatten_world_map(
                self.worldMap, self.mapWidth, self.mapHeight, 
                self.min_layer, self.max_layer
            )
            
            layer_h_pixels = next_power_of_two(max_y)
            w_pot = max(64, next_power_of_two(max_x))
            h_pot = max(64, next_power_of_two(layer_h_pixels * self.num_layers))

            surf = pygame.Surface((w_pot, h_pot), flags=pygame.SRCALPHA, depth=32)
            surf.fill((0,0,0,255))
            
            for z, grid in layers.items():
                layer_idx = z - min_z
                base_y = layer_idx * layer_h_pixels
                
                for map_x, row in enumerate(grid):
                    for map_y, tile in enumerate(row):
                        if tile > 0:
                            surf.set_at((map_x, base_y + map_y), (255, tile, 0, 255))
            
            tex = renpy.display.draw.load_texture(surf)
            
            # Calculate uniforms
            self.map_layer_norm_height = float(layer_h_pixels) / float(h_pot)
            self.map_tex_pixel_size = (1.0 / float(w_pot), 1.0 / float(h_pot))
            
            self.map_uv_scale = (float(max_x) / float(w_pot), float(max_y) / float(layer_h_pixels)) 
            
            return tex

        def render(self, width, height, st, at):
            if self.oldst is None: self.oldst = st
            dtime = st - self.oldst
            self.oldst = st

            if dtime > 0.0:
                inst_fps = 1.0 / dtime
                
                current_fps = getattr(renpy.store, 'stein_current_fps', 60)
                new_fps = (current_fps * 0.9) + (inst_fps * 0.1)
                renpy.store.stein_current_fps = int(new_fps)

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
            
            scale = float(width) / float(self.internal_width)

            if self.last_rot is None:
                self.last_rot = self.player.rot

            diff_rot = self.player.rot - self.last_rot
            
            if diff_rot > math.pi: 
                diff_rot -= (math.pi * 2)
            elif diff_rot < -math.pi: 
                diff_rot += (math.pi * 2)

            mb_strength = getattr(persistent, "stein_motion_blur_strength", 0.0)
            
            blur_amount = -diff_rot * mb_strength * 10.0 

            self.last_rot = self.player.rot

            # Flatten the raycast layer
            flat_layer = renpy.display.layout.Flatten(self.raycast_layer)
            
            args_blur = { 'child': flat_layer, 'zoom': 1.0 } 
            
            if abs(blur_amount) > 0.005:
                args_blur['shader'] = "stein.motion_blur"
                args_blur['u_blur_amount'] = blur_amount
            
            blur_transform = Transform(**args_blur)

            if abs(blur_amount) > 0.005:
                blur_transform = renpy.display.layout.Flatten(blur_transform)

            use_bloom = getattr(persistent, "stein_enable_bloom", True)
            
            args_bloom = { 'child': blur_transform, 'zoom': scale, 'nearest': True }
            
            if use_bloom:
                args_bloom['shader'] = "stein.bloom"
                args_bloom['u_resolution'] = (float(width), float(height))

            final_transform = Transform(**args_bloom)
            
            main_scene_render = renpy.render(final_transform, width, height, st, at)
            
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
            
            if self.builder_mode:
                info_str = f"BUILDER MODE ON [[VOXEL: {self.selected_voxel}]]\COORDS: {self.player.x:.2f}, {self.player.y:.2f}, {self.player.z:.2f}"
                b_text = Text(info_str, size=30, color="#00FF00", outlines=[(2, "#000", 0, 0)])
                b_r = renpy.render(b_text, width, height, st, at)
                r.blit(b_r, (20, 20))

            if self.return_value:
                renpy.timeout(0)

            renpy.redraw(self, 0.01) 
            return r

        def update_weather(self, dt):
            if not hasattr(self, 'weather_state'):
                self.weather_state = "none"
                self.weather_timer = 0.0
                self.next_weather_check = 5.0
                self.wetness = 0.0

            if not self.is_arena_mode: return
            
            if not persistent.stein_volumetric_clouds or not getattr(persistent, "stein_enable_weather", True):
                self.weather_state = "none"
                self.wetness = max(0.0, self.wetness - dt * 0.1)
                return

            game_hours_passed = dt * 0.04
            
            if self.weather_state != "none":
                self.weather_timer -= game_hours_passed
                self.wetness = min(1.0, self.wetness + dt * 0.2)
                
                if self.weather_timer <= 0:
                    self.weather_state = "none"
            else:
                self.wetness = max(0.0, self.wetness - dt * 0.05)
            
            self.next_weather_check -= game_hours_passed
            if self.next_weather_check <= 0:
                if config.developer:
                    self.next_weather_check = 1.0
                else:
                    self.next_weather_check = 5.0 
                
                if self.weather_state == "none":
                    prob = 0.10
                    if config.developer: prob = 1.0
                    
                    if renpy.random.random() < prob:
                        if renpy.random.random() < 0.5:
                            self.weather_state = "rain"
                        else:
                            self.weather_state = "snow"
                        
                        self.weather_timer = 6.0

        def update_logic(self, dt):
            self.time_since_last_damage += dt
            if self.time_since_last_damage > 2.5 and self.player.health < 100 and self.player.health > 0:
                # Regenerate 95 HP in 3 seconds, like 31.67 hp/sec
                heal_rate = 31.67
                self.player.health = min(100, self.player.health + heal_rate * dt)

            self.update_weather(dt)
            self.hit_marker_timer = max(0, self.hit_marker_timer - dt)
            self.check_item_pickup()
            
            c_enemies = self.enemy_array
            active_count = 0
            state_map = {'idle': 0, 'chasing': 1, 'attacking': 2, 'dying': 3, 'dead': 4}

            for i, e in enumerate(self.enemies):
                if i >= self.max_enemies: break
                c_enemies[i].x = e.x
                c_enemies[i].y = e.y
                c_enemies[i].z = getattr(e, 'z', 0.0) 
                c_enemies[i].hp = e.health
                c_enemies[i].state = state_map.get(e.state, 0)
                c_enemies[i].texture_idx = e.texture_index
                c_enemies[i].move_speed = e.moveSpeed
                c_enemies[i].enemy_type = 0 
                active_count += 1

            map_addr, _ = self.flat_map_buffer.buffer_info()
            SteinWrapper.stein_lib.update_enemies_c(
                self.enemy_ptr,
                active_count,
                self.player.x, self.player.y, self.player.z,
                dt,
                map_addr,
                self.mapWidth, self.mapHeight, self.num_layers, self.min_layer
            )

            state_map_inv = {0: 'idle', 1: 'chasing', 2: 'attacking', 3: 'dying', 4: 'dead'}
            
            for i in range(active_count):
                e = self.enemies[i]
                c_e = c_enemies[i]
                
                e.x = c_e.x
                e.y = c_e.y
                e.health = c_e.hp
                e.state = state_map_inv.get(c_e.state, 'idle')
                
                if c_e.state == 2 and e.attack_timer <= 0:
                    pass

                if e.state == 'attacking':
                    if e.attack_timer <= 0:
                        e.attack(self.player)

            for e in self.enemies:
                if e.attack_timer > 0:
                    e.attack_timer -= dt
            
            SteinWrapper.update_projectiles_native(
                self.proj_ptr, self.MAX_PROJECTILES, dt,
                map_addr, self.mapWidth, self.mapHeight, 
                self.num_layers, self.min_layer
            )

            for i in range(self.MAX_PROJECTILES):
                p = self.proj_array[i]
                if p.active == 0: continue
                
                if p.from_player == 1:
                    for e in list(self.enemies):
                        dist_sq = (e.x - p.x)**2 + (e.y - p.y)**2
                        if dist_sq < 0.25:
                            e.health -= p.damage
                            self.hit_marker_timer = 0.15
                            renpy.sound.play("sounds/ow.ogg", channel="audio")
                            p.active = 0 
                            
                            if e.health <= 0:
                                if e in self.enemies: self.enemies.remove(e)
                                self.sprite_positions.append((e.x, e.y, e.destroyed_texture_index))
                            break 
                else:
                    dx = self.player.x - p.x
                    dy = self.player.y - p.y
                    dist_sq = dx*dx + dy*dy
                    
                    if dist_sq < 0.25:
                        # Check Z height
                        if p.z >= self.player.z and p.z <= self.player.z + 1.0:
                            if not self.builder_mode:
                                self.player.health -= p.damage
                                self.add_damage_indicator(-p.dir_x, -p.dir_y)
                                self.damage_flash_timer = 0.2
                                self.time_since_last_damage = 0.0
                                renpy.sound.play("sounds/ow.ogg", channel="audio")
                            p.active = 0

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
                    elif texture_index == 13:
                        w_obj = self.weapon_library["shotgun"]
                        has_shotgun = renpy.store.stein_has_shotgun or (self.inventory[w_obj.category] and self.inventory[w_obj.category].name == "shotgun")
                        
                        if not has_shotgun:
                            if self.is_arena_mode:
                                self.equip_weapon("shotgun")
                            else:
                                renpy.store.stein_has_shotgun = True
                            
                            picked = True
                            self.pickup_msg = "SHOTGUN ACQUIRED"
                            self.pickup_msg_timer = 3.0

                    elif texture_index == 15:
                        w_obj = self.weapon_library["minigun"]
                        has_minigun = renpy.store.stein_has_minigun or (self.inventory[w_obj.category] and self.inventory[w_obj.category].name == "minigun")
                        
                        if not has_minigun:
                            if self.is_arena_mode:
                                self.equip_weapon("minigun")
                            else:
                                renpy.store.stein_has_minigun = True
                            
                            picked = True
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
            
            speed = 100.0
            dz = pitch / float(self.height)
            z_start = self.player.z + 0.5

            if weapon.projectile_type == 'shotgun':
                import random
                spread_mult = 0.1 if is_ads else 0.2
                for _ in range(5):
                    spread = (random.random() - 0.5) * spread_mult
                    angle = self.player.rot + spread
                    pdx = math.cos(angle)
                    pdy = math.sin(angle)
                    self.spawn_projectile(self.player.x, self.player.y, z_start, pdx, pdy, dz, speed, self.bullet_texture_index, weapon.damage, True, pitch=pitch)
                renpy.sound.play("sounds/shotgun.ogg", channel="audio")
            elif weapon.projectile_type == 'bullet':
                self.spawn_projectile(self.player.x, self.player.y, z_start, dx, dy, dz, speed, self.bullet_texture_index, weapon.damage, True, pitch=pitch)
                renpy.sound.play("sounds/gunshot.ogg", channel="audio")
            else:
                dir_z = -math.sin(self.player.pitch / float(self.height)) # Approximation
                dir_z = (self.player.pitch / float(self.height)) 

                hit_index = SteinWrapper.stein_lib.check_hitscan_c(
                    self.player.x, self.player.y, self.player.z + 0.5,
                    dx, dy, dir_z,
                    self.enemy_ptr,
                    len(self.enemies),
                    100.0,
                    float(weapon.damage)
                )

                if hit_index != -1:
                    e = self.enemies[hit_index]
                    
                    c_enemies = self.enemy_array
                    e.health = c_enemies[hit_index].hp
                    
                    self.hit_marker_timer = 0.15
                    
                    if e.health <= 0:
                        renpy.sound.play("sounds/ow.ogg", channel="audio")
                        if self.is_arena_mode:
                            persistent.stein_kills += 1
                        
                        if e in self.enemies:
                            self.enemies.remove(e)
                        
                        self.sprite_positions.append((e.x, e.y, e.destroyed_texture_index))
                        
                                    
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

        def add_damage_indicator(self, source_dir_x, source_dir_y):
            angle = math.atan2(source_dir_y, source_dir_x)
            self.damage_indicators.append(DamageIndicator(angle))

        def isBlocking(self, x, y, z=0.0):
            if x < 0 or x >= self.mapWidth or y < 0 or y >= self.mapHeight: return True
            
            layer = int(math.floor(z))
            tile = 0
            
            if isinstance(self.worldMap, dict):
                if layer in self.worldMap:
                    grid = self.worldMap[layer]
                    if int(x) < len(grid) and int(y) < len(grid[int(x)]):
                        tile = grid[int(x)][int(y)]
            else:
                if layer == 0:
                    tile = self.worldMap[int(x)][int(y)]
            
            if tile == 0: return False
            
            h = 1.0
            if tile == 20: h = 0.5
            
            local_z = z - float(layer)
            if local_z >= h: return False
            
            return True

        def checkCollision(self, fromX, fromY, toX, toY, radius, z=0.0):
            # Check center
            if self.isBlocking(math.floor(toX), math.floor(toY), z):
                return [fromX, fromY]
            
            # Check radius
            points = [
                (toX + radius, toY), (toX - radius, toY),
                (toX, toY + radius), (toX, toY - radius)
            ]
            
            for px, py in points:
                if self.isBlocking(math.floor(px), math.floor(py), z):
                    return [fromX, fromY]
            
            return [toX, toY]

        def isVoxel(self, x, y, z):
            if x < 0 or x >= self.mapWidth or y < 0 or y >= self.mapHeight: return False
            
            layer = int(math.floor(z))
            tile = 0
            
            if isinstance(self.worldMap, dict):
                if layer in self.worldMap:
                    grid = self.worldMap[layer]
                    if int(x) < len(grid) and int(y) < len(grid[int(x)]):
                        tile = grid[int(x)][int(y)]
            else:
                if layer == 0:
                    tile = self.worldMap[int(x)][int(y)]
            
            return tile > 0

        def cast_ray(self, start_x, start_y, start_z, dir_x, dir_y, dir_z, max_dist=10.0):
            map_address, _ = self.flat_map_buffer.buffer_info()
            
            # Call to cpp
            return stein_core.cast_ray_fast(
                start_x, start_y, start_z, 
                dir_x, dir_y, dir_z, 
                map_address, 
                self.mapWidth, self.mapHeight, self.num_layers, self.min_layer,
                max_dist
            )

        def handle_builder_action(self, action):
            u_pitch = self.player.pitch / float(self.height)
            pitch_angle = math.atan(u_pitch)
            
            cp = math.cos(pitch_angle)
            sp = math.sin(pitch_angle)
            
            px = self.player.planex
            py = self.player.planey
            plen = math.sqrt(px*px + py*py)
            if plen == 0: plen = 1.0
            rx = px / plen
            ry = py / plen
            
            bx = self.player.dirx
            by = self.player.diry
            
            cz = rx*by - ry*bx
            dot_rb = rx*bx + ry*by
            
            rdx = bx * cp + 0.0 * sp + rx * dot_rb * (1.0 - cp)
            rdy = by * cp + 0.0 * sp + ry * dot_rb * (1.0 - cp)
            rdz = 0.0 * cp + cz * sp + 0.0 * dot_rb * (1.0 - cp)
            
            rdx = bx * cp + 0.0 + rx * dot_rb * (1.0 - cp)
            rdy = by * cp + 0.0 + ry * dot_rb * (1.0 - cp)
            rdz = 0.0 + cz * sp + 0.0
            
            # Normalize
            rlen = math.sqrt(rdx*rdx + rdy*rdy + rdz*rdz)
            if rlen > 0:
                rdx /= rlen
                rdy /= rlen
                rdz /= rlen
            
            res = self.cast_ray(self.player.x, self.player.y, self.player.z + 0.5, rdx, rdy, rdz, max_dist=100.0)
            
            if res[0]: 
                mx, my, mz, side, sx, sy, sz = res[1:]
                
                if action == 'remove':
                    self.set_voxel(mx, my, mz, 0)
                elif action == 'place':
                    nx, ny, nz = mx, my, mz
                    if side == 0: nx -= sx
                    elif side == 1: ny -= sy
                    elif side == 2: nz -= sz
                    
                    if math.floor(self.player.x) == nx and math.floor(self.player.y) == ny and math.floor(self.player.z) == nz:
                        return
                    
                    self.set_voxel(nx, ny, nz, self.selected_voxel)
            else:
                if action == 'place':
                    nx = int(math.floor(self.player.x))
                    ny = int(math.floor(self.player.y))
                    nz = int(math.floor(self.player.z))
                    self.set_voxel(nx, ny, nz, self.selected_voxel)

        def shift_map(self, off_x, off_y):
            self.mapWidth += off_x
            self.mapHeight += off_y
            self.map_w = self.mapWidth
            self.map_h = self.mapHeight
            
            for z, grid in self.worldMap.items():
                curr_w = len(grid)
                curr_h = len(grid[0]) if curr_w > 0 else 0
                
                if off_x > 0:
                    new_cols = [[0] * curr_h for _ in range(off_x)]
                    for col in reversed(new_cols):
                        grid.insert(0, col)
                
                if off_y > 0:
                    for col in grid:
                        for _ in range(off_y):
                            col.insert(0, 0)
            
            self.player.x += off_x
            self.player.y += off_y
            
            for e in self.enemies:
                e.x += off_x
                e.y += off_y
                if hasattr(e, 'last_known_x') and e.last_known_x is not None: e.last_known_x += off_x
                if hasattr(e, 'last_known_y') and e.last_known_y is not None: e.last_known_y += off_y
            
            for p in self.projectiles:
                p.x += off_x
                p.y += off_y
            
            new_sprites = []
            for s in self.sprite_positions:
                l = list(s)
                l[0] += off_x
                l[1] += off_y
                new_sprites.append(tuple(l))
            self.sprite_positions = new_sprites
            
            new_spawns = []
            for s in self.spawn_points:
                new_spawns.append((s[0] + off_x, s[1] + off_y))
            self.spawn_points = new_spawns
            
            new_exits = []
            for e in self.exits:
                l = list(e)
                l[0] += off_x
                l[1] += off_y
                new_exits.append(tuple(l))
            self.exits = new_exits
            
            self.pickup_msg = f"MAP SHIFTED BY {off_x}, {off_y}"
            self.pickup_msg_timer = 2.0

        def set_voxel(self, x, y, z, val):
            map_changed = False
            if not isinstance(self.worldMap, dict):
                new_map = {0: [row[:] for row in self.worldMap]}
                self.worldMap = new_map
                self.map_data = new_map
            
            off_x = 0
            off_y = 0
            if x < 0:
                off_x = abs(x)
                x = 0
            if y < 0:
                off_y = abs(y)
                y = 0
            
            if off_x > 0 or off_y > 0:
                self.shift_map(off_x, off_y)
                map_changed = True
            
            # Check for expansion
            if x >= self.mapWidth or y >= self.mapHeight:
                new_w = max(self.mapWidth, x + 1)
                new_h = max(self.mapHeight, y + 1)
                self.expand_map(new_w, new_h)
                map_changed = True

            if z not in self.worldMap:
                if val == 0: 
                    if map_changed: self.map_texture = self.create_map_texture()
                    return 
                self.worldMap[z] = [[0 for _ in range(self.mapHeight)] for _ in range(self.mapWidth)]
            
            grid = self.worldMap[z]
            if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
                grid[x][y] = val
                map_changed = True

                if 0 <= x < self.mapWidth and 0 <= y < self.mapHeight:
                    layer_idx = z - self.min_layer
                    if 0 <= layer_idx < self.num_layers:
                        idx = (layer_idx * self.mapWidth * self.mapHeight) + (x * self.mapHeight) + y
                        self.flat_map_buffer[idx] = val
                
            if map_changed:
                self.map_texture = self.create_map_texture()

        def expand_map(self, new_w, new_h):
            self.mapWidth = new_w
            self.mapHeight = new_h
            self.map_w = new_w
            self.map_h = new_h
            
            for z, grid in self.worldMap.items():
                current_w = len(grid)
                current_h = len(grid[0]) if current_w > 0 else 0
                
                # Resize width
                if new_w > current_w:
                    for _ in range(new_w - current_w):
                        grid.append([0] * current_h)
                
                # Resize height
                for row in grid:
                    if new_h > len(row):
                        row.extend([0] * (new_h - len(row)))
            
            self.pickup_msg = f"MAP EXPANDED TO {new_w}x{new_h}"
            self.pickup_msg_timer = 2.0

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
                if config.developer:
                    if ev.key == pygame.K_o:
                        self.builder_mode = not self.builder_mode
                        self.player.fly_mode = self.builder_mode
                        if self.builder_mode:
                            self.pickup_msg = "BUILDER MODE ON"
                            self.pickup_msg_timer = 2.0
                        else:
                            self.pickup_msg = "BUILDER MODE OFF"
                            self.pickup_msg_timer = 2.0

                    if ev.key == pygame.K_p:
                        print("--- LEVEL DATA START ---")
                        if isinstance(self.worldMap, dict):
                            print("{")
                            for z in sorted(self.worldMap.keys()):
                                print(f"    {z}: [")
                                for row in self.worldMap[z]:
                                    print(f"        {repr(row)},")
                                print("    ],")
                            print("}")
                        else:
                            print("[")
                            for row in self.worldMap:
                                print(f"    {repr(row)},")
                            print("]")
                        print("--- LEVEL DATA END ---")
                        self.pickup_msg = "LEVEL DATA PRINTED"
                        self.pickup_msg_timer = 2.0

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
                
                if ev.key == pygame.K_SPACE: 
                    if self.player.fly_mode: self.kb_fly_up = True
                    else: self.player.trigger_jump()
                
                if ev.key == pygame.K_LCTRL or ev.key == pygame.K_RCTRL:
                    self.kb_running = True

                if ev.key == pygame.K_n:
                    if self.player.fly_mode: self.kb_fly_down = True

            if ev.type == pygame.MOUSEBUTTONDOWN:
                if self.builder_mode:
                    if ev.button == 1: # Left Click - Place
                        self.handle_builder_action('place')
                    elif ev.button == 3: # Right Click - Remove
                        self.handle_builder_action('remove')
                    elif ev.button == 4: # Wheel Up
                        self.selected_voxel = (self.selected_voxel % 9) + 1
                        self.pickup_msg = f"VOXEL: {self.selected_voxel}"
                        self.pickup_msg_timer = 1.0
                    elif ev.button == 5: # Wheel Down
                        self.selected_voxel = ((self.selected_voxel - 2) % 9) + 1
                        self.pickup_msg = f"VOXEL: {self.selected_voxel}"
                        self.pickup_msg_timer = 1.0
                    
                    return 

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
                if ev.key == pygame.K_SPACE: self.kb_fly_up = False
                if ev.key in (pygame.K_w, pygame.K_s, pygame.K_UP, pygame.K_DOWN): self.kb_speed = 0.0
                if ev.key in (pygame.K_a, pygame.K_d): self.kb_strafe = 0.0
                if ev.key in (pygame.K_LEFT, pygame.K_RIGHT): self.kb_dir = 0.0
                if ev.key in (pygame.K_LCTRL, pygame.K_RCTRL): 
                    self.kb_running = False
                
                if ev.key == pygame.K_n:
                    self.kb_fly_down = False

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
                    if renpy.android:
                        if joy.get_numbuttons() > 9 and joy.get_button(9): self.gp_running = True
                    else:
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

                    if renpy.android:
                        if joy.get_numbuttons() > 11 and joy.get_button(11):
                            btn_flashlight_held = True
                    elif joy.get_numhats() > 0:
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
