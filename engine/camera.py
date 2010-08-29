import pyglet

import gamestate

class CameraPoint(object):
    def __init__(self, identifier, position):
        self.identifier = identifier
        self.position = position
    

class Camera(object):
    def __init__(self, min_bounds=None, max_bounds=None, speed=100.0, points_dict=None):
        self.min_bounds = min_bounds or gamestate.camera_min
        self.max_bounds = max_bounds or gamestate.camera_max
        self.speed = speed
        self.position = self.min_bounds
        self.target = self.position
        points_dict = points_dict or {}
        self.points = {identifier: CameraPoint(identifier, (d['x'], d['y'])) \
                       for identifier, d in points_dict.viewitems()}
    
    def points_dict(self):
        return {identifier: {'x': p.x, 'y': p.y} for identifier, p in self.points.viewitems()}
    
    def set_target(self, x, y):
        x = min(max(x, self.min_bounds[0]), self.max_bounds[0])
        y = min(max(y, self.min_bounds[1]), self.max_bounds[1])
        self.target = (x, y)
    
    def set_position(self, x, y):
        x = min(max(x, self.min_bounds[0]), self.max_bounds[0])
        y = min(max(y, self.min_bounds[1]), self.max_bounds[1])
        self.position = (x, y)
        self.target = self.position
    
    def camera_point_near_point(self, mouse):
        close = lambda a, b: abs(a-b) <= 5
        for point in self.points.viewvalues():
            if close(point.position[0], mouse[0]) and close(point.position[1], mouse[1]):
                return point
        return None
    
    def add_point(self, identifier, x, y):
        x = min(max(x, self.min_bounds[0]), self.max_bounds[0])
        y = min(max(y, self.min_bounds[1]), self.max_bounds[1])
        self.points[identifier] = CameraPoint(identifier, (x, y))
        return self.points[identifier]
    
    def remove_point(self, identifier):
        try:
            del self.points[identifier]
        except KeyError:
            return
    
    def update(self, dt):
        move_amt = self.speed*dt
        x, y = self.position
        tx, ty = self.target
        if x < x - move_amt: x += move_amt
        if x > tx + move_amt: x -= move_amt
        if abs(x - tx) <= move_amt: x = tx
        if y < ty - move_amt: y += move_amt
        if y > ty + move_amt: y -= move_amt
        if abs(y - ty) <= move_amt: y = ty
        x = min(max(x, self.min_bounds[0]), self.max_bounds[0])
        y = min(max(y, self.min_bounds[1]), self.max_bounds[1])
        self.position = (x, y)
    
    def apply(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(-self.position[0]+gamestate.norm_w//2, -self.position[1]+gamestate.norm_h//2,0)
    
    def unapply(self):
        pyglet.gl.glPopMatrix()
    
    def mouse_to_canvas(self, x, y):
        return (x/gamestate.scale_factor + self.position[0]-gamestate.norm_w//2, 
                y/gamestate.scale_factor + self.position[1]-gamestate.norm_h//2)
    

