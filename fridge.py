from collections import Counter
import cherrypy

class Fridge():
    
    contents = {}
    can_types = {'red_can', 'blue_can', 'green_can'}
    needsRestock = False

    def __init__ (self,red_count = 0, blue_count = 0, green_count = 0):
        self.contents = Counter({'red_can': red_count, 'blue_can': blue_count, 'green_can': green_count})
        self.needsRestock = False

    def set_red_can(self,n=0):
        self.contents['red_can'] = n
        self.check_stock()
    def set_green_can(self,n=0):
        self.contents['green_can'] = n
        self.check_stock()
    def set_blue_can(self,n=0):
        self.contents['blue_can'] = n
        self.check_stock()

    def get_red_can(self):
        return self.contents['red_can']
    def get_green_can(self):
        return self.contents['green_can']
    def get_blue_can(self):
        return self.contents['blue_can']
      
    def incr_can(self,canColour):
        assert canColour in self.can_types
        self.contents[canColour] += 1
        self.check_stock()
        return self.contents[canColour]
    def incr_red_can(self):
        return self.incr_can('red_can')
    def incr_green_can(self):
        return self.incr_can('green_can') 
    def incr_blue_can(self):
        return self.incr_can('blue_can')

    def decr_can(self,canColour):
        assert canColour in self.can_types 
        if self.contents[canColour] > 0:
           self.contents[canColour] -= 1
           self.check_stock()
        return self.contents[canColour]
    def decr_red_can(self):
        return self.decr_can('red_can')
    def decr_green_can(self):
        return self.decr_can('green_can')
    def decr_blue_can(self):
        return self.decr_can('blue_can')

    def check_stock(self):
        restock = False
        for can_type, stock_level in self.contents.items():
            restock |= (stock_level <=1)
        self.needsRestock = restock
        return self.needsRestock

    def restock(self):
        """ Restock the fridge back to standard levels
            Returns the number of cans added
        """
        added_cans = 0
        for can_colour, stock_level in self.contents.items():
            if can_colour=="red_can":
                if stock_level<4:
                    added_cans += 4 - stock_level
                    self.contents["red_can"] = 4
            else:
                if (stock_level<2):
                    added_cans += 2 - stock_level
                    self.contents[can_colour] = 2
        self.needsRestock = False
        return added_cans

    def status(self):
        return repr(self.contents)
 

