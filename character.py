import thorpy
import parameters
from controllable import Controllable

class Character(Controllable):

    def __init__(self, name, color):
        Controllable.__init__(self)
        self.name = name
        self.life = 1.
        self.hunting = 0.1
        self.ship_skill = 0.1
        self.color = color
        self.img = thorpy.graphics.get_aa_ellipsis((parameters.CHAR_SIZE,
                                                    parameters.CHAR_SIZE),
                                                    (0,0,0)) #already alpha-converted
        interior = thorpy.graphics.get_aa_ellipsis((parameters.CHAR_SIZE-2,
                                                    parameters.CHAR_SIZE-2),
                                                    color)
        self.img.blit(interior,(1,1))
        self.death_text = ""
        self.weakness = 0.
        self.aboard = True

    def refresh_life(self, stock, temperature_bad):
        tmp = self.life
        self.life -= parameters.TBAD_FACTOR*temperature_bad*(self.weakness+0.2)
        food_consumption = min(stock.food, parameters.FOOD_PER_TURN)
        self.life += food_consumption
        stock.food -= food_consumption
        if stock.food < 0:
            stock.food = 0
        self.control_life()
        return tmp != self.life

    def compute_collision_factor(self, collisions, level):
        factor = 0.
        for h in collisions:
            if h < level:
                factor += 1.
        return min((parameters.SWIMMING, factor / parameters._NCOLL))
