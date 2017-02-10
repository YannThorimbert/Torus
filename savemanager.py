#parameters.py !!...
import numpy as np
from pygame.math import Vector2
from controllable import Flag
import time
import parameters

GAME_ATTRS = ["i","season_idx","next_season","does_perigeo","score","n_hunt","is_winter","campos","aboard"]
CAM_ATTRS = ["seed","pos","chunk"]
VILLAGES_ATTRS = ["food","pos","type"]
STATS_ATTRS = ["dist","alt","last_pos","last_alt","mMalt","mMtemp","maxSpeed"]
CHARS_ATTRS = ["life","img_pos","weakness","hunting","ship_skill","aboard"]
FLAGS_ATTRS = ["img_pos","title","text"]
JOURNAL_ATTRS = ["entries"]
TREAS_ATTRS = ["food","img_pos","n_hunt","text"]
SHIP_ATTRS = ["life","food","img_pos","dead","model"] #appeller autoset_captain

def stringize_object(name, obj, attrs):
    text = "*"+name+"\n"
    for a in attrs:
        text += "@"+a+"="+str(getattr(obj,a))+"\n"
    return text

def stringize_parameters():
    text = ""
    for p in parameters.__dict__:
        if not p.startswith("_") and not p[0].islower():
            text += "@"+p+"="+str(getattr(parameters,p))+"\n"
    return text


def save_game(fn, game):
    text = "*date " + time.asctime()+"\n"
    text += "@epochtime="+str(time.time())+"\n"
    text += stringize_object("game",game,GAME_ATTRS)
    text += stringize_object("cam",game.cam,CAM_ATTRS)
    for v in game.villages:
        text += stringize_object("village "+v.type+" "+str(v.id),v,VILLAGES_ATTRS)
    if game.is_winter:
        for o in game.oasises:
            text += stringize_object("oasis "+str(o.id),o,VILLAGES_ATTRS)
    text += stringize_object("ship",game.ship,SHIP_ATTRS)
    text += stringize_object("astronomer",game.a,CHARS_ATTRS)
    text += stringize_object("captain",game.c,CHARS_ATTRS)
    text += stringize_object("hunter",game.h,CHARS_ATTRS)
    for f in game.flags:
        text += stringize_object("flag "+str(f.img_pos),f,FLAGS_ATTRS)
##    for t in game.treasures:
##        text += stringize_object("treasure "+str(t.chunk),t,TREAS_ATTRS)
    text += "*treasures_taken\n"
    for i,(x,y) in enumerate(game.treasures_taken):
        text += "@took"+str(i)+"="+str(x)+" "+str(y)+"\n"
##    text += stringize_object("journal",game.journal,JOURNAL_ATTRS)
    text += journal_to_str(game)
    text += stringize_object("stats",game.stats,STATS_ATTRS)
    text += "*parameters\n"
    text += stringize_parameters()
    f = open(fn,"w")
    f.write(text)
    f.close()

def listize_string(text,dtype):
##    assert text[0] == "[" and text[-1] == "]"
    type_ = int
    if dtype:
        if "float" in dtype:
            type_ = float
    text = text[1:-1]
    text = text.replace(",","")
    text = text.replace("(","")
    text = text.replace(")","")
    text = text.replace("[","")
    text = text.replace("]","")
    text = text.split(" ")
    if type_ is None: #auto
        for value in text:
            if value:
                if value.isdecimal():
                    type_ = int
                else:
                    type_ = float
                break
    text = [type_(value) for value in text if value]
    return text


def get_value(name, obj, stringval, type_):
    if "numpy" in type_:
        dtype=str(getattr(obj,name).dtype)
        s = listize_string(stringval,dtype)
        return np.array(s,dtype=dtype)
    elif "Vector2" in type_:
        s = listize_string(stringval,"float")
        return Vector2(s)
    elif "MinMax" in type_:
        s = tuple(listize_string(s,"float"))
        return type(getattr(obj,name))(s)
    elif "tuple" in type_:
        return tuple(listize_string(stringval,None))
    elif "list" in type_:
        return listize_string(stringval,None)
    else:
        real_type = type(getattr(obj,name))
        if real_type is bool:
            if stringval == "True":
                return True
            elif stringval == "False":
                return False
            else:
                raise Exception()
        else:
            return real_type(stringval)


def load_object(obj,objname,attrs,d):
    for a in attrs:
        s = d[objname][a]
        type_ = str(type(getattr(obj,a)))
        print(objname,a,s,type_)
        if "numpy" in type_:
            dtype=str(getattr(obj,a).dtype)
            s = listize_string(s,dtype)
            value = np.array(s,dtype=dtype)
        elif "Vector2" in type_:
            s = listize_string(s,"float")
            value = Vector2(s)
        elif "MinMax" in type_:
            s = tuple(listize_string(s,"float"))
            value = type(getattr(obj,a))(s)
        else:
            type_ = type(getattr(obj,a))
            if type_ is bool:
                if s == "True":
                    value = True
                elif s == "False":
                    value = False
                else:
                    raise Exception()
            else:
                value = type_(s)
        setattr(obj,a,value)

def get_infos(fn):
    d = dictize_file(fn)
    for k in d:
        if k.startswith("date"):
            date = k.replace("date ","")
    return date, d["parameters"]["WORLD_SIZE"], d["date "+date]["epochtime"], d["game"]["score"]

def dictize_file(fn):
    f = open(fn,"r")
    text = f.readlines()
    f.close()
    d = {}
    for line in text:
        assert line[-1] == "\n"
        line = line[0:-1]
        if line[0] == "*":
            obj = line[1:]
            if not obj in d:
                d[obj] = {}
        elif line[0] == "@":
            attr_name = line.split("=")[0][1:]
            attr_value = line[len(attr_name)+2:]
            d[obj][attr_name] = attr_value
        else:
            d[obj][attr_name] += line
    return d

def journal_to_str(game):
    text = ""
    i = 0
    args = "title", "day", "coord", "alt", "temp", "text"
    for entry in game.journal.entries:
        text += "*journalentry "+str(i)+"\n"
        for k,argname in enumerate(args):
            text += "@"+argname+"="+str(entry[k])+"\n"
        i += 1
    return text

def load_journal(game, d):
    entries = []
    for k in d:
        if "journal" in k:
            number = int(k.split(" ")[1])
##            title,day,coord,alt,temp,text = d[k]
            print("entry:",d[k])
            title = d[k]["title"]
            day = int(d[k]["day"])
            coord = d[k]["coord"]
            alt = int(d[k]["alt"])
            temp = float(d[k]["temp"])
            text = d[k]["text"]
            e = (number, (title,day,coord,alt,temp,text))
            entries.append(e)
    entries.sort()
    for e in entries:
        game.journal.entries.append(e[1])



class SaveManager:

    def __init__(self, fn):
        self.fn = fn
        self.d = dictize_file(fn)

    def load_parameters(self):
        params = self.d["parameters"]
        for name in params:
            value = params[name]
            type_ = type(getattr(parameters,name))
            print("Loading",name,value,type_)
            real_value = get_value(name, parameters, value, str(type_))
##            print(name, value, type_, real_value)
##            print()
            setattr(parameters,name,real_value)

    def load_game(self,game):
        game.save = self
        game.cam.saved_chunks = {}
        game.cam.villages = []
        game.treasures = []
        game.treasures_put = []
        game.villages = []
        game.oasies = []
        #
        d = self.d
        self.villages = {} #{chunk: (food,type,pos), ...}
##        self.oasises = {}
##        self.treasures = {}
        self.treasures_taken = []
        #GAME
        load_object(game,"game",GAME_ATTRS,d)
        #CAM
        load_object(game.cam,"cam",CAM_ATTRS,d)
        #VILLAGES (to use for retablishing correct food)
        for k in d.keys():
            if "village" in k:
                chunk = k[10:]
                if chunk != "None":
                    chunk = listize_string(chunk,"int")
                    chunk = tuple(chunk)
                else: #probably camp
                    chunk = None
                pos = np.array(listize_string(d[k]["pos"],"float"),dtype=float)
                food = int(d[k]["food"])
                type_ = d[k]["type"]
                self.villages[chunk] = (food, type_, pos)
                if type_ == "c":
                    game.build_camp()
                    c = game.villages[-1]
                    c.pos = pos
                    c.id = chunk
                    c.food = food
        #OASISES
##        if game.is_winter:
##            for k in d.keys():
##                if "oasis" in k:
##                    chunk = k.replace("oasis ","")
##                    chunk = listize_string(chunk,"int")
##                    chunk = tuple(chunk)
##                    pos = np.array(listize_string(d[k]["pos"],"float"),dtype=float)
##                    food = int(d[k]["food"])
##                    type_ = d[k]["type"]
##                    self.oasises[chunk] = (food, type_, pos)
        #TREASURES
##        for k in d.keys():
##            if "treas" in k:
##                chunk = k.replace("treasure ","")
##                chunk = listize_string(chunk,"int")
##                chunk = tuple(chunk)
##                food = int(d[k]["food"])
##                n_hunt = int(d[k]["n_hunt"])
##                self.treasures[chunk] = (food, n_hunt)
        for k in d.keys():
            if "taken" in k:
                tt = d["treasures_taken"]
                for took in tt:
                    print(tt[took])
                    chunk = tt[took].split(" ")
                    x,y = int(chunk[0]), int(chunk[1])
                    self.treasures_taken.append((x,y))
        #SHIP
        load_object(game.ship,"ship",SHIP_ATTRS,d)
        #CHARS
        load_object(game.a,"astronomer",CHARS_ATTRS,d)
        load_object(game.c,"captain",CHARS_ATTRS,d)
        load_object(game.h,"hunter",CHARS_ATTRS,d)
        #JOURNAL
    ##    load_object(game.journal,"journal",JOURNAL_ATTRS,d)
        load_journal(game,d)
        #STATS
        load_object(game.stats,"stats",STATS_ATTRS,d)
        #FLAGS
        for k in d.keys():
            if "flag" in k:
                img_pos = listize_string(k.replace("flag ",""),"float")
                img_pos = Vector2(img_pos)
                print("img_pos",k, img_pos)
                title = d[k]["title"]
                text = d[k]["text"]
                game.plant_flag(img_pos,title,text)
        #
        game.set_season(game.season_idx)
        game.living_chars = [c for c in game.chars() if c.life > 0]
        game.ship.autoset_captain(game)
        if game.aboard:
            game.board_ship()
        else:
            game.leave_ship()
        game.refresh_controlled()
        game.cam.pos = np.array(game.campos,dtype=int)
        game.next_season += 1
        game.saved = True


##d = dictize_file("save.dat")
##print(d)
