from settings import *
from sprites import *
from player import Player
from enemies import *
from groups import AllSprites
from random import randint,uniform
from support import *
class Level:
    def __init__(self,tmx_map,level_frames,audio_files,data,switch_stage,items_dissapear,st_pos):
        self.display_surface=pygame.display.get_surface()
        self.data=data
        self.switch_stage=switch_stage
        self.pause_menu=False
        self.large_cloud_pause=True
        self.items_dissapear=items_dissapear

        #level data
        self.level_width=tmx_map.width*TILE_SIZE
        self.level_height=tmx_map.height*TILE_SIZE
        tmx_map_properties=tmx_map.get_layer_by_name("Data")[0].properties
        self.level_unlock=tmx_map_properties["level_unlock"]
        self.st_pos=st_pos
        if tmx_map_properties["bg"]:
            bg_tile=level_frames["bg"]["Blue"]
        else:
            bg_tile=None

        #groups
        self.all_sprites=AllSprites(
            tmx_map.width,
            tmx_map.height,
            clouds={
                "large_cloud":level_frames["large_cloud"],
                "small_cloud":level_frames["small_cloud"]
            },
            horizon_line=tmx_map_properties["horizon_line"],
            data=self.data,
            bg_tile=bg_tile,
            top_limit=tmx_map_properties["top_limit"],
            cloud_pause=self

        )
        self.collision_sprites=pygame.sprite.Group()
        self.semicollidable_sprites=pygame.sprite.Group()
        self.damage_sprites=pygame.sprite.Group()
        self.tooth_sprites=pygame.sprite.Group()
        self.pearl_sprites=pygame.sprite.Group()
        self.item_sprites=pygame.sprite.Group()
        self.present_pos=(0,0)
        self.setup(tmx_map,level_frames,audio_files)

        #frames
        self.pearl_surf=level_frames["pearl"]
        self.particle_frames=level_frames["particle"]

        # audio
        self.coin_sound=audio_files["coin"]
        self.hit_sound=audio_files["hit"]
        self.pearl_sound=audio_files["pearl"]
        
        # pause plam tree groups
        self.palm_groups=pygame.sprite.Group()
    def setup(self,tmx_map,level_frames,audio_files):
        self.level_frames=level_frames
        for layer in ["BG","Terrain","FG","Platforms"]:
            for x,y,image in tmx_map.get_layer_by_name(layer).tiles():
                groups=[self.all_sprites]
                if layer=="Terrain":groups.append(self.collision_sprites)
                if layer=="Platforms":groups.append(self.semicollidable_sprites)
                match layer:
                    case "BG":z=Z_LAYERS["bg tiles"]
                    case "FG":z=Z_LAYERS["bg tiles"]
                    case _:z=Z_LAYERS["main"]
                Sprite(image,(TILE_SIZE*x,TILE_SIZE*y),groups,z)

        # bg-details
        for obj in tmx_map.get_layer_by_name("BG details"):
            if obj.name=="static":
                Sprite(obj.image,(obj.x,obj.y),(self.all_sprites),Z_LAYERS["bg tiles"])
            else:
                frames=level_frames[obj.name]
                AnimatedSprite((obj.x,obj.y),level_frames[obj.name],self.all_sprites,Z_LAYERS["bg tiles"])           
                if obj.name=="candle":
                    AnimatedSprite((obj.x,obj.y)+vector(-20,-20),level_frames["candle_light"],self.all_sprites,z=Z_LAYERS["bg tiles"])           
        # objects
        for obj in tmx_map.get_layer_by_name("Objects"):
            if obj.name=="player":
                self.player=Player(
                    pos=(obj.x,obj.y),
                    groups=self.all_sprites,
                    collision_sprites=self.collision_sprites,
                    semicollidable_sprites=self.semicollidable_sprites,
                    frames=level_frames["player"],
                    data=self.data,
                    attack_sound=audio_files["attack"],
                    jump_sound=audio_files["jump"]
                    )
            else:
                if obj.name in ("barrel","crate"):
                    Sprite(obj.image,(obj.x,obj.y),(self.all_sprites,self.collision_sprites))
                else:
                    #frames
                    frames=level_frames[obj.name] if not "palm" in obj.name else level_frames["palms"][obj.name]
                    if obj.name=="floor_spike" and obj.properties["inverted"]:
                        frames=[pygame.transform.flip(frame,False,True) for frame in frames]

                    #groups
                    groups=[self.all_sprites]
                    if obj.name in ("palm_small","palm_large"):groups.append(self.semicollidable_sprites)
                    if obj.name in ("saw","floor_spike"):groups.append(self.damage_sprites)

                    # z index
                    z=Z_LAYERS["main"] if not "bg" in obj.name else Z_LAYERS["bg details"]
                    # animation speed
                    animation_speed=ANIMATION_SPEED if not "palm" in obj.name else ANIMATION_SPEED+uniform(-1,1)
                    AnimatedSprite((obj.x,obj.y),frames,groups,z,animation_speed)
            if obj.name=="flag":
                self.present_pos=(obj.x,obj.y)
                self.level_finish_rect=pygame.FRect((obj.x,obj.y),(obj.width,obj.height))  
        if self.st_pos:
            self.player.rect.topleft=self.present_pos
        print(self.st_pos)
        # moving objects
        for obj in tmx_map.get_layer_by_name("Moving Objects"):
            if obj.name=="spike":
                Spike(
                    pos=(obj.x+obj.width/2,obj.y+obj.height/2),
                    surf=level_frames["spike"],
                    start_angle=obj.properties["start_angle"],
                    end_angle=obj.properties["end_angle"],
                    radius=obj.properties["radius"],
                    speed=obj.properties["speed"],
                    groups=(self.all_sprites,self.damage_sprites)
                )
                for i in range(0,obj.properties["radius"],20):
                    Spike(
                    pos=(obj.x+obj.width/2,obj.y+obj.height/2),
                    surf=level_frames["spiked_chain"],
                    start_angle=obj.properties["start_angle"],
                    end_angle=obj.properties["end_angle"],
                    radius=i,
                    speed=obj.properties["speed"],
                    groups=(self.all_sprites),
                    z=Z_LAYERS["bg details"]
                    )
            else:
                frames=level_frames[obj.name]
                groups=(self.all_sprites,self.semicollidable_sprites) if obj.properties["platform"] else (self.all_sprites,self.damage_sprites)
                if obj.width>obj.height:
                    move_dir="x"
                    start_pos=(obj.x,obj.y + obj.height/2)
                    end_pos=(obj.x + obj.width,obj.y + obj.height/2)
                elif obj.width<obj.height:
                    move_dir="y"
                    start_pos=(obj.x + obj.width/2,obj.y)
                    end_pos=(obj.x + obj.width/2,obj.y + obj.height)  
                speed=obj.properties["speed"]  if obj.name!="boat" else obj.properties["speed"]+40
                MovingSprite(frames,start_pos,end_pos,move_dir,groups,speed,obj.properties["flip"])

                if obj.name=="saw":
                    if move_dir=="x":
                        y=start_pos[1]-level_frames["saw_chain"].get_height()/2
                        left,right=int(start_pos[0]),int(end_pos[0])
                        for x in range(left,right,20):
                            Sprite(level_frames["saw_chain"],(x,y),self.all_sprites,z=Z_LAYERS["bg details"])
                    else:
                        x=start_pos[0]-level_frames["saw_chain"].get_width()/2
                        top,bottom=int(start_pos[1]),int(end_pos[1])
                        for y in range(top,bottom,20):
                            Sprite(level_frames["saw_chain"],(x,y),self.all_sprites,z=Z_LAYERS["bg details"])
        # Enemies
        for obj in tmx_map.get_layer_by_name("Enemies"):
            if obj.name=="tooth":
                Tooth((obj.x,obj.y),level_frames[obj.name],(self.all_sprites,self.damage_sprites,self.tooth_sprites),self.collision_sprites)
            if obj.name=="shell":
                Shell(
                    pos=(obj.x,obj.y),
                    frames=level_frames[obj.name],
                    groups=(self.all_sprites,self.collision_sprites),
                    reverse=obj.properties["reverse"],
                    player=self.player,
                    create_pearl=self.create_pearl
                    )
                
        # items
        for obj in tmx_map.get_layer_by_name("Items"):
            pos=(obj.x+TILE_SIZE/2,obj.y+TILE_SIZE/2)
            if not (pos) in self.items_dissapear[self.data.current_level]: 
                Item(pos,obj.name,level_frames["items"][obj.name],(self.all_sprites,self.item_sprites),self.data)

        # water
        for obj in tmx_map.get_layer_by_name("Water"):
            rows=int(obj.height/TILE_SIZE)
            cols=int(obj.width/TILE_SIZE)
            for i in range(rows):
                for j in range(cols):
                    x=obj.x+(j*TILE_SIZE)
                    y=obj.y+(i*TILE_SIZE)
                    if i==0:
                        AnimatedSprite((x,y),level_frames["water_top"],self.all_sprites,z=Z_LAYERS["water"])
                    else:
                        Sprite(level_frames["water_body"],(x,y),self.all_sprites,z=Z_LAYERS["water"])

        
    def pearl_collision(self):
        for sprite in self.collision_sprites:
            if not hasattr(sprite,"not_fired"):
                sprite =pygame.sprite.spritecollide(sprite,self.pearl_sprites,True)
                if sprite:
                    ParticleEffectSprite(sprite[0].rect.center,self.particle_frames,(self.all_sprites))

    def hit_collision(self):
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect)>0:
                self.player.get_damage()
                self.hit_sound.play()
                if hasattr(sprite,"pearl"):
                    ParticleEffectSprite(sprite.rect.center,self.particle_frames,(self.all_sprites))


    def create_pearl(self,pos,direction):
        Pearl(pos,self.pearl_surf,(self.all_sprites,self.damage_sprites,self.pearl_sprites),direction,speed=150)
        self.pearl_sound.play()

    def item_collision(self):
        if self.item_sprites:
            item_sprites=pygame.sprite.spritecollide(self.player,self.item_sprites,True)
            if item_sprites:
                item_sprites[0].activate()
                self.items_dissapear[self.data.current_level].append((item_sprites[0].rect.center))
                
                ParticleEffectSprite(item_sprites[0].rect.center,self.particle_frames,(self.all_sprites))
                self.coin_sound.play()
    def attack_collision(self):
        for target in self.pearl_sprites.sprites()+self.tooth_sprites.sprites():
            facing_pos=self.player.rect.centerx<target.rect.centerx and  self.player.facing_right and target.direction==-1 or\
            self.player.rect.centerx>target.rect.centerx and not self.player.facing_right and target.direction==1
            if target.rect.colliderect(self.player.rect)>0 and self.player.attacking and facing_pos:
                if hasattr(target,"tooth"):
                    target.kill()
                else:
                    target.reverse()
    def check_constraint(self):
        # left and right
        if self.player.hitbox_rect.left<=0:
            self.player.hitbox_rect.left=0

        if self.player.hitbox_rect.right>=self.level_width:
            self.player.hitbox_rect.right=self.level_width

        if self.player.hitbox_rect.bottom>=self.level_height:
            self.switch_stage("overworld",unlock=-1)

            #sucess
        if (self.player.hitbox_rect.colliderect(self.level_finish_rect)):
            self.switch_stage("overworld",self.level_unlock)
    def pause_button(self):
        surf=pygame.image.load(join("graphics","pause","pause_button2.png")).convert_alpha()
        pause_button=pygame.transform.scale(surf,(40,40))
        pause_rect=pause_button.get_frect(center=(WINDOW_WIDTH-40,40))
        self.display_surface.blit(pause_button,pause_rect)
        pos=pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if pause_rect.collidepoint(pos):
                self.large_cloud_pause=False
                AnimatedSprite(pygame.Rect((WINDOW_WIDTH/2-90,WINDOW_HEIGHT/2.5-40),(200,300)).topright+vector(-70,-80),import_folder("graphics","overworld","palm"),self.palm_groups,Z_LAYERS["fg"])
                self.pause_menu=True

    def box_items(self,font_size,content,color,pos,):
        box_icons_surf=pygame.font.Font(None,font_size).render(content,True,color)
        box_icons_rect=pygame.FRect((WINDOW_WIDTH/2-60,pos[1]),(140,50))
        pygame.draw.rect(self.display_surface,"#ddc6a1",box_icons_rect,0,10)
        self.display_surface.blit(box_icons_surf,box_icons_rect.center+vector(-box_icons_surf.get_width()/2,-box_icons_surf.get_height()/2))
        return box_icons_rect
    def pause_box(self):
        spacing=80
        pause_font=pygame.font.Font(None,140)
        pause_surf=pause_font.render("Pause Menu",True,"#D8AE7E")
        pause_rect=pause_surf.get_frect(center=(WINDOW_WIDTH/2,WINDOW_HEIGHT/6))
        self.display_surface.blit(pause_surf,pause_rect)    
        pygame.draw.rect(self.display_surface,"#A67B5B",pygame.Rect((WINDOW_WIDTH/2-90,WINDOW_HEIGHT/2.5-40),(200,300)),0,20)
        rect=pygame.draw.rect(self.display_surface,"black",pygame.Rect((WINDOW_WIDTH/2-90,WINDOW_HEIGHT/2.5-40),(200,300)),4,20)


        resume_rect=self.box_items(40,"Resume","white",(WINDOW_WIDTH/2,WINDOW_HEIGHT/2.5))
        restart_rect=self.box_items(40,"Restart","white",(WINDOW_WIDTH/2,WINDOW_HEIGHT/2.5+spacing))
        exit_rect=self.box_items(40,"Exit","white",(WINDOW_WIDTH/2,WINDOW_HEIGHT/2.5+spacing*2))
        mouse_pos=pygame.mouse.get_pos()
        if pygame.mouse.get_just_pressed()[0]:
            if resume_rect.collidepoint(mouse_pos):
                self.pause_menu=False
            elif restart_rect.collidepoint(mouse_pos):
                self.data.unlocked_level=0
                self.data.current_level=0
                self.data.health=5
                self.switch_stage("level")
            elif exit_rect.collidepoint(mouse_pos):
                self.data.health=0



       
    def run(self,dt):
        self.display_surface.fill("black")
        if not self.pause_menu:
            self.all_sprites.update(dt)
        self.pearl_collision()
        self.hit_collision()
        self.item_collision()
        self.attack_collision()
        self.check_constraint()
        self.all_sprites.draw(self.player.hitbox_rect.center,dt)
        if not self.pause_menu:
            self.pause_button()
            self.hit_sound.set_volume(1)
            self.coin_sound.set_volume(1)
        else:
            self.pause_box()
            self.hit_sound.set_volume(0)
            self.coin_sound.set_volume(0)
        if self.pause_menu:
            self.palm_groups.update(dt)
            self.palm_groups.draw(self.display_surface)
