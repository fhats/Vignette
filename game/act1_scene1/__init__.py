import pyglet
import functools
import re

from engine import actor
from engine.interpolator import PulseInterpolator, LinearInterpolator
from engine.util.const import WALK_PATH_COMPLETED
from engine import ui
from engine import cam
from engine import gamehandler
from engine import gamestate
from engine import convo
from engine import util

# myscene is set by scene.py
myscene = None

levity_exposition = False
levity_direction = "right"

do_sit = False
sneelock_distracted = False

def init(fresh=False):
    print 'start'
    myscene.ui.inventory.visible = True
    
    myscene.begin_background_conversation("mumblestiltskin")
    
    myscene.play_music('simple', fade=False)
    myscene.play_background('Train_Loop1', fade=True)
    
    myscene.handler.handler.game_variables['temperature'] = 72
    
    if fresh:
        print 'fresh'
        myscene.interaction_enabled = False
        myscene.actors['levity'].prepare_walkpath_move("levity_4")
        myscene.actors['levity'].next_action()
    
        spcbux = myscene.new_actor('space_bucks', 'space_bucks')
        myscene.ui.inventory.put_item(spcbux)
        
    else:
        myscene.interaction_enabled = True

def transition_from(old_scene):
    if old_scene == 'act1_scene2':
        myscene.interaction_enabled = True
        myscene.actors['main'].walkpath_point = 'transition_left'
        myscene.actors['main'].sprite.position = myscene.walkpath.points['transition_left']
        myscene.actors['main'].prepare_walkpath_move('inga_attempt_silver_class')
        myscene.actors['main'].next_action()

def inga_walk(actor, point):
    global do_sit
    global sneelock_distracted
    if point == "inga_attempt_silver_class":
        if not sneelock_distracted:
            sneelock = myscene.actors['sneelock']
            sneelock.prepare_walkpath_move("sneelock_block")
            sneelock.next_action()
            myscene.convo.begin_conversation("you_shall_not_pass")
    if point == "transition_left":
        myscene.handler.notify("act1_scene2")
    if re.match(r"seat_\d+", point) and do_sit:
        myscene.actors['main'].update_state("sit")
        do_sit = False

def inga_sit(seat):
    global do_sit
    inga = myscene.actors['main']
    inga.prepare_walkpath_move(seat.identifier)
    inga.next_action()
    do_sit = True

#TODO: Find a more pythonic way to do some of this...
def levity_walk(actor, point):
    print "Walk handler called..."
    global levity_exposition            #gross how can we un-global this? (i.e. static local var in C)
    global levity_direction
    levity = myscene.actors['levity']
    next_point = point
    if point == "levity_left" or point == "levity_right":   
        if point == "levity_left":
            levity_direction = "right"
            next_point = "levity_1"
        elif point == "levity_right":
            levity_direction = "left"
            next_point = "levity_4"
        #levity.prepare_walkpath_move(next_point)
        pyglet.clock.schedule_once(util.make_dt_wrapper(levity.prepare_walkpath_move), 1, next_point)
        pyglet.clock.schedule_once(levity.next_action, 60)
        
    else:
        if point == "levity_1":
            next_point = "levity_2" if levity_direction == "right" else "levity_left"
        elif point == "levity_2":
            next_point = "levity_3" if levity_direction == "right" else "levity_1"
        elif point == "levity_3":
            next_point = "levity_4" if levity_direction == "right" else "levity_2"
        elif point == "levity_4":
            if levity_exposition is False:
                levity_exposition = True
                #begin convo
                actor.update_state("stand_right")
                myscene.begin_conversation("introduction")
            else:
                next_point = "levity_right" if levity_direction == "right" else "levity_3"
        
        if next_point is not point:    
            levity.prepare_walkpath_move(next_point)
    print "Moving from %s to %s..." % (point, next_point)

def tourist_walk(actor, point):
    global sneelock_distracted
    if point == "tourist_complain":
        sneelock_distracted = True
        myscene.begin_background_conversation("its_too_hot")
        
def sneelock_walk(actor, point):
    if point == "sneelock_inspect":
        pyglet.clock.schedule_once(util.make_dt_wrapper(myscene.begin_background_conversation), 5, "sneelock_checks_it_out")
    
def potato_roll(actor, point):
    point_match = re.search(r"potato_(\d+)", point)
    if point_match:
        current_index = int(point_match.group(1))
        next_index = current_index + 1
        if next_index > 40:
            next_index = 1
        next_point = "potato_%d" % next_index
        print "Potato rolling from %s to %s" % (point, next_point)
        #actor.prepare_walkpath_move(next_point)
        pyglet.clock.schedule_once(util.make_dt_wrapper(actor.prepare_walkpath_move), 0, next_point)
        #actor.next_action()
        pyglet.clock.schedule_once(util.make_dt_wrapper(actor.next_action), 0)

def end_conversation(convo_name):
    if convo_name == "introduction":
        myscene.interaction_enabled = True
        myscene.actors['levity'].prepare_walkpath_move("levity_right")
        myscene.actors['levity'].next_action()
        myscene.handler.handler.save()

    if convo_name == "you_shall_not_pass":
        myscene.actors['sneelock'].prepare_walkpath_move("sneelock_guard")
        myscene.actors['sneelock'].next_action()

        myscene.actors['main'].prepare_walkpath_move("point_6")
        myscene.actors['main'].next_action()
        
        myscene.handler.handler.save()
    
    if convo_name == "its_too_hot":
        myscene.actors['sneelock'].prepare_walkpath_move("sneelock_inspect")
        myscene.actors['sneelock'].next_action()
        myscene.handler.handler.save()
        
    if convo_name == "hamster_from_a_baby":
        potato = myscene.new_actor('potato', 'potato')
        potato.walk_speed = 200.0
        potato.walkpath_point = "potato_1"
        potato.prepare_walkpath_move("potato_2")
        potato.next_action()
    
    if convo_name == "thermostat_discover":
        print myscene.handler.handler.game_variables['temperature']
        if myscene.handler.handler.game_variables['temperature'] >= 80:
            # Nicole complains!
            tourist = myscene.actors['tourist']
            pyglet.clock.schedule_once(util.make_dt_wrapper(tourist.prepare_walkpath_move), 5, "tourist_complain")
            pyglet.clock.schedule_once(tourist.next_action, 5)
        
def talk_to_briggs():
    myscene.end_background_conversation('mumblestiltskin')
    myscene.begin_conversation("briggs_exposition")

walk_handlers = {
    'main': inga_walk,
    'levity': levity_walk,
    'tourist': tourist_walk,
    'sneelock': sneelock_walk,
    'potato': potato_roll
}

def handle_event(event, *args):
    if event == WALK_PATH_COMPLETED:
        info = args[0]
        actor = info['actor']
        point = info['point']
        if walk_handlers.has_key(actor.identifier):
            walk_handlers[actor.identifier](actor, point)
    print "Handled", event, "with", args

def actor_clicked(clicked_actor):
    print clicked_actor
    
    click_handlers = {
        "gregg_briggs": talk_to_briggs,
        "shamus": functools.partial(myscene.begin_conversation, "a_young_irish_boy"),
        "thermostat": functools.partial(myscene.ui.show_cam, clicked_actor, {'Inspect': functools.partial(myscene.begin_conversation, "thermostat_discover")})
    }
    
    if re.match(r"seat_\d+", clicked_actor.identifier) and clicked_actor.current_state == "couch":
        if clicked_actor.identifier in myscene.info['walkpath']['points']:
            myscene.ui.show_cam(clicked_actor, {'Sit': lambda: inga_sit(clicked_actor) })
    
    if click_handlers.has_key(clicked_actor.identifier):
        click_handlers[clicked_actor.identifier]()
    
    if clicked_actor.identifier == "tourist" or clicked_actor.identifier == "tourist_1":
        if myscene.actors['tourist'].walkpath_point == "tourist_start":
            myscene.begin_conversation("meet_the_tourists")
    
    if clicked_actor.identifier == "hipster_amanda" or clicked_actor.identifier == "hipster_liam" or clicked_actor.identifier == "hipster_fran":
        if not sneelock_distracted:
            myscene.begin_conversation("grunt")
        
        
def give_actor(actor, item):
    print "Attemping to give %s %s" % (actor.identifier, item.identifier)
    if actor.identifier == "shamus" and item.identifier == "beans":
        myscene.begin_conversation("hamster_from_a_baby")
        return True
    else:
        return False
        
        
def filter_move(point):
    if point == "transition_left" and not sneelock_distracted:
        return "inga_attempt_silver_class"
    else:
        return point
