"""
File:           scenehandler.py
Description:    Handles scene loading, saving, and transitions.
Notes: A scenehandler object has a save() method which will save all data for the scene in the autosave folder. Whenever a plot element is completed (task completed, item acquired, etc.) the save() method should be called.

When a new scene is needed or the game is closed, the notify() method should be used. If a new scene is specified then scenehandler initiates a scene transition. If no new scene is specified, it is assumed that the user is attempting to exit the game, and the gamehandler will be notified to allow the user to save their game before closing.
"""

import json

import pyglet

import gamestate, actionsequencer, util, interpolator, scene

class SceneHandler(actionsequencer.ActionSequencer):
    def __init__(self, game_handler):
        super(SceneHandler, self).__init__()
        self.scene = None
        self.handler = game_handler
        
        self.controller = interpolator.InterpolatorController()
        self.fade_time = 1.0
        self.batch = pyglet.graphics.Batch()
        
        # Build transition sprite(s)
        scene_transition_img = pyglet.resource.image(util.respath('environments', 'transitions', 'test.png'))
        self.sprite = pyglet.sprite.Sprite(scene_transition_img, x = 0, y = 0, batch=self.batch)
        self.sprite.opacity = 0
    
    def set_first_scene(self, scn):
        self.scene = scn
        self.scene.load_script()
        gamestate.event_manager.set_scene(self.scene)
    
    def __repr__(self):
        return "SceneHandler(scene_object=%s)" % str(self.scene)

    # Called by a scene to load a new scene.
    # If dir is specified a sliding transition is used
    def notify(self, next_scene, dir=0):
        if self.handler.ui.cam is not None:
            self.handler.ui.cam.set_visible(False)
        
        if next_scene is None:
            self.handler.prompt_save_and_quit()
        else:
            if(dir == 0):
                self.fade_to(next_scene)
            else:
                self.slide_to(next_scene, dir)
            
    # For direction 1 is up, 2 is right, 3 is down, 4 is left
    def slide_to(self, next_scene, dir=2):
        InterpClass = interpolator.LinearInterpolator
        gamestate.event_manager.set_scene(None)
        slide_scene = scene.Scene(next_scene, self, self.handler.ui)
        slide_scene.pause()
        # Determine offset
        if(dir == 1):
            slide_scene.y_offset = gamestate.norm_h
        elif(dir == 2):
            slide_scene.x_offset = gamestate.norm_w
        elif(dir == 3):
            slide_scene.y_offset = -gamestate.norm_h
        elif(dir == 4):
            slide_scene.x_offset = -gamestate.norm_w
        
        def slide(ending_action=None):
            self.scene.pause()
            if(dir == 1 or dir == 3):
                interp1 = InterpClass(self.scene, 'y_offset', end=-slide_scene.y_offset, duration=2*self.fade_time)
                interp2 = InterpClass(slide_scene, 'y_offset', end=0, duration=2*self.fade_time, done_function=self.next_action())
            else:
                interp1 = InterpClass(self.scene, 'x_offset', end=-slide_scene.x_offset, duration=2*self.fade_time)
                interp2 = InterpClass(slide_scene, 'x_offset', end=0, duration=2*self.fade_time, done_function=self.next_action())
                
            self.controller.add_interpolator(interp1)
            self.controller.add_interpolator(interp2)
            
        def switch_scenes(ending_action=None):
            self.handler.save()
            self.scene.exit()
            slide_scene.transition_from(self.scene.name)
            self.scene = slide_scene
            self.scene.resume()
            self.next_action()
            
        def complete_transition(ending_action=None):
            gamestate.event_manager.set_scene(self.scene)
            self.next_action()
            
        self.simple_sequence(slide, switch_scenes, complete_transition)
    
    def fade_to(self, next_scene):
        InterpClass = interpolator.LinearInterpolator
        def fade_out(ending_action=None):
            gamestate.event_manager.set_scene(None)
            interp = InterpClass(self.sprite, 'opacity', end=255, start=0, duration=self.fade_time,
                                done_function=self.next_action)
            self.controller.add_interpolator(interp)
        
        def complete_transition(ending_action=None):
            gamestate.event_manager.set_scene(self.scene)
            self.next_action()
        
        def fade_in(ending_action=None):
            # Remove scene
            self.handler.save()
            self.scene.exit()
            new_scene = scene.Scene(next_scene, self, self.handler.ui)
            new_scene.transition_from(self.scene.name)
            self.scene = new_scene
            interp = InterpClass(self.sprite, 'opacity', end=0, start=255, duration=self.fade_time,
                                done_function=complete_transition)
            self.controller.add_interpolator(interp)
        
        self.simple_sequence(fade_out, fade_in)
    
    def update(self, dt=0):
        self.controller.update_interpolators(dt)
        if self.scene:
            self.scene.update(dt)
    
    def draw(self):
        self.batch.draw()
    
