from engine import actor

myscene = None

def init():
    print "Initializing script for", myscene
    print "Not changing anything, accepting defaults"

def handle_event(event, *args):
    print "Handled", event, "with", args

def actor_clicked(clicked_actor):
    clicked_actor.prepare_jump()
    clicked_actor.next_action()