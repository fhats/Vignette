"""
File:           cam.py
Author:         Fred Hatfull
Description:    A class encompassing the primary functionality of the Contextual Action Menu (CAM) in SPACE TRAIN.
Notes: 

Contextual Action Menu Life Cycle:
* A CAM instance is requested by a caller (scene, object, level script, something)
    * The caller must provide:
        + A reference to the UI object in use (will probably be a singleton/global)
        + A dictionary of available actions: {'action_name': [function or closure]}
        + A coordinate indicating the centre of menu area around which actions will appear
* A CAM is instantiated and attached to the UI object
    * When a CAM is instantiated it will not have to load any resources like sprites - these should be allocated as static resources somehow and associated with the CAM when it is created
* The CAM is set to visible to indicate that it should drawn by the UI each frame at the specified coordinates
* The CAM remains visible until it detects a click:
    * If the click is within a region controlled by the CAM (i.e. on an action button), the CAM calls the callback associated with the action
    * If the click is elsewhere, pass the event down the event stack and set the CAM to false.
        * Destroy the CAM instance?
"""

import copy, math
import json, pyglet
import gamestate, ui, util
from pyglet.window import key
class CAM(object):
    
    # Init
    def __init__(self, actions, x, y):
        self.visible = False
        self.actions = actions
        self.x = x
        self.y = y

        self.batch = pyglet.graphics.Batch()
        self.buttons = []
        
        # Static resources, such as sprites for the CAM backgrounds
        sprites = {}
        sprite_batch = pyglet.graphics.Batch()
        sprites[1] = util.load_sprite(['ui', 'cam_1.png'], batch = self.batch)
        sprites[2] = util.load_sprite(['ui', 'cam_2.png'], batch = self.batch)
        sprites[3] = util.load_sprite(['ui', 'cam_3.png'], batch = self.batch)
        sprites[4] = util.load_sprite(['ui', 'cam_4.png'], batch = self.batch)
        sprites[5] = util.load_sprite(['ui', 'cam_5.png'], batch = self.batch)

        positioning = {}
        positioning[1] = (67,160)
        positioning[2] = (45,127)
        positioning[3] = (25,89)
        positioning[4] = (11,50)
        positioning[5] = (0,0)
                
        # Turn each action entry into a menu item
        count = 1

        for action, callback in self.actions.items():      
            button = self.Button(x + positioning[count][0], y +  positioning[count][1], sprites[count], action, callback)
            self.buttons.append(button)
            count += 1
        
        self.set_visible(True)
        
    
    # Make this into a property instead. I can't remember how right now. --Steve
    def set_visible(self, new_visible):
        if new_visible:
            gamestate.main_window.push_handlers(self)
        else:
            gamestate.main_window.pop_handlers()
        self.visible = new_visible
    
    # Handle an event
    def on_mouse_release(self, x, y, button, modifiers):
        if(self.visible):
            self.visible = False
            button = self.button_under(x,y)
            if button is None:
                # pass this even down to other handlers, clean up the CAM
                return pyglet.event.EVENT_UNHANDLED
            else:
                # execute the click action and clean up the CAM
                button.click()
                return pyglet.event.EVENT_HANDLED
    
    def on_key_press(self, symbol, modifiers):
        button = 0
        if symbol == key.LEFT:
            self.buttons[button].set_x(self.buttons[button].x - 1)
        elif symbol == key.RIGHT:
            self.buttons[button].set_x(self.buttons[button].x + 1)
        elif symbol == key.UP:
            self.buttons[button].set_y(self.buttons[button].y + 1)
        elif symbol == key.DOWN:
            self.buttons[button].set_y(self.buttons[button].y - 1)
            
        print "Button %d: (%d, %d)" % (button, self.buttons[button].x, self.buttons[button].y)
    
    # Determines which button is under the given point
    # Note that this function's behaviour is undefined when buttons overlap
    # this is intended but should later be changed to return the topmost button
    def button_under(self, x, y):
        for button in self.buttons:
            if (x > button.x and x < button.x + button.width
                and  y > button.y and y < button.y + button.height):
                return button
        return None
    
    def draw(self, dt=0):
        if(self.visible):
            self.batch.draw()
            
    # TODO: finish button class
    class Button(object):
        def __init__(self, x, y, sprite, action, callback):
            self.sprite = sprite
            self.sprite.x = x
            self.sprite.y = y
            self.label = pyglet.text.Label(action, font_name = 'Times New Roman', font_size = 14, anchor_x = 'center', 
                                           anchor_y = 'center', batch = self.sprite.batch, color = (0, 0, 0, 255),
                                           x = self.sprite.x + 5, y = (self.sprite.y + self.sprite.height) - (self.sprite.height / 2) - 5)
            # right-align
            self.label.x = self.sprite.x + ((self.sprite.width - 10) / 2)
            
            self.x = x
            self.y = y
            self.width = self.sprite.width
            self.height = self.sprite.height
            self.callback = callback
            
        def click(self):
            if(self.callback is not None):
				self.callback()
    
        def set_x(self, x):
            self.sprite.x = x
            self.label.x = self.sprite.x + ((self.sprite.width - 10) / 2)
            self.x = x
            
        def set_y(self, y):
            self.sprite.y = y
            self.label.y = (self.sprite.y + self.sprite.height) - (self.sprite.height / 2) - 5
            self.y = y