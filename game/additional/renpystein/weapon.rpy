init python:

    class Weapon(object):
        def __init__(self, weaponName="fist", frameCount = 5, zoom_factor = 11, damage=25, projectile_type=None, cooldown=0.5):
            self.images = []
            self.playing = False
            self.frame = 0
            self.oldst = None
            self.damage = damage
            self.projectile_type = projectile_type
            self.cooldown = cooldown
            self.last_fired = 0.0
            
            for i in range(frameCount):
                img = Transform("pics/weapons/%s%s.png" % (weaponName, i+1), zoom = zoom_factor)
                self.images.append(img)
        def play(self):
            self.playing = True
            self.oldst = None
        def stop(self):
            self.playing = False
            
            
            
        def render_to(self, r, width, height, st, at):
            # Figure out the time elapsed since the previous frame.
            if self.oldst is None:
                self.oldst = st
                
            time_passed = st - self.oldst
            if (time_passed > 0.05 and self.playing):
                self.oldst = st
                self.frame += 1
                if (self.frame >= len(self.images)):
                    self.frame = 0
                    self.playing = False
            
            eileen = renpy.render(self.images[self.frame], width, height, st, at)
            ew, eh = eileen.get_size()
            r.blit(eileen, (width/2-ew/2, height-eh))
            
            