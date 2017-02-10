from pygame.math import Vector2
import parameters

class FoodStock:

    def __init__(self, n):
        self.n = n
        self.max_food = int(parameters.MAX_WSF*n/3.)
        self.food = 0
        self.name = "bla"

    def refood_from(self, stock):
        lack = self.max_food - self.food
        qty = min(lack, stock.food)
        self.food += qty
        stock.food -= qty

    def make_consistent(self):
        if self.food > self.max_food: self.food = self.max_food
        if self.food < 0: self.food = 0

    def set_food(self, food):
        self.food = food
        self.make_consistent()

    def add_food(self, qty):
        self.food += qty
        self.make_consistent()

class Tile:

    def __init__(self, img=None, img_pos=None):
        self.img = img
        self.img_pos = img_pos

    def blit(self, screen):
        screen.blit(self.img, self.img_pos)


    def refresh_img_pos(self, game, delta=None):
        if delta is None: delta = game.controlled.velocity
        self.img_pos -= delta
        #the if is to allow for partial blitting, avoid sudden apparition.
        if abs(self.img_pos[0]) > parameters.S:
            self.img_pos[0] %= game.cam.world_size[0]*parameters.S
        if abs(self.img_pos[1]) > parameters.S:
            self.img_pos[1] %= game.cam.world_size[1]*parameters.S

class Flag(Tile):

    def __init__(self, img=None, img_pos=None, title="Flag", text="No text"):
        Tile.__init__(self, img, img_pos)
        self.title = title
        self.text = text

class Treasure(Flag): #degeulasse mais rapide

    def __init__(self, img, img_pos, food, n_hunt, chunk):
        Flag.__init__(self, img, img_pos, "Treasure")
        supp_text = ""
        if food > 0:
            text_food = str(food) + " food"
        if n_hunt > 0:
            text_hunt = str(n_hunt) + " quiver" + "s"*(n_hunt>1)
        if food > 0 and n_hunt > 0:
            supp_text = text_food + " and " + text_hunt
        elif food > 0:
            supp_text = text_food
        elif n_hunt > 0:
            supp_text = text_hunt
        text = "You have found a treasure containing " + supp_text + ".\n Do you want to take it?"
        self.text = text
        self.food = food
        self.n_hunt = n_hunt
        self.chunk = chunk

class Controllable(Tile):

    def __init__(self):
        Tile.__init__(self)
        self.img_pos = Vector2()
        self.velocity = Vector2()
        self.last_pos = Vector2()
        self.destination = None
        self.currently_animated = False

    def control_life(self):
        if self.life > 1.:
            self.life = 1.
        elif self.life < 0.:
            self.life = 0.

    def get_current_pos(self, cam):
        return self.img_pos + cam.pos

    def refresh_last_position(self, cam):
        current_pos = self.get_current_pos(cam)
        if current_pos.distance_to(self.last_pos) > parameters.DELTA_POS:
            self.last_pos = current_pos

    def set_velocity_to_destination(self, cam, destination, velocity_norm):
        self.destination = Vector2(destination)
        self.velocity = self.destination - self.get_current_pos(cam)
        self.velocity.scale_to_length(velocity_norm)