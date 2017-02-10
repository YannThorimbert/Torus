import pygame
import thorpy
import parameters
import gui
from pygame.math import Vector2


def launch_end_text(score):
    screen = thorpy.get_screen()
    title_text = "The End - Score : " + str(score) + " days"
    title = thorpy.make_text(title_text, thorpy.style.TITLE_FONT_SIZE, gui.TCOLOR)
    text = "Your expedition was a success. After that long trip, you are back to civilization. "+\
            " Perigeo's compass and seals were undoubtedly recognizable, and their memory will now be teached at school."
    end_text = "Regarding yourself and your crew, you will be recorded in the centuries to come as the first to complete a round aroud the world.\n"+\
    " Which has been proven to be a torus."
    end_text = thorpy.pack_text(400,end_text)
    end = thorpy.make_text(end_text, thorpy.style.TITLE_FONT_SIZE, gui.TCOLOR)
    letter = thorpy.make_text(thorpy.pack_text(int(0.7*parameters.S),text))
    w = letter.get_fus_rect().w + 10
    boxletter = thorpy.Box.make([letter],(w,parameters.S//2))
    boxletter.refresh_lift()
    thorpy.style.BOX_RADIUS += 10
    box = thorpy.make_ok_box([title,boxletter,end],"Quit")
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    box.set_main_color((200,200,255))
    box.center()
    thorpy.style.BOX_RADIUS -= 10
    launch(box)


def launch_perigeo_text():
    screen = thorpy.get_screen()
    title_text = "Dear visitor,\nI apologize for the welcome, which could have been warmer...\n"
    title = thorpy.make_text(title_text, thorpy.style.TITLE_FONT_SIZE, gui.TCOLOR)
    text = "But the crew's death does not help. I tried my best to prove that the world is toroidal."+\
    " According to the theory, my ship has gone beyond the half-perimeter, and we still did not recognize any of the landscapes"+\
    " that some of us saw as members of former Settentrio's expeditions. As a result, I am convinced of the toroidal nature of the world."+\
    " As a proof of my presence so far on the East - well, it is actually the West side of the world now - let my bones on the wild. But..."
    end_text = "... bring my compass and my seal back to civilization, and show them that I was right.\n          Gottfried Perigeo"
    end_text = thorpy.pack_text(400,end_text)
    end = thorpy.make_text(end_text, thorpy.style.TITLE_FONT_SIZE, gui.TCOLOR)
    letter = thorpy.make_text(thorpy.pack_text(int(0.7*parameters.S),text))
    w = letter.get_fus_rect().w + 10
    boxletter = thorpy.Box.make([letter],(w,parameters.S//2))
    boxletter.refresh_lift()
    thorpy.style.BOX_RADIUS += 10
    box = thorpy.make_ok_box([title,boxletter,end],"Accept")
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    box.set_main_color((200,200,255))
    box.center()
    thorpy.style.BOX_RADIUS -= 10
    launch(box)


def get_intro_text():
    image = thorpy.load_image("message_in_a_bottle_by_solid_pawn.png")
    image = pygame.transform.scale(image, (parameters.S,parameters.S))
    title_text = "Dear friend,\nA few years ago, I found a message in a bottle near the sea...\n"
    title = thorpy.make_text(title_text, thorpy.style.TITLE_FONT_SIZE, gui.TCOLOR)
    text = "At that time, I was working hard on that famous Topological Astronomy Problem and I began to inattentively read the message..."+\
            "But to my great surprise, it appeared that the author of the letter, a certain Gottfried Perigeo,"+\
            " was trying to complete a mad - though so brave! - travel around the world, following West-East axis, almost one century ago.\n\n"+\
            "    Except the fact that the poor explorer sent a desperate SOS message that was obviously received hundred year too late,"+\
            " my interest was peaked by the singular axis he was travelling. Here the story joins the Topological Astronomy Problem.\n\n"+\
            "    Indeed, my dear friend, I was - and I'm still - one of the rare physicists to believe that the world has the topology of a torus"+\
            " (explain uneducated people that it's like donut). Despite several celestial hints, most of my colleagues give no credit in this theory, and invest"+\
            "all their energy in proving that our planet is spherical. The situation was the same during Perigeo's life ; since the famous"+\
            "explorer Girato Settentrio completed the South-North around the world travel, it was clear that Gottfried Perigeo thought the planet"+\
            "is a torus , otherwise the travel he initiated was a suicide, because of the absolute extreme difficulty of the West-East round trip, if it exists.\n\n"+\
            "    I know you trust in my science, my friend, and I have to admit you are one of the few ones. Here is my demand:\n"+\
            "Take all my money. Buy ship, hire mens, prepare a big exploration trip. Find Perigeo's shipwreck, pursue his travel, and finish what he began. Bring back with you a keepsake of Perigeo. He deserves it.\n"+\
            "\n        You cannot let him in here."
    end_text = "Prove the world that our planet is toroidal!"
    end = thorpy.make_text(end_text, thorpy.style.TITLE_FONT_SIZE, gui.TCOLOR)
    letter = thorpy.make_text(thorpy.pack_text(int(0.7*parameters.S),text))
    w = letter.get_fus_rect().w + 10
    boxletter = thorpy.Box.make([letter],(w,parameters.S//2))
    boxletter.set_main_color((200,200,255,50))
    boxletter.refresh_lift()
    thorpy.style.BOX_RADIUS += 10
    box = thorpy.make_ok_box([title,boxletter,end],"Accept")
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    box.set_main_color((200,200,255,80))
    box.center()
    background = thorpy.Background(image=image,elements=[box])
    thorpy.style.BOX_RADIUS -= 10
    return background

def make_instruction(text):
    splits = text.split(":")
    title, corpus = splits[0], "".join(splits[1:])
    corpus = thorpy.pack_text(int(0.6*parameters.S), corpus)
    etitle = thorpy.make_text(title, font_color=(255,0,0))
    ecorpus = thorpy.Element.make(corpus)
    return thorpy.make_group([etitle, ecorpus])

def get_instructions():
    title = thorpy.make_text("Instructions", thorpy.style.TITLE_FONT_SIZE,
                                gui.TCOLOR)
    perig_coord = (Vector2(parameters.WRECK_COORD)*parameters.S)//10
    cordtext = "Coordinates of Gottfried Perigeo's wreckage: not far from"+str(perig_coord)
    ecoord = make_instruction(cordtext)
    #
    jtext = "Journal: Press J to open crew's logbook. It lists a lot of events, and allow you to add entries."
    ejournal = make_instruction(jtext)
    #
    ftext = "Flags: You have "+str(parameters.MAX_FLAGS)+" flags at your disposal to help you locate. Press F to plant a flag on the ground. You can remove flags. Flags automatically add entries in logbook."
    eflag = make_instruction(ftext)
    #
    stext = "Seasons: Seasons change the terrain and the temperatures. Season change are every "+str(parameters.SEASON_MOD_DAYS)+" day from day zero."
    eseason = make_instruction(stext)
    #
    foodtext = "Food: Crew has to eat in order to survive. Remaining food is schematized by a gauge on the right. Low temperature result in higher demand in food. "+\
                "Ship can carry a limited amount of food, as well as the crew when walking. You can store food from/into villages and camps. You can obtain food by hunting."
    efood = make_instruction(foodtext)
    #
    huntext = "Hunting: Crew members are able to hunt if there are arrows in your stock. Sucessful hunting refill your food bar. The chance to find food depends on the temperature and the skills of the best hunter in your crew."
    ehunt = make_instruction(huntext)
    #
    vtext = "Village: Villages contains and produce food along the year. You can exchange food with villages by pressing E. However, villages become more rare as you go far from civilization."
    evillage = make_instruction(vtext)
    #
    camptext = "Camp: You can camp/uncamp by pressing C. You have "+str(parameters.MAX_CAMPS)+" camps at your disposal. You need a camp to hunt and to wait. As for villages, you can exchange food with camps."
    ecamp = make_instruction(camptext)
    #
    wtext = "Weather: Altitude influe temperature. Wind is schematized by a line over the compass. Wind moves the ship. Sometimes, violent storms can appear."
    eweather = make_instruction(wtext)
    #
    #
    waitext = "Waiting: You can wait for a chosen duration (in days) if you are in a camp. Crew still consume food during waiting. Waiting will be stopped if food level reaches zero. Press P."
    ewait = make_instruction(waitext)
    #
    #
    cannibalismtext = "Cannibalism: In extreme situations, you may take serious decisions... If your food level is null, press X to choose a crew member to eat."
    ecannibal = make_instruction(cannibalismtext)
    #
    #
    oasistext = "Oasis: During summer, you can find food in oasises."
    eoasis = make_instruction(oasistext)
    #
    #
    foresttext = "Forest: hunting near a forest increases by 20 percent your chances of finding food, in any season." #not really true
    eforest = make_instruction(foresttext)
    #
    elements = [ecoord,efood,ehunt,eoasis,eforest,ejournal,evillage,ecamp,eflag,eseason,eweather,ecannibal,ewait,]
    thorpy.style.BOX_RADIUS += 10
    boxletter = thorpy.Box.make(elements,(int(0.9*parameters.S),int(0.8*parameters.S)))
    boxletter.refresh_lift()
    box = thorpy.make_ok_box([title,boxletter])
    box.e_ok.user_func = thorpy.functions.quit_menu_func
    box.e_ok.user_params = {}
    box.set_main_color((200,200,255))
    box.center()
    thorpy.style.BOX_RADIUS -= 10
    return box

def launch(e, func=None):
    if not isinstance(e, thorpy.Ghost):#dirty hack because I'm lazy
        e = e.instructions
    print("launching",e)
    m = thorpy.Menu(e)
    m.play()
    if func:
        func()



