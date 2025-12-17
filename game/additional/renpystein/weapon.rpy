init python:

    class Weapon(object):
        def __init__(self, weaponName="fist", frameCount = 5, zoom_factor = 11, damage=25, projectile_type=None, cooldown=0.5, ads_idle=None, ads_fire=None, loop_frames=None):
            self.images = []
            self.playing = False
            self.frame = 0
            self.oldst = None
            self.damage = damage
            self.projectile_type = projectile_type
            self.cooldown = cooldown
            self.last_fired = 0.0
            self.loop_frames = loop_frames
            
            # ADS Support
            self.ads_idle = None
            self.ads_fire = None
            if ads_idle:
                self.ads_idle = Transform(ads_idle, zoom=zoom_factor)
            if ads_fire:
                self.ads_fire = Transform(ads_fire, zoom=zoom_factor)
            
            for i in range(frameCount):
                img = Transform("pics/weapons/%s%s.png" % (weaponName, i+1), zoom = zoom_factor)
                self.images.append(img)

        def play(self):
            if not self.playing:
                self.playing = True
                self.frame = 0
                self.oldst = None

        def stop(self):
            self.playing = False
            
        def render_to(self, r, width, height, st, at, is_ads=False, is_firing=False):
            # Figure out the time elapsed since the previous frame.
            if self.oldst is None:
                self.oldst = st
                
            time_passed = st - self.oldst
            if (time_passed > 0.05 and self.playing):
                self.oldst = st
                
                if self.loop_frames and is_firing:
                    if self.frame == self.loop_frames[-1]:
                        self.frame = self.loop_frames[0]
                    else:
                        self.frame += 1
                        if self.frame >= len(self.images): self.frame = 0
                else:
                    self.frame += 1
                    if (self.frame >= len(self.images)):
                        self.frame = 0
                        self.playing = False
            
            if is_ads and self.ads_idle:
                # ADS Rendering Logic
                if self.playing and self.ads_fire and is_firing:
                    # Show firing sprite if playing animation
                    # For single-frame ADS fire, we just show it while "playing" is true
                    # (which is controlled by the frame counter of the normal anim in background)
                    img_to_render = self.ads_fire
                else:
                    img_to_render = self.ads_idle
                
                eileen = renpy.render(img_to_render, width, height, st, at)
            else:
                # Normal Hip-fire Rendering
                eileen = renpy.render(self.images[self.frame], width, height, st, at)
            
            ew, eh = eileen.get_size()
            r.blit(eileen, (width/2-ew/2, height-eh))
            
            