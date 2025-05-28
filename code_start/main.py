from settings import *
from support import *
from level import Level
from data import Data
from debug import debug
import os
from ui import UI
from overworld import OverWorld
from pytmx.util_pygame import load_pygame

class Game:
    def __init__(self):
        pygame.init()
        os.environ["SDL_VIDEO_CENTERED"]="1"
        info =pygame.display.Info()
        self.display_surface=pygame.display.set_mode((info.current_w,info.current_h),pygame.RESIZABLE)
        pygame.display.set_caption("Super-Pirate-World")
        self.running=True
        self.tmx_maps={
            0:load_pygame(join("data","levels","0.tmx")),
            1:load_pygame(join("data","levels","1.tmx")),
            2:load_pygame(join("data","levels","2.tmx")),
            3:load_pygame(join("data","levels","3.tmx")),
            4:load_pygame(join("data","levels","4.tmx")),
            5:load_pygame(join("data","levels","5.tmx")),
            }
        self.overworld=load_pygame(join("data","overworld","overworld.tmx"))
        self.clock=pygame.time.Clock()
        self.import_assets()
        self.game_sound=self.audio_files["game"]
        self.game_sound.play(loops=-1)
        self.items_disappear={}
        for i in range(0,6):
            self.items_disappear[i]=[]
        self.ui=UI(self.heart_font,self.ui_frames)
        self.data=Data(self.ui)
        self.current_stage=OverWorld(self.overworld,self.overworld_frames,self.data,self.switch_stage)
        self.pause=True
        self.level_health_plus={}
        for i in range(0,6):
            self.level_health_plus[i]=True
        
    def import_assets(self):
        self.level_frames={
            "flag":import_folder("graphics","level","flag"), 
            "saw": import_folder("graphics","enemies","saw","animation"),
            "saw_chain": import_image("graphics","enemies","saw","saw_chain"),
            "floor_spike":import_folder("graphics","enemies","floor_spikes"),
            "palms":import_sub_folders("graphics","level","palms"),
            "candle":import_folder("graphics","level","candle"),
            "window": import_folder("graphics","level","window"),
            "big_chain":import_folder("graphics","level", "big_chains"),
            "small_chain":import_folder("graphics","level","small_chains"),
            "candle_light": import_folder("graphics","level", "candle light"),
            "player":import_sub_folders("graphics","player"),
            "helicopter":import_folder("graphics","level", "helicopter"),
            "boat":import_folder("graphics","objects", "boat"),
            "spike":import_image("graphics","enemies","spike_ball","Spiked Ball"),
            "spiked_chain":import_image("graphics","enemies","spike_ball","spiked_chain"),
            "tooth":import_folder("graphics","enemies","tooth","run"),
            "shell":import_sub_folders("graphics","enemies","shell"),
            "pearl":import_image("graphics","enemies","bullets","pearl"),
            "items":import_sub_folders("graphics","items"),
            "particle":import_folder("graphics","effects","particle"),
            "water_top":import_folder("graphics","level","water","top"),
            "water_body":import_image("graphics","level","water","body"),
            "bg":import_folder_dict("graphics","level","bg","tiles"),
            "large_cloud":import_image("graphics","level","clouds","large_cloud"),
            "small_cloud": import_folder("graphics","level","clouds","small")


        }
        self.heart_font=pygame.font.Font(join("graphics","ui","runescape_uf.ttf"),25)
        self.ui_frames={
            "hearts":import_folder(join("graphics","ui","heart")),
            "coin":import_image(join("graphics","ui","coin"))
        }
    
        self.overworld_frames={
            "palm":import_folder("graphics","overworld","palm"),
            "water":import_folder("graphics","overworld","water") ,
            "stone":import_image("graphics","overworld","objects","stone"),
            "path":import_folder_dict("graphics","overworld","path"),
            "icon":import_sub_folders("graphics","overworld","icon")
        }
        self.audio_files={
            "coin":pygame.mixer.Sound(join("audio","coin.wav")),
            "game":pygame.mixer.Sound(join("audio","starlight_city.mp3")),
            "hit":pygame.mixer.Sound(join("audio","hit.wav")),
            "jump":pygame.mixer.Sound(join("audio","jump.wav")),
            "attack":pygame.mixer.Sound(join("audio","attack.wav")),
            "damage":pygame.mixer.Sound(join("audio","damage.wav")),
            "pearl":pygame.mixer.Sound(join("audio","pearl.wav")),
        }
    def switch_stage(self,target,unlock=0):
        if target=="level":
            
            if self.data.current_level!=0 and self.level_health_plus[self.data.current_level]==True:
                self.level_health_plus[self.data.current_level-1]=False
                self.data.health+=1   
            if self.level_health_plus[self.data.current_level]==False:
                self.current_stage=Level(self.tmx_maps[self.data.current_level],self.level_frames,self.audio_files,self.data,self.switch_stage,self.items_disappear,True)
            else:
                self.current_stage=Level(self.tmx_maps[self.data.current_level],self.level_frames,self.audio_files,self.data,self.switch_stage,self.items_disappear,False)


        
        else:
            if unlock>0:
                self.data.unlocked_level=unlock
            else:
                self.data.health-=1
            self.current_stage=OverWorld(self.overworld,self.overworld_frames,self.data,self.switch_stage)


    def game_end(self):
        if self.data.health==0:
            pygame.quit()
            sys.exit()
    def run(self):
        while True:
            dt=self.clock.tick() /1000
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            if self.data.current_level==6:
                pygame.quit()
                sys.exit()
            self.game_end()
            self.current_stage.run(dt)
            self.ui.update(dt)
            pygame.display.update()

if __name__=="__main__":

    game=Game()
    game.run()
                    
