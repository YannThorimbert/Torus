import numpy as np
import pygame
from pygame.math import Vector2
import thorpy
import parameters
import terrain

TCOLOR = (0,0,100)

AZERTY = False

def get_layout_keys():
    if AZERTY:
        return [pygame.K_q, pygame.K_d, pygame.K_z, pygame.K_s]
    else:
        return [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s]



def make_line(elements):
    for i in range(1,len(elements)):
        elements[i].stick_to(elements[i-1],"right","left")

def get_line_info(pre, command, post, dsize=0, color=(0,255,0)):
    e1 = thorpy.make_text(pre,font_size=thorpy.style.FONT_SIZE+dsize)
    e2 = thorpy.make_text(command, font_size=thorpy.style.FONT_SIZE+3+dsize,
                                    font_color=color)
    e3 = thorpy.make_text(post,font_size=thorpy.style.FONT_SIZE+dsize)
    line = [e1,e2,e3]
    make_line(line)
    return line


def blit_line(elements, x, y):
    dy = y - elements[0].get_fus_rect().y
    dx = x - elements[0].get_fus_rect().x
    for e in elements:
        e.move((dx,dy))
        e.blit()


class AlertMonitor:

    def __init__(self, game):
##        self.line_boarding = get_line_boarding()
        self.line_boarding = get_line_info("Press ", "space", " to board/unload ship")
        self.line_flag = get_line_info("Press ", "f", " to plant flag")
        self.line_treasure = get_line_info("Press ", "t", " to get treasure")
        self.line_flag_take = get_line_info("Press ", "r", " to read/take flag")
        self.line_village = get_line_info("Press ", "e", " to exchange food")
        self.line_camp = get_line_info("Press ", "c", " to camp/uncamp")
        self.line_hunt = get_line_info("Press ", "h", " to hunt")
        self.line_cannibal = get_line_info("Critical food! Press ", "x", " to cannibalize crew ...",4,(255,0,0))
        self.line_wait = get_line_info("Press ", "p", " to wait until next season")
        self.x = 5
        self.y = 5
        self.alerts = []
        self.game = game
        self.dh = self.line_boarding[1].get_fus_rect().h + 3

    def blit(self):
        y = self.y
        if self.game.can_board:
            blit_line(self.line_boarding, self.x, y)
            y += self.dh
        if self.game.near_treasure:
            blit_line(self.line_treasure, self.x, y)
            y += self.dh
        if self.game.near_flag is None:
            if self.game.can_flag:
                blit_line(self.line_flag, self.x, y)
                y += self.dh
        else:
            blit_line(self.line_flag_take, self.x, y)
            y += self.dh
        if self.game.can_camp:
            blit_line(self.line_camp, self.x, y)
            y += self.dh
        if self.game.near_camp and not self.game.aboard:
            blit_line(self.line_hunt, self.x, y)
            y += self.dh
            blit_line(self.line_wait, self.x, y)
            y += self.dh
        if self.game.near_village:
            blit_line(self.line_village, self.x,y)
            y += self.dh
        for a in self.alerts:
            a.set_topleft((self.x,y))
            a.blit()
            y += self.dh
            a.fading_i -= 1
        for a in self.alerts:
            if a.fading_i < 0:
                self.alerts.pop(0)
        if self.game.stock.food < parameters.CRITICAL_FOOD:
            if len(self.game.living_chars) > 1:
                blit_line(self.line_cannibal, self.x, y)
                y += self.dh


    def launch_fading_alert(self, text, color=(255,0,0),
                                        size=thorpy.style.FONT_SIZE):
        if isinstance(size, str):
            size = thorpy.style.FONT_SIZE + int(float(size))
        e = thorpy.make_text(text,font_color=color,font_size=size)
        e.fading_i = parameters.I_FADING
        self.alerts.append(e)

    def launch_failure_alert(self, text):
        self.launch_fading_alert(text, parameters.COLOR_FAIL,
                                int(thorpy.style.FONT_SIZE*parameters.FAIL_FACTOR))

    def launch_success_alert(self, text):
        self.launch_fading_alert(text, parameters.COLOR_SUCCESS,
                                int(thorpy.style.FONT_SIZE*parameters.SUCCESS_FACTOR))


class LifeBar(thorpy.Element):

    def __init__(self, text, color=(255,165,0), text_color=(0,0,0),
                    size=parameters.LIFEBAR_SIZE):
        thorpy.Element.__init__(self)
        painter = thorpy.painterstyle.ClassicFrame(size,
                                                    color=thorpy.style.DEF_COLOR,
                                                    pressed=True)
        self.set_painter(painter)
        self.finish()
        #
        self.life_text = thorpy.make_text(text,font_color=text_color)
        self.life_text.center(element=self)
        self.life_color = color
        self.add_elements([self.life_text])
        self.life_width = size[0]-2
        self.life_rect = pygame.Rect(1,1, self.life_width,size[1]-2)

    def set_life_text(self, text):
        self.life_text.set_text(text)
        self.life_text.center(element=self)

    def blit(self):
        """Recursive blit"""
        self._clip_screen()
        for e in self._blit_before:
            e.blit()
        if self.visible:
            self.solo_blit()
            pygame.draw.rect(self.surface, self.life_color, self.life_rect)
        for e in self._blit_after:
            e.blit()
        self._unclip_screen()

    def move(self,shift):
        thorpy.Element.move(self,shift)
        self.life_rect.move_ip(shift)

    def set_life(self,life):
        self.life_rect.width = int(life*self.life_width)




class GUI:

    def __init__(self, game):
        self.game = game
        self.game.gui = self
        self.e_chars = {c:None for c in self.game.chars()}
        #
        import scenario
        def l_func_after():
##            self.game.element.blit()
            self.game.cam.show(self.game.screen)
            self.game.blit_things()
            self.e_pause.blit()
            pygame.display.flip()
        def launch_stats():
            scenario.launch(self.get_stats(), l_func_after)
        def save_game():
            game.autosave()
            thorpy.launch_blocking_alert("Game saved")
            l_func_after()
        self.e_controls = thorpy.make_button("See instructions", scenario.launch,
                                    {"e":game,"func":l_func_after})
        #
        self.e_save = thorpy.make_button("Save game",save_game)
        self.e_stats = thorpy.make_button("Statistics", launch_stats)
        self.e_options = thorpy.make_button("Options",launch_options)
        #
        self.e_pause = thorpy.make_ok_cancel_box([self.e_controls, self.e_save,
                                                    self.e_stats, self.e_options],
                                                  "Continue game", "Quit game")
        #
        self.pause_launcher = thorpy.get_launcher(self.e_pause,
                                                    launching=game.element)
        self.e_options.user_params = {"game":game,"epause":self.e_pause}
        reac_esc = thorpy.ConstantReaction(pygame.KEYDOWN,
                                            self.pause_launcher.launch,
                                            {"key":pygame.K_ESCAPE})
        self.game.element.add_reaction(reac_esc)
        self.e_pause.set_main_color((200,200,255,100))
        def quit_game():
            thorpy.launch_blocking_choices("This will quit the game. Make sure you saved the game.",
                                            [("Ok",thorpy.functions.quit_func),
                                                ("Cancel",None)])
            l_func_after()
        self.e_pause.e_cancel.user_func = quit_game
        self.e_pause.e_cancel.user_params = {}

    def get_stats(self):
        stats = self.game.stats.get()
        elements = [thorpy.make_text("Trip Statistics",
                    thorpy.style.TITLE_FONT_SIZE, TCOLOR),
                    thorpy.Line.make(200, "h")]
        for title,value,post in stats:
            value = " : " + str(round(value,1))
            elements.append(thorpy.make_text(title+value+" "+post))
        box = thorpy.make_ok_box(elements)
        box.e_ok.user_func = thorpy.functions.quit_menu_func
        box.e_ok.user_params = {}
        box.center()
        return box




def set_game_gui(game, compass_pos, compass, thermo_pos, thermo):
    game.e_temp = thorpy.make_text("99 C ")
    game.e_temp.stick_to("screen","right","right")
    game.e_temp.set_topleft((thermo_pos[0],
                                compass_pos[1]+compass.get_height()+5))
    #
    game.e_alt = thorpy.make_text("Alt.: 9000 m")
    game.e_x = thorpy.make_text("X: 9000 m")
    game.e_y = thorpy.make_text("Y: 9000 m")
    game.e_coords = thorpy.Element.make(elements=[game.e_alt,
                                                    game.e_x,game.e_y])
    game.e_coords.set_main_color((200,200,255,100))
    thorpy.store(game.e_coords)
    game.e_coords.fit_children(margins=(15,2))
    game.e_coords.set_topleft(Vector2(thermo_pos)+\
                                (0,thermo.get_size()[1]+10))
    game.e_coords.stick_to("screen","right","right",align=False)
    game.e_coords.move((-5,0))
    #
##        game.life_ship = get_lifebar("Ship")
    game.e_food = LifeBar("Food", color=(0,255,0))
    game.e_life_ship = LifeBar("Ship seaworthy")
    game.e_life_a = LifeBar("Astronomer", color=parameters.A_COLOR)
    game.e_life_h = LifeBar("Hunter", color=parameters.H_COLOR)
    game.e_life_c = LifeBar("Captain", color=parameters.C_COLOR)
    #
    game.e_life = thorpy.Element.make(elements=[game.e_food,
                                                game.e_life_ship,
                                                thorpy.Line.make(80,"h"),
                                                thorpy.make_text("Life"),
                                                game.e_life_a,
                                                game.e_life_h,
                                                game.e_life_c])
    game.e_life.set_main_color((200,200,255,100))
    thorpy.store(game.e_life, gap=10)
    game.e_life.fit_children()
    game.e_life.set_topleft(Vector2(thermo_pos)+(0,thermo.get_size()[1]+10))
    game.e_life.stick_to(game.e_coords,"bottom","top")
    game.e_life.stick_to("screen","right","right",align=False)
    game.e_life.move((0,10))
    game.echars = {game.a:game.e_life_a, game.h:game.e_life_h, game.c:game.e_life_c}
    #
    game.e_clock = thorpy.make_text("Day 0",
                                        font_size=thorpy.style.FONT_SIZE+2)
    game.e_clock.stick_to(game.e_life,"top","bottom")
    game.e_clock.set_topleft((None,3))



def read_flag(flag):
    title = thorpy.make_text(flag.title, font_size=thorpy.style.FONT_SIZE+3,
                                font_color=TCOLOR)
    line = thorpy.Line.make(100, "h")
    text = thorpy.make_text(thorpy.pack_text(100, flag.text))
    elements = [title, line, text]
    class Choice:
        ok = False
    def func_cancel():
        Choice.ok = True
        thorpy.functions.quit_menu_func()
    box = thorpy.make_ok_cancel_box(elements, "Ok", "Take flag")
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    box.e_cancel.user_func = func_cancel
    box.e_cancel.user_params = {}
    box.center()
##    box.add_reaction(thorpy.ConstantReaction(pygame.KEYDOWN,
##                                             thorpy.functions.quit_menu_func,
##                                             {"key":pygame.K_SPACE}))
    m = thorpy.Menu([box])
    m.play()
    return Choice.ok

def read_treasure(treas):
    title = thorpy.make_text(treas.title, font_size=thorpy.style.FONT_SIZE+3,
                                font_color=TCOLOR)
    line = thorpy.Line.make(100, "h")
    text = thorpy.make_text(thorpy.pack_text(100, treas.text))
    elements = [title, line, text]
    class Choice:
        ok = False
    def func_cancel():
        Choice.ok = True
        thorpy.functions.quit_menu_func()
    box = thorpy.make_ok_cancel_box(elements, "No, let it there", "Yes, take it")
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    box.e_cancel.user_func = func_cancel
    box.e_cancel.user_params = {}
    box.center()
##    box.add_reaction(thorpy.ConstantReaction(pygame.KEYDOWN,
##                                             thorpy.functions.quit_menu_func,
##                                             {"key":pygame.K_SPACE}))
    m = thorpy.Menu([box])
    m.play()
    return Choice.ok

def writing():
    thorpy.parameters.KEY_DELAY = 30
    thorpy.parameters.KEY_INTERVAL = 100
    pygame.key.set_repeat(30,500)

def playing():
    thorpy.parameters.KEY_DELAY = 1000//parameters.FPS
    thorpy.parameters.KEY_INTERVAL = 1000//parameters.FPS
    pygame.key.set_repeat(1000//parameters.FPS,1000//parameters.FPS)

def plant_flag(flag):
    writing()
    varset = thorpy.VarSet()
    varset.add("title", value=str(flag.title), text="Flag name:", limits=(200,None))
    varset.add("text", value=str(flag.text), text="Text:",limits=(200,None))
    ps = thorpy.ParamSetter.make([varset])
    title = thorpy.make_text("Plant flag", font_size=thorpy.style.FONT_SIZE+3,
                                font_color=TCOLOR)
    line = thorpy.Line.make(100, "h")
    elements = [title, line, ps]
    class Choice:
        ok = False
    def func_cancel():
        Choice.ok = True
        thorpy.functions.quit_menu_func()
    box = thorpy.make_ok_cancel_box(elements, "Ok", "Cancel")
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    box.e_cancel.user_func = func_cancel
    box.e_cancel.user_params = {}
    box.center()
##    box.add_reaction(thorpy.ConstantReaction(pygame.KEYDOWN,
##                                             thorpy.functions.quit_menu_func,
##                                             {"key":pygame.K_SPACE}))
    m = thorpy.Menu([box])
    m.play()
    ps.save()
    playing()
    if not Choice.ok:
        flag.title = varset.get_value("title")
        flag.text = varset.get_value("text")
    return Choice.ok

def get_cannibalism(game):
    title = thorpy.make_text("Cannibalism", font_size=thorpy.style.FONT_SIZE+3,
                                font_color=TCOLOR)
    descr = thorpy.make_text("Who should be eaten by the others?")
    class Choice:
        choice = None
    def choice1():
        if thorpy.launch_binary_choice("Are you sure?"):
            Choice.choice = "a"
            thorpy.functions.quit_menu_func()
        else:
            box.unblit_and_reblit()
    def choice2():
        Choice.choice = "c"
        thorpy.functions.quit_menu_func()
    def choice3():
        Choice.choice = "h"
        thorpy.functions.quit_menu_func()
##    a = thorpy.make_button()
##    choices = [a, c, h, ("cancel",None)]
    a=thorpy.pack_text(150,"You won't be able to know your position anymore.")
    c=thorpy.pack_text(150,"Sailing will become very difficult. ")
    h=thorpy.pack_text(150,"Your chances of sucess while hunting will be very low.")
    choices = [(a,choice1), (c,choice2), (h,choice3), ("cancel",None)]
##    thorpy.launch_blocking_choices("Blocking choices box!\n", choices,
##                                    parent=game.element) #for auto unblit
##    launcher = thorpy.launch_choices("LOL", choices)
##    launcher.launch()

    ea = thorpy.make_button("Astronomer",choice1)
    ea.set_main_color((0,0,255))
    at = thorpy.make_text(a,font_size=thorpy.style.FONT_SIZE-2)
    ab = thorpy.make_group([ea,at],"v")
    #
    ec = thorpy.make_button("Captain", choice2)
    ec.set_main_color((255,0,0))
    ct = thorpy.make_text(c,font_size=thorpy.style.FONT_SIZE-2)
    cb = thorpy.make_group([ec,ct],"v")
    #
    eh = thorpy.make_button("Hunter", choice3)
    eh.set_main_color((0,255,0))
    ht = thorpy.make_text(h,font_size=thorpy.style.FONT_SIZE-2)
    hb = thorpy.make_group([eh,ht],"v")
    #
    cancel = thorpy.make_button("Cancel")
    cancel.set_as_menu_exiter()
    #
    bar1,bar2 = thorpy.Line.make(100,"h"),thorpy.Line.make(100,"h")
    #
    crew = []
    if game.a.life > 0:
        crew.append(ab)
    if game.h.life > 0:
        crew.append(hb)
    if game.c.life > 0:
        crew.append(cb)
    elements = [title,descr,bar1]+crew+[bar2,cancel]
##    box = thorpy.Element.make(elements=elements)
##    thorpy.store(box,mode="h")
    box = thorpy.Box.make(elements)
    box.center()
    m = thorpy.Menu([box])
    m.play()
    return Choice.choice

def get_journal(game):
    journal_title = thorpy.make_text("Journal", font_size=thorpy.style.FONT_SIZE+3,
                                font_color=TCOLOR)
    line = thorpy.Line.make(100, "h")
    elements = []
    #entries
    for name, day, coord, h, t, text in game.journal.entries:
        e_name = thorpy.make_text(name, font_color=(0,0,255))
        infos = thorpy.make_text(" ".join(["| Day", str(day),
                                  ", coord=", coord,
                                  ", alt=", str(round(h)),
                                  ", temp=", str(round(t))]),
                                  font_color=(50,50,150))
##            e_title = thorpy.Element.make(elements=[e_name,infos])
##            thorpy.store(e_title, mode="h")
        e_title = thorpy.make_group([e_name, infos])
        e_title.fit_children()
        elements.append(e_title)
        elements.append(thorpy.make_text("    "+thorpy.pack_text(400,text)))
    subbox = thorpy.Element.make(elements=elements,size=(500,300))
    thorpy.store(subbox, elements, x=3, y=0, align="left", gap=3)
    #
    def add_entry():
        add_journal_entry(game)
        thorpy.functions.quit_menu_func()
    ok = thorpy.make_button("Ok", func=thorpy.functions.quit_menu_func)
    add = thorpy.make_button("Add entry", func=add_entry)
    ok_add = thorpy.make_group([ok,add])
    #
    box = thorpy.Element.make(elements=[journal_title,subbox,ok_add])
    box.set_main_color((200,200,200,100))
    thorpy.store(box)
    box.fit_children()
    box.set_size((None,int(1.3*subbox.get_fus_rect().h)))
    #
    subbox.set_prison()
    subbox.refresh_lift()
##    box.add_reaction(thorpy.ConstantReaction(pygame.KEYDOWN,
##                                             thorpy.functions.quit_menu_func,
##                                             {"key":pygame.K_SPACE}))
    box.center()
    m = thorpy.Menu([box])
    m.play()

def add_journal_entry(game):
    writing()
    varset = thorpy.VarSet()
    varset.add("title", value="Entry "+str(len(game.journal.entries)+1),
                text="Title:", limits=(300,None))
    varset.add("text", value="", text="Text:",limits=(300,None))
    ps = thorpy.ParamSetter.make([varset])
    title = thorpy.make_text("Add journal entry", font_size=thorpy.style.FONT_SIZE+3,
                                font_color=TCOLOR)
    line = thorpy.Line.make(100, "h")
    elements = [title, line, ps]
    class Choice:
        ok = False
    def func_cancel():
        Choice.ok = True
        thorpy.functions.quit_menu_func()
    box = thorpy.make_ok_cancel_box(elements, "Ok", "Cancel")
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    box.e_cancel.user_func = func_cancel
    box.e_cancel.user_params = {}
    box.center()
    m = thorpy.Menu([box])
    m.play()
    ps.save()
    playing()
    if not Choice.ok:
        game.journal.add_entry(varset.get_value("title"),varset.get_value("text"))
    return Choice.ok



def manage_stocks(stock1, stock2):
    c = stock1.food + stock2.food #remains constant
    class Os1:
        v = stock1.food
    class Os2:
        v = stock2.food
    title = thorpy.make_text("Food stock management",
                                font_size=thorpy.style.FONT_SIZE+3,
                                font_color=TCOLOR)
    line = thorpy.Line.make(300, "h")
    def take_all():
        stock1.refood_from(stock2)
        thorpy.functions.quit_menu_func()
##    print(stock1,stock2)
    e_take = thorpy.make_button("Take all", func=take_all)
    s1 = thorpy.SliderX.make(length=350, limvals=(0, stock1.max_food),
                                text=stock1.name, type_=int,
                                initial_value=int(stock1.food))
    s2 = thorpy.SliderX.make(length=350, limvals=(0, stock2.max_food),
                                text=stock2.name, type_=int,
                                initial_value=int(stock2.food))
    e1 = thorpy.Box.make(elements=[s1])
    e2 = thorpy.Box.make(elements=[s2])
    arrow = thorpy.Image.make("doublearrow32.bmp", colorkey=(255,255,255))
    #
    box = thorpy.make_ok_cancel_box([title,line,e_take,e1,arrow,e2])
    box.set_main_color((200,200,255,150))
    box.center()
    #
    def refresh_sliders(e):
        ns1 = s1.get_value()
        ns2 = s2.get_value()
        if ns1 + ns2 > c:
            s1.unblit_and_reblit_func(s1.set_value, value=Os1.v)
            s2.unblit_and_reblit_func(s2.set_value, value=Os2.v)
            return
        if e.el is s1:
            new_value = c-ns1
            if new_value > s2.limvals[1]:
                new_value = s2.limvals[1]
            elif new_value < s2.limvals[0]:
                new_value = s2.limvals[0]
            s2.unblit_and_reblit_func(s2.set_value, value=new_value)
        elif e.el is s2:
            new_value = c-ns2
            if new_value > s1.limvals[1]:
                new_value = s1.limvals[1]
            elif new_value < s1.limvals[0]:
                new_value = s1.limvals[0]
            s1.unblit_and_reblit_func(s1.set_value, value=new_value)
        Os1.v, Os2.v = s1.get_value(), s2.get_value()
    reaction = thorpy.Reaction(reacts_to=thorpy.constants.THORPY_EVENT,
                                reac_func=refresh_sliders,
                                event_args={"id":thorpy.constants.EVENT_SLIDE})
    box.add_reaction(reaction)
    def func_ok():
        stock1.food = s1.get_value()
        stock2.food = s2.get_value()
        thorpy.functions.quit_menu_func()
    box.e_cancel.user_func = thorpy.functions.quit_menu_func
    box.e_cancel.user_params = {}
    box.e_ok.user_func = func_ok
    box.e_ok.user_params = {}
    menu = thorpy.Menu(box)
    menu.play()
##    def refresh_sliders(event, drag, sx, sy):
##        if event.el == drag:
##            pos_drag = drag.get_rect().topleft
##            sx.unblit_and_reblit_func(sx.set_value, value=pos_drag[0])
##            sy.unblit_and_reblit_func(sy.set_value, value=pos_drag[1])


def uncamp():
    class Choice:
        ok = False
    def ok():
        Choice.ok = True
    choices = [("Yes",ok), ("No, let camp here",None)]
    thorpy.launch_blocking_choices("Uncamp and take food?", choices,
                                    title_fontsize=thorpy.style.FONT_SIZE+3,
                                    title_fontcolor=TCOLOR,
                                    main_color=(200,200,255,150))
    return Choice.ok

def want_to_hunt():
    class Choice:
        ok = False
    def ok():
        Choice.ok = True
    choices = [("Yes",ok), ("No, forget about hunting",None)]
    text = "Spend one quiver to try to fill food stock?"
    thorpy.launch_blocking_choices(text, choices,
                                    title_fontsize=thorpy.style.FONT_SIZE+3,
                                    title_fontcolor=TCOLOR,
                                    main_color=(200,200,255,150))
    return Choice.ok

def get_options_elements():
    efont = thorpy.make_font_options_setter("./metadata", "Font Options")
    tmemory = thorpy.make_text("Memory usage", thorpy.style.TITLE_FONT_SIZE,
                                thorpy.style.TITLE_FONT_COLOR)
    text2 = thorpy.make_text("Set to 1 for no pre-loaded chunks (may work great on fast machines):")
    ememory = thorpy.SliderX.make(200, (1,1000),
                                    "Max Mb used",
                                    type_=int,
                                    initial_value=parameters.MAX_MEMORY_USAGE)
    esound = thorpy.Checker.make("Music",parameters.MUSIC)
    ereflect = thorpy.Checker.make("Ship reflect",parameters.REFLECT)
    eclouds = thorpy.Checker.make("Clouds reflects",parameters.NCLOUDS>0)
    eimpacts = thorpy.SliderX.make(200, (0,50),
                                    "Rain impacts (0 for deactivated)",
                                    type_=int,
                                    initial_value=parameters.RAIN_IMPACTS)
    tgraphics=thorpy.make_text("Graphics", thorpy.style.TITLE_FONT_SIZE,
                                thorpy.style.TITLE_FONT_COLOR)
    tmisc=thorpy.make_text("Misc. options", thorpy.style.TITLE_FONT_SIZE,
                                thorpy.style.TITLE_FONT_COLOR)
    return [tmisc, efont, esound, thorpy.Line.make(100,"h"), tmemory, text2, ememory,
            thorpy.Line.make(100,"h"), tgraphics, ereflect, eclouds, eimpacts]

def get_options():
    els = get_options_elements()
    box = thorpy.make_ok_box(els)
    return thorpy.make_launcher(box, "Options"), els[6]


def launch_options(game, epause, mainmenu=False):
    els = get_options_elements()
    box = thorpy.make_ok_box(els)
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    box.center()
    m = thorpy.Menu(box)
    m.play()
    parameters.set_approx_memory_usage(els[6].get_value())
    parameters.MUSIC = els[2].get_value()
    if not parameters.MUSIC:
        pygame.mixer.music.stop()
    #
    parameters.REFLECT = els[9].get_value()
    hasclouds = els[10].get_value()
    parameters.RAIN_IMPACTS = els[11].get_value()
    if hasclouds:
        parameters.NCLOUDS = 5
    else:
        parameters.NCLOUDS = 0
    need_bisurf = hasclouds or parameters.RAIN_IMPACTS>0 or parameters.REFLECT
    if need_bisurf != parameters.BISURFACE:
        print("Changing camera type", need_bisurf)
        parameters.BISURFACE = not(parameters.BISURFACE)
        if not mainmenu:
            game.refresh_camera()
    if not mainmenu:
        if need_bisurf and parameters.NCLOUDS == 0:
            game.cam.clouds = []
    if not mainmenu:
        game.cam.show(thorpy.get_screen())
        game.blit_things()
    epause.blit()
    pygame.display.flip()

def launch_load_game(game,show):
    show_loading()
    thorpy.get_screen().fill((255,255,255))
    import os, savemanager
    files = [f for f in os.listdir("./") if f.endswith(".dat")]
    savelist = []
    class Choice:
        value = None
    def delete():
        Choice.value = "del"
    def cancel_func():
        Choice.value = "cancel"
    def load(filename):
        thorpy.launch_blocking_choices("What do you want to do ?",
                                [("Load",None),("Delete",delete),("Cancel",cancel_func)])
        if not Choice.value:
            game.savefile = filename
            thorpy.functions.quit_menu_func()
            thorpy.functions.quit_menu_func()
        else:
            if Choice.value == "del":
                if thorpy.launch_binary_choice("   Are you sure?   \n\n"):
                    os.remove(filename)
                    thorpy.functions.quit_menu_func()
            else:
                thorpy.get_screen().fill((255,255,255))
                frame.blit()
                pygame.display.flip()
    for f in files:
        date, size, epochtime, score = savemanager.get_infos(f)
        success = ""
        if float(score)>0:
            success = "\n*** Game successfully ended at day "+str(int(score))+" ***"
##        infos.append(epochtime, date, size, f)
        b = thorpy.make_button(date+"\n"+"World size: "+size+success,load,{"filename":f})
        savelist.append((epochtime,b))
    savelist.sort(key=lambda x:x[0],reverse=True)
    elist = [e for t,e in savelist]
    thorpy.style.BOX_RADIUS += 10
    box = thorpy.Box.make(elist,(int(0.6*parameters.S),int(0.8*parameters.S)))
    box.refresh_lift()
    thorpy.style.BOX_RADIUS -= 10
    title = thorpy.make_text("Load game", font_size=thorpy.style.FONT_SIZE+3,
                                font_color=TCOLOR)
    cancel = thorpy.make_button("Cancel",thorpy.functions.quit_menu_func)
    frame = thorpy.Element.make(elements=[title,box,cancel])
    thorpy.store(frame)
    frame.center()
    pygame.display.flip()
    m = thorpy.Menu(frame)
    m.play()
    #
    show()
    pygame.display.flip()

def show_loading():
    thorpy.get_application().fill((0,0,0))
    loading = thorpy.make_text("Loading ...", thorpy.style.TITLE_FONT_SIZE+5, (0,0,200))
    loading.center()
    loading.blit()
    pygame.display.flip()

def game_parameters_menu():
    writing()
    # VARSET
    varset = thorpy.VarSet()
    varset.add("difficulty",["easy","medium","hard"],text="Difficulty:")
    varset.add("worldx", value=str(parameters.WORLD_SIZE[0]),
                text="World X-size:", limits="int")
    varset.add("worldy", value=str(parameters.WORLD_SIZE[1]),
                text="World Y-size:", limits="int")
    varset.add("seasonmod", value=parameters.SEASON_MOD_DAYS,
                    text="Season duration (days):", limits=(6, 100))
    varset.add("seed", value=str(np.random.randint(0,1000000)), text="Seed:", limits="int")
    ps = thorpy.ParamSetter.make([varset])
    #
    title = thorpy.make_text("Game parameters", font_size=thorpy.style.FONT_SIZE+3,
                                font_color=TCOLOR)
    line = thorpy.Line.make(100, "h")
    elements = [title, line, ps]
    box = thorpy.make_ok_box(elements)
    box.center()
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    m = thorpy.Menu([box])
    m.play()
    ps.save()
    playing()
    return varset



def launch_main_menu():
    np.random.seed()
    from colorscale import get_summer
    terrain.DEEP_CONSTANT = 4
    if parameters.BISURFACE:
        camtype = terrain.CameraBisurface
    else:
        camtype = terrain.Camera
    cam = camtype(chunk=(100,100), pos=(0,0),
                            seed=np.random.randint(0,1000), world_size=(2,2))
    if parameters.BISURFACE:
        cam.iter_ship = parameters.nothing
    class FakeGame:
        def __init__(self):
            self.villages = []
            self.try_building_village = self.n
            self.try_building_oasis = self.n
            self.try_putting_treasure = self.n
            self.try_building_firs = self.n
            self.clouds = []
            self.storm = False
            self.is_winter = False
            self.savefile = None
            class FakeControlled:
                def __init__(self):
                    self.velocity = -Vector2(0.1,0.1)
            self.controlled = FakeControlled()

        def n(self,a,b):
            pass
    cam.game = FakeGame()
    game = cam.game
    for i in range(3):
        img = thorpy.load_image("clouds"+str(i)+".png",(0,0,0))
        img.set_alpha(parameters.CLOUD_ALPHA)
        game.clouds.append(img)
    cam.set_colorscale(get_summer())
    screen = thorpy.get_screen()
    show_loading()
##    tmp = parameters.REFLECT
##    parameters.REFLECT = False
    class Pos:
        pos = np.zeros(2)
    def show():
        if parameters.BISURFACE:
            cam.iter_clouds()
        cam.show(screen)
        etitle.solo_blit()
        box.blit()
        pygame.display.flip()
        Pos.pos += (0.4,0.4)
        cam.pos = np.array(Pos.pos,dtype=int)
    #
    def launch_credits():
        text = "Author: Yann Thorimbert (yann.thorimbert@gmail.com)\n"+\
                "Libraries used: NumPy, Pygame, ThorPy (www.thorpy.org)\n\n"+\
                "If you are interested in the procedural world generation technique used in this game, please do not hesitate to contact the author."
        text = thorpy.pack_text(int(0.8*parameters.S), text)
        thorpy.launch_blocking_alert(text)
    etitle = thorpy.make_text("The Torus",
                                font_size=2*thorpy.style.TITLE_FONT_SIZE,
                                font_color=(0,0,100))
    etitle.stick_to("screen","top","top")
    etitle.move((0,30))
    eplay = thorpy.make_button("New Game", func=thorpy.functions.quit_menu_func)
    eload = thorpy.make_button("Load game", launch_load_game, {"game":game,"show":show})
    eoptions, memory = get_options()
    ecredits = thorpy.make_button("Credits", launch_credits)
    equit = thorpy.make_button("Quit", func=thorpy.functions.quit_func)
    box = thorpy.Box.make([eplay,eload,eoptions,ecredits,equit])
    box.add_reaction(thorpy.ConstantReaction(thorpy.USEREVENT+2, show))
    box.center()
    box.set_main_color((200,200,255,150))
    eoptions.user_func = launch_options
    eoptions.user_params = {"game":None,"epause":box,"mainmenu":True}
    m = thorpy.Menu(box,fps=parameters.FPS)
    show()
    pygame.time.set_timer(thorpy.USEREVENT+2,1000//parameters.FPS)
    m.play()
    pygame.time.set_timer(thorpy.USEREVENT+2,0)
    terrain.DEEP_CONSTANT = 1
    parameters.set_approx_memory_usage(memory.get_value()) #in MB
##    if parameters.REFLECT != tmp: #may have been changed
##        if not parameters.REFLECT:
##            parameters.REFLECT = True
    return game.savefile
