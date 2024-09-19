
class Data:
    def __init__(self,ui):
        self.ui=ui
        self._coins=0
        self._health=5
        self.ui.create_hearts(self._health)
        self.unlocked_level=0
        self.current_level=0

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self,value):
        self._health=value
        self.ui.create_hearts(value)
        print(self._health)

    @property
    def coins(self):
        self.ui.coin_timer.activate()
        return self._coins
    
    @coins.setter
    def coins(self,value):
        if self._coins>=100:
            value=0
            self.health+=1
        self.ui.coins=value 
        self._coins=value 
        

        
        

    