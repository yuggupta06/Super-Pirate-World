from settings import *
from timers import Timer
from sprites import AnimatedSprite
class UI:
    def __init__(self,font,frames):
        self.display_surface=pygame.display.get_surface()
        self.all_sprites=pygame.sprite.Group()
        self.font=font
        self.hearts_frames=frames["hearts"]
        self.heart_padding=5

        self.coins=0
        self.coin_timer=Timer(1000)
        self.coin_surf=frames["coin"]
    def create_hearts(self,count):
        for sprite in self.all_sprites:
            sprite.kill()
        for i in range(count):
            x=10+i*(self.hearts_frames[0].get_width()+self.heart_padding)
            y=10
            Heart((x,y),self.hearts_frames ,self.all_sprites)

    def display_text(self,value):
        text_surf=self.font.render(str(value),False,"#33323d")
        text_rect=text_surf.get_frect(topleft=(16,34))
        self.display_surface.blit(text_surf,text_rect)
        coin_surf=self.coin_surf
        coin_rect=coin_surf.get_frect(center=text_rect.bottomleft).move(0,6)
        self.display_surface.blit(coin_surf,coin_rect)



    def update(self,dt):
        self.coin_timer.update()
        self.all_sprites.draw(self.display_surface)
        self.all_sprites.update(dt)
        if self.coin_timer.active:
            self.display_text(self.coins)



class Heart(AnimatedSprite):
    def __init__(self,pos,frames,groups):
        super().__init__(pos,frames,groups)
        self.active=False

    def animate(self,dt):
        self.frame_index+=ANIMATION_SPEED*dt
        if self.frame_index<len(self.frames):
            self.image=self.frames[(int(self.frame_index))]
        else:
            self.active=False
            self.frame_index=0
    def update(self,dt):
        if self.active:
            self.animate(dt)
        else:
            if randint(0,500)==1:
                self.active=True
        
