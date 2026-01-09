# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
# cython: initializedcheck=False

"""
Module: stein_core
==================

Description:
    High-performance, native Raycasting and Voxel rendering engine designed for RenPy.
    This module handles computationally intensive tasks (DDA algorithm, collision detection)
    outside the Python interpreter to ensure stable 60+ FPS on mobile and desktop platforms.

Architecture: "Standalone Shared Library" Pattern
-------------------------------------------------
    Unlike traditional Python Extensions (.pyd/.so linked against libpython), this module is 
    compiled as a standalone C shared library. It does not initialize a Python module structure 
    (PyModuleDef) nor interacts with the Python C-API during execution.

    Integration is achieved via Python's 'ctypes' foreign function interface (FFI), treating 
    this module strictly as a dynamic binary library (DLL/Shared Object).

Design Rationale:
    1. Android/RAPT Compatibility:
       RenPy on Android uses a highly customized Python environment. Standard Cython modules 
       often trigger SIGSEGV errors (in 'sem_wait' / 'PyThread_acquire_lock') due to Global 
       Interpreter Lock (GIL) state mismatches during module initialization.
       By bypassing 'PyInit' and the Python C-API entirely, we eliminate ABI conflicts.

    2. Cross-Platform ABI:
       This architecture allows the same rendering logic to be compiled with MSVC (Windows) 
       and CMake/NDK (Android) without version-specific dependencies (e.g., python3.10 vs 3.12),
       as the interface relies solely on C primitives.

Implementation Guidelines:
--------------------------
    * Type Safety: Public functions ('cdef public') must exclusively use standard C types 
      ('int', 'ouble', 'void'). Usage of Python objects ('PyObject*', 'list', 'tuple') or 
      Cython MemoryViews in the public interface is strictly prohibited to prevent GIL acquisition.

    * Memory Addressing: All memory pointers passed from Python must be typed as 'size_t'
      (defined in 'libc.stddef'). Do not use 'long' or 'int' for pointers, as this causes 
      heap corruption on LLP64 architectures (specifically Windows x64).

    * Data Output: Functions should return 'void' or primitive scalars. Complex data 
      structures must be populated via pointer arguments (pass-by-reference buffers) pre-allocated 
      by the host Python application.

Build Instructions:
-------------------
    1. Source Generation:
       $ python -m cython -3 stein_core.pyx -o stein_core.c

    2. Compilation (Windows - MSVC):
       Requires 'stein_core.def' for explicit symbol export.
       $ cl /LD /O2 /Tc stein_core.c /I "PATH_TO_INCLUDE" /link /LIBPATH:"PATH_TO_LIBS" /DEF:stein_core.def

    3. Compilation (Android - CMake):
       Target as a standard shared library. Do not link against 'libpython'. 
       Use flag: `-Wl,` (if necessary).
    
    You can see an example in game/core/notes.txt
"""

from libc.math cimport floor, abs, sqrt, cos, sin
from libc.stddef cimport size_t
from libc.stdlib cimport qsort


cdef public void cast_ray_c(
    double start_x, double start_y, double start_z, 
    double dir_x, double dir_y, double dir_z, 
    size_t flat_map_addr, 
    int map_w, int map_h, int map_layers, int min_layer,
    double max_dist,
    size_t out_addr
):
    cdef int* flat_map = <int*>flat_map_addr
    cdef int* output = <int*>out_addr
    
    output[0] = 0
    
    cdef int map_x = <int>floor(start_x)
    cdef int map_y = <int>floor(start_y)
    cdef int map_z = <int>floor(start_z)
    cdef double delta_dist_x = abs(1.0 / dir_x) if dir_x != 0 else 1e30
    cdef double delta_dist_y = abs(1.0 / dir_y) if dir_y != 0 else 1e30
    cdef double delta_dist_z = abs(1.0 / dir_z) if dir_z != 0 else 1e30
    cdef int step_x = 1 if dir_x > 0 else -1
    cdef int step_y = 1 if dir_y > 0 else -1
    cdef int step_z = 1 if dir_z > 0 else -1
    cdef double side_dist_x, side_dist_y, side_dist_z
    
    if dir_x > 0: side_dist_x = (map_x + 1.0 - start_x) * delta_dist_x
    else:         side_dist_x = (start_x - map_x) * delta_dist_x
    if dir_y > 0: side_dist_y = (map_y + 1.0 - start_y) * delta_dist_y
    else:         side_dist_y = (start_y - map_y) * delta_dist_y
    if dir_z > 0: side_dist_z = (map_z + 1.0 - start_z) * delta_dist_z
    else:         side_dist_z = (start_z - map_z) * delta_dist_z

    cdef double dist = 0.0
    cdef int side = 0
    cdef int idx = 0
    cdef int layer_offset = 0
    cdef int hit = 0
    
    while dist < max_dist:
        if side_dist_x < side_dist_y:
            if side_dist_x < side_dist_z:
                dist = side_dist_x
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                dist = side_dist_z
                side_dist_z += delta_dist_z
                map_z += step_z
                side = 2
        else:
            if side_dist_y < side_dist_z:
                dist = side_dist_y
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            else:
                dist = side_dist_z
                side_dist_z += delta_dist_z
                map_z += step_z
                side = 2
        
        if map_x < 0 or map_x >= map_w or map_y < 0 or map_y >= map_h:
            continue
        
        layer_offset = map_z - min_layer
        if layer_offset >= 0 and layer_offset < map_layers:
            idx = (layer_offset * map_w * map_h) + (map_x * map_h) + map_y
            if flat_map[idx] > 0:
                hit = 1
                break

    if hit:
        output[0] = 1
        output[1] = map_x
        output[2] = map_y
        output[3] = map_z
        output[4] = side
        output[5] = step_x
        output[6] = step_y
        output[7] = step_z


cdef inline bint is_wall(int x, int y, int z, int w, int h, int layers, int min_layer, int* flat_map):
    if x < 0 or x >= w or y < 0 or y >= h: return 1
    cdef int layer_offset = z - min_layer
    if layer_offset < 0 or layer_offset >= layers: return 0 
    cdef int idx = (layer_offset * w * h) + (x * h) + y
    return flat_map[idx] > 0

cdef public void resolve_movement_c(
    double x, double y, double z,
    double dx, double dy, 
    double radius,
    size_t flat_map_addr, 
    int w, int h, int layers, int min_layer,
    size_t out_addr
):
    cdef int* flat_map = <int*>flat_map_addr
    cdef double* output = <double*>out_addr
    
    cdef double new_x = x + dx
    cdef double new_y = y + dy
    cdef int iz = <int>floor(z + 0.5)
    
    if dx != 0:
        if is_wall(<int>floor(new_x + (radius if dx > 0 else -radius)), <int>floor(y + radius), iz, w, h, layers, min_layer, flat_map) or \
           is_wall(<int>floor(new_x + (radius if dx > 0 else -radius)), <int>floor(y - radius), iz, w, h, layers, min_layer, flat_map):
            if dx > 0: new_x = floor(new_x + radius) - radius - 0.001
            else:      new_x = floor(new_x - radius) + 1.0 + radius + 0.001

    if dy != 0:
        if is_wall(<int>floor(new_x + radius), <int>floor(new_y + (radius if dy > 0 else -radius)), iz, w, h, layers, min_layer, flat_map) or \
           is_wall(<int>floor(new_x - radius), <int>floor(new_y + (radius if dy > 0 else -radius)), iz, w, h, layers, min_layer, flat_map):
            if dy > 0: new_y = floor(new_y + radius) - radius - 0.001
            else:      new_y = floor(new_y - radius) + 1.0 + radius + 0.001

    output[0] = new_x
    output[1] = new_y

cdef public int check_line_of_sight_c(
    double start_x, double start_y, double z,
    double target_x, double target_y,
    size_t flat_map_addr,
    int w, int h, int layers, int min_layer
):
    cdef int* flat_map = <int*>flat_map_addr
    
    cdef double dir_x = target_x - start_x
    cdef double dir_y = target_y - start_y
    cdef double dist_sq = dir_x*dir_x + dir_y*dir_y
    
    if dist_sq < 0.1:
        return 1

    cdef double target_dist = sqrt(dist_sq)
    
    dir_x /= target_dist
    dir_y /= target_dist

    cdef int map_x = <int>floor(start_x)
    cdef int map_y = <int>floor(start_y)
    cdef int map_z = <int>floor(z)
    
    cdef double delta_dist_x = abs(1.0 / dir_x) if dir_x != 0 else 1e30
    cdef double delta_dist_y = abs(1.0 / dir_y) if dir_y != 0 else 1e30
    
    cdef int step_x = 1 if dir_x > 0 else -1
    cdef int step_y = 1 if dir_y > 0 else -1
    
    cdef double side_dist_x, side_dist_y
    
    if dir_x > 0: side_dist_x = (map_x + 1.0 - start_x) * delta_dist_x
    else:         side_dist_x = (start_x - map_x) * delta_dist_x
    
    if dir_y > 0: side_dist_y = (map_y + 1.0 - start_y) * delta_dist_y
    else:         side_dist_y = (start_y - map_y) * delta_dist_y

    cdef double current_dist = 0.0
    cdef int layer_offset = map_z - min_layer
    cdef int idx = 0

    if layer_offset < 0 or layer_offset >= layers:
        return 1

    while current_dist < target_dist:
        if side_dist_x < side_dist_y:
            current_dist = side_dist_x
            side_dist_x += delta_dist_x
            map_x += step_x
        else:
            current_dist = side_dist_y
            side_dist_y += delta_dist_y
            map_y += step_y

        if current_dist >= target_dist:
            return 1
            
        if map_x < 0 or map_x >= w or map_y < 0 or map_y >= h:
            continue

        idx = (layer_offset * w * h) + (map_x * h) + map_y
        
        if flat_map[idx] > 0:
            return 0 

    return 1

cdef public double get_map_height_c(
    double x, double y, double check_z,
    size_t flat_map_addr,
    int w, int h, int layers, int min_layer
):
    cdef int* flat_map = <int*>flat_map_addr
    cdef int ix = <int>floor(x)
    cdef int iy = <int>floor(y)
    
    if ix < 0 or ix >= w or iy < 0 or iy >= h:
        return -1000.0
        
    cdef double max_z = -1000.0
    cdef int l, idx, tile
    cdef double top_z
    cdef double block_height
    
    for l in range(layers):
        idx = (l * w * h) + (ix * h) + iy
        tile = flat_map[idx]
        
        if tile > 0:
            block_height = 0.5 if tile == 20 else 1.0
            
            top_z = (min_layer + l) + block_height
            
            if top_z <= (check_z + 0.5):
                if top_z > max_z:
                    max_z = top_z
                    
    return max_z

cdef struct ProjectileData:
    double x, y, z
    double dir_x, dir_y, dir_z
    double speed
    int active
    int texture_idx
    double pitch
    int damage
    int from_player

cdef inline double _get_height_fast(int x, int y, int check_z, int w, int h, int layers, int min_layer, int* flat_map):
    if x < 0 or x >= w or y < 0 or y >= h: return -1000.0
    cdef double max_z = -1000.0
    cdef int l, idx, tile
    cdef double top_z, block_height
    
    for l in range(layers):
        idx = (l * w * h) + (x * h) + y
        tile = flat_map[idx]
        if tile > 0:
            block_height = 0.5 if tile == 20 else 1.0
            top_z = (min_layer + l) + block_height
            if top_z <= (check_z + 1.0): 
                if top_z > max_z: max_z = top_z
    return max_z

cdef public void update_projectiles_c(
    size_t proj_array_addr,
    int count,
    double dt,
    size_t flat_map_addr,
    int w, int h, int layers, int min_layer
):
    cdef ProjectileData* projs = <ProjectileData*>proj_array_addr
    cdef int* flat_map = <int*>flat_map_addr
    cdef int i
    cdef double dist_to_travel, traveled, step_dist
    cdef double next_x, next_y, next_z
    cdef double floor_h
    cdef double STEP_SIZE = 0.4

    for i in range(count):
        if projs[i].active == 0:
            continue

        dist_to_travel = projs[i].speed * dt
        traveled = 0.0

        while traveled < dist_to_travel:
            step_dist = STEP_SIZE
            if (dist_to_travel - traveled) < STEP_SIZE:
                step_dist = dist_to_travel - traveled

            next_x = projs[i].x + projs[i].dir_x * step_dist
            next_y = projs[i].y + projs[i].dir_y * step_dist
            next_z = projs[i].z + projs[i].dir_z * step_dist

            if is_wall(<int>floor(next_x), <int>floor(next_y), <int>floor(next_z), w, h, layers, min_layer, flat_map):
                projs[i].active = 0
                break

            floor_h = _get_height_fast(<int>floor(next_x), <int>floor(next_y), <int>floor(next_z), w, h, layers, min_layer, flat_map)
            if next_z < floor_h:
                projs[i].active = 0
                break

            projs[i].x = next_x
            projs[i].y = next_y
            projs[i].z = next_z
            traveled += step_dist

cdef struct RenderSprite:
    double x, y
    double dist_sq
    int texture_idx
    double pitch

cdef int compare_sprites(const void* a, const void* b) noexcept nogil:
    cdef RenderSprite* sa = <RenderSprite*>a
    cdef RenderSprite* sb = <RenderSprite*>b
    if sa.dist_sq < sb.dist_sq: return 1
    if sa.dist_sq > sb.dist_sq: return -1
    return 0

cdef struct EnemyData:
    double x, y, z
    double dir_x, dir_y
    double hp
    int state           # 0=Idle, 1=Chasing, 2=Attacking, 3=Dying, 4=Dead
    int texture_idx
    double timer        # For attack cooldowns or state transitions
    double move_speed
    int enemy_type      # To distinguish behavior (Guard vs Yuritler)

cdef public int prepare_scene_sprites_c(
    double player_x, double player_y,
    
    size_t proj_array_addr, int max_projs,
    size_t enemies_struct_addr, int num_enemies,
    size_t static_in_addr, int num_statics,
    
    size_t output_buffer_addr, int max_sprites_shader
):
    cdef ProjectileData* projs = <ProjectileData*>proj_array_addr
    cdef EnemyData* enemies = <EnemyData*>enemies_struct_addr
    cdef double* statics = <double*>static_in_addr
    
    cdef float* out_buf = <float*>output_buffer_addr
    
    cdef RenderSprite sort_buf[128] 
    cdef int count = 0
    cdef int i, k
    cdef double dx, dy
    
    for i in range(max_projs):
        if projs[i].active == 1:
            if count >= 128: break
            dx = projs[i].x - player_x
            dy = projs[i].y - player_y
            sort_buf[count].x = projs[i].x
            sort_buf[count].y = projs[i].y
            sort_buf[count].dist_sq = dx*dx + dy*dy
            sort_buf[count].texture_idx = projs[i].texture_idx
            sort_buf[count].pitch = projs[i].pitch
            count += 1

    for i in range(num_enemies):
        if count >= 128: break
        
        if enemies[i].state == 4: 
             pass

        dx = enemies[i].x - player_x
        dy = enemies[i].y - player_y
        sort_buf[count].x = enemies[i].x
        sort_buf[count].y = enemies[i].y
        sort_buf[count].dist_sq = dx*dx + dy*dy
        sort_buf[count].texture_idx = enemies[i].texture_idx
        sort_buf[count].pitch = 0.0
        count += 1

    for i in range(num_statics):
        if count >= 128: break
        k = i * 4
        dx = statics[k] - player_x
        dy = statics[k+1] - player_y
        sort_buf[count].x = statics[k]
        sort_buf[count].y = statics[k+1]
        sort_buf[count].dist_sq = dx*dx + dy*dy
        sort_buf[count].texture_idx = <int>statics[k+2]
        sort_buf[count].pitch = statics[k+3]
        count += 1
        
    qsort(sort_buf, count, sizeof(RenderSprite), compare_sprites)
    
    cdef int limit = count
    if limit > max_sprites_shader:
        limit = max_sprites_shader
        
    for i in range(limit):
        out_buf[i*4 + 0] = <float>sort_buf[i].x
        out_buf[i*4 + 1] = <float>sort_buf[i].y
        out_buf[i*4 + 2] = <float>sort_buf[i].texture_idx
        out_buf[i*4 + 3] = <float>sort_buf[i].pitch
        
    for i in range(limit * 4, max_sprites_shader * 4):
        out_buf[i] = 0.0
        
    return limit

cdef inline double dist_sq(double x1, double y1, double x2, double y2):
    return (x1 - x2)*(x1 - x2) + (y1 - y2)*(y1 - y2)

cdef public void update_enemies_c(
    size_t enemies_addr, 
    int count, 
    double player_x, double player_y, double player_z,
    double dt,
    size_t flat_map_addr, 
    int w, int h, int layers, int min_layer
):
    """
    Updates all enemy positions, logic, and states in a single C pass.
    Handles basic pathfinding (move towards player) and wall collisions.
    """
    cdef EnemyData* enemies = <EnemyData*>enemies_addr
    cdef int* flat_map = <int*>flat_map_addr
    cdef int i
    cdef double dx, dy, dist, dist_inv
    cdef double next_x, next_y
    cdef double attack_range = 15.0
    
    for i in range(count):
        if enemies[i].state >= 4:
            continue
            
        # Calculate vector to player
        dx = player_x - enemies[i].x
        dy = player_y - enemies[i].y
        dist = sqrt(dx*dx + dy*dy)
        
        if enemies[i].state == 0: # Idle
            if dist < attack_range:
                enemies[i].state = 1 # Start Chasing
                
        elif enemies[i].state == 1: # Chasing
            if dist <= attack_range:
                enemies[i].state = 2 # Prepare Attack
                enemies[i].timer = 1.0 # Attack delay
            else:
                # Normalize direction
                if dist > 0:
                    dist_inv = 1.0 / dist
                    enemies[i].dir_x = dx * dist_inv
                    enemies[i].dir_y = dy * dist_inv
                
                next_x = enemies[i].x + enemies[i].dir_x * enemies[i].move_speed * dt
                next_y = enemies[i].y + enemies[i].dir_y * enemies[i].move_speed * dt
                
                if not is_wall(<int>floor(next_x + 0.3), <int>floor(enemies[i].y), <int>floor(enemies[i].z), w, h, layers, min_layer, flat_map) and \
                   not is_wall(<int>floor(next_x - 0.3), <int>floor(enemies[i].y), <int>floor(enemies[i].z), w, h, layers, min_layer, flat_map):
                    enemies[i].x = next_x
                
                # Check Y-axis movement
                if not is_wall(<int>floor(enemies[i].x), <int>floor(next_y + 0.3), <int>floor(enemies[i].z), w, h, layers, min_layer, flat_map) and \
                   not is_wall(<int>floor(enemies[i].x), <int>floor(next_y - 0.3), <int>floor(enemies[i].z), w, h, layers, min_layer, flat_map):
                    enemies[i].y = next_y

        elif enemies[i].state == 2: # Attacking
            enemies[i].timer -= dt
            if enemies[i].timer <= 0:
                enemies[i].state = 1 # Return to chase

cdef public int check_hitscan_c(
    double ray_x, double ray_y, double ray_z,
    double dir_x, double dir_y, double dir_z,
    size_t enemies_addr,
    int count,
    double max_dist,
    double damage
):
    """
    Performs a raycast against the enemy bounding cylinders.
    Returns: Index of the enemy hit, or -1 if none.
    Side Effect: Applies damage directly to the struct in C memory.
    """
    cdef EnemyData* enemies = <EnemyData*>enemies_addr
    cdef int i
    cdef int best_idx = -1
    cdef double closest_dist = max_dist
    
    cdef double ex, ey, ez
    cdef double v_x, v_y
    cdef double t_closest, proj, dist_to_line_sq
    cdef double hit_z
    cdef double enemy_radius = 0.35
    cdef double enemy_height = 0.8
    
    for i in range(count):
        if enemies[i].state >= 3: continue
        
        ex = enemies[i].x
        ey = enemies[i].y
        ez = enemies[i].z
        
        v_x = ex - ray_x
        v_y = ey - ray_y
        
        t_closest = v_x * dir_x + v_y * dir_y
        
        if t_closest < 0 or t_closest > closest_dist:
            continue
            
        # Distance squared from enemy center to the ray line
        proj = t_closest
        dist_to_line_sq = (v_x*v_x + v_y*v_y) - (proj*proj)
        
        if dist_to_line_sq < (enemy_radius * enemy_radius):
            hit_z = ray_z + dir_z * t_closest
            
            if hit_z >= ez and hit_z <= (ez + enemy_height):
                closest_dist = t_closest
                best_idx = i

    if best_idx != -1:
        enemies[best_idx].hp -= damage
        if enemies[best_idx].hp <= 0:
            enemies[best_idx].state = 3 # Dying
            
    return best_idx

cdef struct PlayerData:
    double x, y, z
    double vel_z
    double rot
    int is_grounded
    int is_crouching

cdef public void update_player_complete_c(
    size_t player_addr,
    double dt,
    double input_speed,   # -1.0 to 1.0 (forward/back)
    double input_strafe,  # -1.0 to 1.0 (left/right)
    double input_turn,    # -1.0 to 1.0 (rotation)
    double move_speed_val,
    double rot_speed_val,
    size_t flat_map_addr,
    int w, int h, int layers, int min_layer
):
    cdef PlayerData* p = <PlayerData*>player_addr
    cdef int* flat_map = <int*>flat_map_addr
    
    cdef double floor_h = _get_height_fast(<int>floor(p.x), <int>floor(p.y), <int>floor(p.z), w, h, layers, min_layer, flat_map)
    cdef double GRAVITY = 35.0
    
    if p.is_grounded == 0:
        p.vel_z -= GRAVITY * dt
        p.z += p.vel_z * dt
        if p.z <= floor_h:
            p.z = floor_h
            p.vel_z = 0.0
            p.is_grounded = 1
        
        if p.z < -25.0:
            p.z = 10.0
            p.vel_z = 0.0
            p.is_grounded = 0
    else:
        if p.z > (floor_h + 0.1):
            p.is_grounded = 0

    p.rot += input_turn * rot_speed_val * dt
    
    cdef double moveStep = input_speed * move_speed_val * dt
    cdef double strafeStep = input_strafe * move_speed_val * dt
    
    cdef double cos_rot = cos(p.rot)
    cdef double sin_rot = sin(p.rot)
    
    # vx = cos(rot) * move + cos(rot-90) * strafe
    # cos(rot-90) = sin(rot), sin(rot-90) = -cos(rot)
    cdef double vx = cos_rot * moveStep + sin_rot * strafeStep
    cdef double vy = sin_rot * moveStep - cos_rot * strafeStep
    
    cdef double radius = 0.3
    cdef double new_x = p.x + vx
    cdef double new_y = p.y + vy
    cdef int iz = <int>floor(p.z + 0.5)
    
    # X Axis Collision
    if vx != 0:
        if is_wall(<int>floor(new_x + (radius if vx > 0 else -radius)), <int>floor(p.y + radius), iz, w, h, layers, min_layer, flat_map) or \
           is_wall(<int>floor(new_x + (radius if vx > 0 else -radius)), <int>floor(p.y - radius), iz, w, h, layers, min_layer, flat_map):
            if vx > 0: new_x = floor(new_x + radius) - radius - 0.001
            else:      new_x = floor(new_x - radius) + 1.0 + radius + 0.001
    
    p.x = new_x

    # Y Axis Collision
    if vy != 0:
        if is_wall(<int>floor(p.x + radius), <int>floor(new_y + (radius if vy > 0 else -radius)), iz, w, h, layers, min_layer, flat_map) or \
           is_wall(<int>floor(p.x - radius), <int>floor(new_y + (radius if vy > 0 else -radius)), iz, w, h, layers, min_layer, flat_map):
            if vy > 0: new_y = floor(new_y + radius) - radius - 0.001
            else:      new_y = floor(new_y - radius) + 1.0 + radius + 0.001

    p.y = new_y

cdef public void update_player_physics_c(
    size_t player_addr,
    double dt,
    size_t flat_map_addr,
    int w, int h, int layers, int min_layer
):
    """
    Handles gravity, jumping integration, and floor detection.
    """
    cdef PlayerData* p = <PlayerData*>player_addr
    cdef int* flat_map = <int*>flat_map_addr
    
    cdef double GRAVITY = 35.0
    cdef double floor_height
    
    floor_height = _get_height_fast(<int>floor(p.x), <int>floor(p.y), <int>floor(p.z), w, h, layers, min_layer, flat_map)
    
    if p.is_grounded == 0:
        p.vel_z -= GRAVITY * dt
        p.z += p.vel_z * dt
        
        if p.z <= floor_height:
            p.z = floor_height
            p.vel_z = 0.0
            p.is_grounded = 1
            
        if p.z < -25.0:
            p.z = 10.0
            p.vel_z = 0.0
            p.is_grounded = 0
    else:
        if p.z > (floor_height + 0.1):
            p.is_grounded = 0
        else:
            pass
