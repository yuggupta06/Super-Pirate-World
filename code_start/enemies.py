from settings import *
from timers import *
class Tooth(pygame.sprite.Sprite):
    def __init__(self,pos,frames,groups,collision_sprites):
        super().__init__(groups)
        self.frames,self.frame_index=frames,0
        self.image=self.frames[self.frame_index]
        self.rect=self.image.get_frect(topleft=pos)
        self.tooth=True
        self.z=Z_LAYERS["main"]

        self.direction=choice((-1,1))
        self.speed=170
        self.collision_rects=[sprite.rect for sprite in collision_sprites]

        self.hit_timer=Timer(300)
    def reverse_direction(self):
        right_rect=pygame.FRect((self.rect.bottomright),(1,1))
        left_rect=pygame.FRect((self.rect.bottomleft),(-1,1))
        top_right_rect=pygame.FRect((self.rect.midright),(-1,1))
        if  left_rect.collidelist(self.collision_rects)<0 or\
            right_rect.collidelist(self.collision_rects)<0 or\
            top_right_rect.collidelist(self.collision_rects)>0:
            self.direction*=-1
    def reverse(self):
        if  not self.hit_timer.active:
            self.direction*=-1
            self.hit_timer.activate()
    def update(self,dt):
        # animate
        self.hit_timer.update()
        self.frame_index+=ANIMATION_SPEED*dt
        self.image=self.frames[(int(self.frame_index))% len(self.frames)]
        self.image=pygame.transform.flip(self.image,True,False) if self.direction<0 else self.image
        #move
        self.reverse_direction()
        self.rect.x+=self.direction*self.speed*dt



class Shell(pygame.sprite.Sprite):
    def __init__(self,pos,frames,groups,reverse,player,create_pearl):
        super().__init__(groups)
        self.create_pearl=create_pearl
        if reverse:
            self.frames={}
            for key,surfs in frames.items():
                self.frames[key]=[pygame.transform.flip(surf,True,False) for surf in surfs ]
            self.bullet_direction=-1
        else:
            self.frames=frames
            self.bullet_direction=1

        self.frame_index=0
        self.state="idle"
        self.player=player
        self.image=self.frames[self.state][self.frame_index]
        self.rect=self.image.get_frect(topleft=pos)
        self.old_rect=self.rect.copy()
        self.z=Z_LAYERS["main"]
        self.not_fired=False
        self.shoot_timer=Timer(2500)
        
    def state_management(self):
        player_pos,shell_pos=vector(self.player.hitbox_rect.center),vector(self.rect.center)
        player_near= shell_pos.distance_to(player_pos) <500
        player_level= abs(player_pos.y-shell_pos.y )<60
        player_front=shell_pos.x<player_pos.x if self.bullet_direction>0 else player_pos.x<shell_pos.x

        if player_near and player_level and player_front and not self.shoot_timer.active:
            self.state="fire"
            self.frame_index=0
            self.shoot_timer.activate()
    def update(self,dt):
        self.shoot_timer.update()
        self.state_management()

        # animate 
        self.frame_index+=ANIMATION_SPEED*dt
        if self.frame_index<len(self.frames[self.state]):
            self.image=self.frames[self.state][(int(self.frame_index))]
            if self.state=="fire" and int(self.frame_index)==3 and not self.not_fired:
                self.create_pearl(self.rect.center,self.bullet_direction)
                self.not_fired=True
        else:
            self.frame_index=0
            if self.state=="fire":
                self.state="idle"
                self.not_fired=False
        

class Pearl(pygame.sprite.Sprite):
    def __init__(self,pos,surf,groups,direction,speed):
        super().__init__(groups)
        self.pearl=True
        self.image=surf
        self.rect=self.image.get_frect(topleft=pos+vector(direction*30,0))
        self.direction=direction
        self.speed=speed
        self.z=Z_LAYERS["main"]
        self.timer={
            "lifetieme":Timer(5000,func=self.kill,autostart=True),
            "hit-timer":Timer(300)
        }
    def reverse(self):
        if  not self.timer["hit-timer"].active:
            self.direction*=-1
            self.timer["hit-timer"].activate()
    def update(self,dt):
        for timer in self.timer.values():
            timer.update()
        self.rect.x+=self.direction*self.speed*dt