from typing import List
from pygame import Surface
from pygame.rect import FRect, Rect
from settings import *
from timers import Timer
from sprites import Sprite , AnimatedSprite,Cloud
class WorldSprites(pygame.sprite.Group):
    def __init__(self,data):
        super().__init__()
        self.display_surface=pygame.display.get_surface()
        self.offset=vector()
        self.data=data

    def draw(self,target_pos):
        self.offset.x=-(target_pos[0]-WINDOW_WIDTH/2)
        self.offset.y=-(target_pos[1]-WINDOW_HEIGHT/2)
        
        # background
        for sprite in sorted(self,key=lambda sprite:sprite.z):
            if sprite.z<Z_LAYERS["main"]:
                if sprite.z==Z_LAYERS["path"]:
                    if sprite.level<=self.data.unlocked_level:
                        self.display_surface.blit(sprite.image,sprite.rect.topleft+self.offset)
                else:
                    self.display_surface.blit(sprite.image,sprite.rect.topleft+self.offset)
        
        # main
        for sprite in sorted(self,key=lambda sprite:sprite.rect.centery):
            if sprite.z>=Z_LAYERS["main"]:
                if hasattr(sprite,"icon"):
                    self.display_surface.blit(sprite.image,sprite.rect.topleft+self.offset+vector(0,-28))
                else:
                    self.display_surface.blit(sprite.image,sprite.rect.topleft+self.offset)


        




class AllSprites(pygame.sprite.Group):
    def __init__(self,width,height,clouds,horizon_line,cloud_pause,data,bg_tile=None,top_limit=0):
        super().__init__()
        self.display_surface=pygame.display.get_surface()
        self.offset=vector()
        self.map_width=width*TILE_SIZE
        self.map_height=height*TILE_SIZE
        self.data=data
        self.horizon_line=horizon_line
        self.game=cloud_pause
        self.borders={
            "left":0,
            "right":-(self.map_width-WINDOW_WIDTH),
            "top":top_limit+80,
            "bottom":-(self.map_height-WINDOW_HEIGHT)
        }
        self.sky=not bg_tile

        if bg_tile:
            for row in range(-int(self.borders["top"]/TILE_SIZE)-1,height):
                for col in range(width):
                    Sprite(bg_tile,(col*TILE_SIZE,row*TILE_SIZE),self,-1)
        elif self.data.current_level!=1:
            self.small_clouds=clouds["small_cloud"]
            self.large_clouds=clouds["large_cloud"]
            self.horizontal_pos=0
            self.direction=-1

            # large cloud
            self.large_cloud_speed=50
            self.large_cloud_x=0
            self.large_cloud_tiles=int((self.map_width/self.large_clouds.get_width())) +2
            self.large_cloud_width,self.large_cloud_height=self.large_clouds.get_size()

            #small cloud
            self.small_cloud_speed=40
            self.cloud_timer=Timer(2500,func=self.create_cloud,repeat=True)
            for i in range(10):
                pos=(randint(0,self.map_width),randint(self.borders["top"],self.horizon_line))
                Cloud(pos,choice(self.small_clouds),self)

    def camera_constraint(self):
        self.offset.x=self.offset.x if self.offset.x<self.borders["left"] else self.borders["left"]
        self.offset.x=self.offset.x if self.offset.x>self.borders["right"] else self.borders["right"]
        self.offset.y=self.offset.y if self.offset.y<self.borders["top"] else self.borders["top"]
        self.offset.y=self.offset.y if self.offset.y>self.borders["bottom"] else self.borders["bottom"]

    def draw_sky(self,color="#ddc6a1"):
        self.display_surface.fill(color)
        self.horizontal_pos= self.horizon_line +self.offset.y
        sea_rect=pygame.FRect(0,self.horizontal_pos,WINDOW_WIDTH,WINDOW_HEIGHT-self.horizontal_pos)
        pygame.draw.rect(self.display_surface,"#92a9ce",sea_rect)
        # horizon line
        pygame.draw.line(self.display_surface,"#f5f1de",(0,self.horizontal_pos),(WINDOW_WIDTH,self.horizontal_pos),4)
    
    def large_cloud(self,dt):
        if self.game.large_cloud_pause==True:
            self.large_cloud_x+=self.direction*self.large_cloud_speed*dt
        if self.large_cloud_x<=-self.large_cloud_width:
            self.large_cloud_x=0
        for i in range(self.large_cloud_tiles):
            x=self.large_cloud_x+self.large_cloud_width*i+self.offset.x
            y=self.horizontal_pos-self.large_cloud_height
            self.display_surface.blit(self.large_clouds,(x,y))
    
    def create_cloud(self):
        pos=(randint(self.map_width+300,self.map_width+600),randint(self.borders["top"],self.horizon_line))
        Cloud(pos,choice(self.small_clouds),self)        
    def draw(self,target_pos,dt):
        self.offset.x=-(target_pos[0]-WINDOW_WIDTH/2)
        self.offset.y=-(target_pos[1]-WINDOW_HEIGHT/2)
        self.camera_constraint()
        if self.sky and self.data.current_level!=1:
            self.draw_sky()
            self.large_cloud(dt)
            self.cloud_timer.update()
        elif self.sky:
            self.draw_sky(color="black")

        for sprite in sorted(self,key=lambda sprite:sprite.z):
            self.display_surface.blit(sprite.image,sprite.rect.topleft+self.offset)

