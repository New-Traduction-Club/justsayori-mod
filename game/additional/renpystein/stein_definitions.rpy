init python:
    class ShaderWarmup(renpy.Displayable):
        def __init__(self, **kwargs):
            super(ShaderWarmup, self).__init__(**kwargs)
            self.dummy_tex = None
            
        def render(self, width, height, st, at):
            if self.dummy_tex is None:
                import pygame
                s = pygame.Surface((64, 64))
                s.fill((255, 0, 255))
                self.dummy_tex = renpy.display.draw.load_texture(s)
            
            # 1. Warmup Raycaster
            r = renpy.Render(width, height)
            
            # We need a child to apply the shader to. Using Image ensures a_tex_coord is generated.
            base_img = Transform(Image("pics/gui/button_bg.png"), size=(width, height))
            child = renpy.render(base_img, width, height, st, at)
            child.add_shader("stein.raycaster")
            
            # Add dummy uniforms
            child.add_uniform('u_resolution', (float(width), float(height)))
            child.add_uniform('u_time', st)
            child.add_uniform('u_player_pos', (0.0, 0.0))
            child.add_uniform('u_player_dir', (1.0, 0.0))
            child.add_uniform('u_player_plane', (0.0, 0.66))
            child.add_uniform('u_pitch', 0.0)
            child.add_uniform('u_z_offset', 0.0)
            child.add_uniform('u_vertical_scale', 1.0)
            child.add_uniform('u_sky_texture', self.dummy_tex)
            child.add_uniform('u_volumetric_clouds', 0.0)
            child.add_uniform('u_rain_intensity', 0.0)
            child.add_uniform('u_snow_intensity', 0.0)
            child.add_uniform('u_wetness', 0.0)
            child.add_uniform('u_time_of_day', 0.0)
            child.add_uniform('u_map_size', (10.0, 10.0))
            child.add_uniform('u_map_uv_scale', (1.0, 1.0))
            child.add_uniform('u_map_texture', self.dummy_tex)
            child.add_uniform('u_map_layer_norm_height', 1.0)
            child.add_uniform('u_map_layer_base_y', 0.0)
            child.add_uniform('u_map_layer_count', 1.0)
            child.add_uniform('u_map_tex_pixel_size', (0.1, 0.1))
            child.add_uniform('u_wall_atlas', self.dummy_tex)
            child.add_uniform('u_floor_texture', self.dummy_tex)
            child.add_uniform('u_num_textures', 1.0)
            child.add_uniform('u_sprite_atlas', self.dummy_tex)
            child.add_uniform('u_num_sprite_textures', 1.0)
            
            sprites = [(0.0, 0.0, 0.0, 0.0)] * 64
            child.add_uniform('u_sprites', sprites)
            child.add_uniform('u_num_active_sprites', 0.0)
            
            child.add_uniform('u_flash_intensity', 0.0)
            child.add_uniform('u_flashlight_active', 0.0)
            child.add_uniform('u_flashlight_bob', (0.0, 0.0))
            child.add_uniform('u_soft_shadows', 0.0)
            child.add_uniform('u_enable_shadows', 0.0)
            child.add_uniform('u_max_dist', 10.0)
            child.add_uniform('u_simple_floor', 0.0)
            child.add_uniform('u_ambient_color', (1.0, 1.0, 1.0))
            child.add_uniform('u_ambient_near_color', (1.0, 1.0, 1.0))
            
            lights = [(0.0, 0.0, 0.0, 0.0)] * 16
            child.add_uniform('u_light_positions', lights)
            child.add_uniform('u_num_active_lights', 0.0)
            
            r.blit(child, (0, 0))
            
            # 2. Warmup Motion Blur
            base_img_small = Transform(Image("pics/gui/button_bg.png"), size=(100, 100))
            mb_child = renpy.render(base_img_small, 100, 100, st, at)
            mb_child.add_shader("stein.motion_blur")
            mb_child.add_uniform("u_blur_amount", 0.5)
            r.blit(mb_child, (0, 0))
            
            # 3. Warmup Weapon FX
            fx_child = renpy.render(base_img_small, 100, 100, st, at)
            fx_child.add_shader("stein.weapon_fx")
            fx_child.add_uniform("u_flash_progress", 0.5)
            fx_child.add_uniform("u_flash_angle", 0.0)
            fx_child.add_uniform("u_flash_color", (1.0, 1.0, 1.0))
            fx_child.add_uniform("u_heat_distortion", 1.0)
            fx_child.add_uniform("u_enable_smoke", 1.0)
            r.blit(fx_child, (0, 0))
            
            # 4. Warmup Bloom
            bloom_child = renpy.render(base_img_small, 100, 100, st, at)
            bloom_child.add_shader("stein.bloom")
            bloom_child.add_uniform("u_resolution", (100.0, 100.0))
            r.blit(bloom_child, (0, 0))
            
            return r

screen shader_warmup():
    add ShaderWarmup()
    text "Compiling Shaders..." xalign 0.5 yalign 0.5 color "#fff" size 30
    timer 0.2 action Return()
