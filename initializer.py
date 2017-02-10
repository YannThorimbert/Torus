import pygame
import thorpy
import parameters
import gui


def get_object(img, oktext, funcok, name, skills, star):
    eimage = thorpy.Image.make(img)
    eok = thorpy.make_button(oktext, func=funcok)
    ename = thorpy.make_text(name)
##    sk1 = thorpy.make_text(s1)
    #
    star_full = thorpy.change_color_on_img(star, (255,0,255), (255,201,14), (255,255,255))
    star_empty = thorpy.change_color_on_img(star, (255,0,255), (255,255,255), (255,255,255))
    w,h = star.get_size()
    stars = thorpy.Element.make(size=(5*w,2*h*len(skills)))
    skill_elements = []
    for skillname in skills:
        value = skills[skillname]
        sname = thorpy.make_text(skillname+": ")
        nfill = int(value*5)
        nempty = 5 - nfill
        elements = [sname]
        for i in range(nfill):
            elements.append(thorpy.Image.make(star_full))
        for i in range(nempty):
            elements.append(thorpy.Image.make(star_empty))
        skill_elements.append(thorpy.make_group(elements))
    eskill = thorpy.Box.make(skill_elements)
    #
    e = thorpy.Element.make(elements=[eimage, ename, eskill, eok])
    thorpy.store(e, mode="h")
    e.fit_children()
    return e


def get_controllable_choice(title, imgs, names, skills, description,
                            oktext="Hire",star=None):
    img1, img2 = imgs
    name1, name2 = names
    s1, s2 = skills
    description = thorpy.pack_text(300,description)
    class Choice:
        value = None
    def choose1():
        Choice.value = 0
        thorpy.functions.quit_menu_func()
    def choose2():
        Choice.value = 1
        thorpy.functions.quit_menu_func()
    #

    #
    e1 = get_object(img1, oktext, choose1, name1, skills[0], star)
    e2 = get_object(img2, oktext, choose2, name2, skills[1], star)
    #
    edescr = thorpy.make_text(description)
    etitle = thorpy.make_text(title, font_size=thorpy.style.FONT_SIZE+3,
                                font_color = gui.TCOLOR)
    box = thorpy.Box.make([etitle,edescr,e1,e2])
    box.center()
    #
    m = thorpy.Menu([box])
    m.play()
    return Choice.value