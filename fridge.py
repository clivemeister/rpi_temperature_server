from collections import Counter

class Fridge():
    
    contents = {}

    def __init__ (self,red_count = 0, blue_count = 0, green_count = 0):
        self.contents = Counter({'red_can': red_count, 'blue_can': blue_count, 'green_can': green_count})

    def set_red_can(self,n=0):
        self.contents['red_can'] = n
    def set_green_can(self,n=0):
        self.contents['green_can'] = n
    def set_blue_can(self,n=0):
        self.contents['blue_can'] = n

    def get_red_can(self):
        return self.contents['red_can']
    def get_green_can(self):
        return self.contents['green_can']
    def get_blue_can(self):
        return self.contents['blue_can']
      
    def incr_can(self,canColour):
        self.contents[canColour] += 1
        return self.contents[canColour]
    def incr_red_can(self):
        return self.incr_can('red_can')
    def incr_green_can(self):
        return self.incr_can('green_can') 
    def incr_blue_can(self):
        return self.incr_can('blue_can')

    def decr_can(self,canColour):
        if self.contents[canColour] > 0:
           self.contents[canColour] -= 1
        return self.contents[canColour]
    def decr_red_can(self):
        return self.decr_can('red_can')
    def decr_green_can(self):
        return self.decr_can('green_can')
    def decr_blue_can(self):
        return self.decr_can('blue_can')

    def status(self):
        return repr(self.contents)
 

