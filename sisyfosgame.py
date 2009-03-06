import math
import random

from Box2D import *
from pyglet.gl import *

class ContactListener(b2ContactListener):
    def __init__(self, point_callback, game_over_callback):
        super(ContactListener, self).__init__()
        self.point_callback = point_callback
        self.game_over_callback = game_over_callback

    def Add(self, point):
        n1 = point.shape1.GetBody().GetUserData().get('name', 'noname')
        n2 = point.shape2.GetBody().GetUserData().get('name', 'noname')
        pair = set([n1, n2])
        if set(['paddle', 'ball']) == pair:
            self.point_callback()
        elif set(['wall', 'ball']) == pair:
            self.game_over_callback()

    def Persist(self, point):
        pass
    
    def Remove(self, point):
        pass
    
    def Result(self, point):
        pass
    
class Sisyfos(object):
    FPS = 60
    HALF_SIDE = 20.0
    MOTOR_SPEED = 2.0
    MAX_MOTOR_TORQUE = 5000
    INITIAL_BALL_SPEED = 9

    BALL_COLOR = (1.0, 0.0, 0.0)
    BALL_RADIUS = 0.5
    
    PADDLE_COLOR = (0.0, 0.0, 1.0)
    PADDLE_CIRCLE_RADIUS = 19
    PADDLE_WIDTH = 5
    PADDLE_THICKNESS = 0.5
    
    def __init__(self, width, height, end_screen_callback):
        self.width = width
        self.height = height
        self.end_screen_callback = end_screen_callback
        self.time_step = 1.0 / self.FPS
        self.time = 0.0
        self.points = 0
        self.paddle_direction = 0
        self.game_over_flag = False

        self.init_world()
        self.init_paddle(self.PADDLE_CIRCLE_RADIUS,
                         self.PADDLE_WIDTH, self.PADDLE_THICKNESS)
        self.init_ball(self.BALL_RADIUS)
        self.init_walls()
        self.init_score_label()
        
        self.on_resize(width, height)
        
        pyglet.clock.schedule_interval(self.step, self.time_step)

    def close(self):
        pass
    
    def init_score_label(self):
        self.label = pyglet.text.Label('%d' % self.points,
                                       font_name=None,
                                       font_size=36, x=10, y=10)

    def draw_score_label(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, 0, self.height, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        self.label.draw()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
    def init_world(self):
        worldAABB = b2AABB()
        worldAABB.lowerBound.Set(-100, -100)
        worldAABB.upperBound.Set(100, 100)
        gravity = b2Vec2(0, 0)
        doSleep = True
        self.world = b2World(worldAABB, gravity, doSleep)
        self.contact_listener = ContactListener(self.point_scored,
                                                self.game_over)
        self.world.SetContactListener(self.contact_listener)
        self.world.GetGroundBody().SetUserData(['nonsense'])
        
    def init_walls(self):
        walls = [((self.HALF_SIDE, 0), (0.2, self.HALF_SIDE)),
                 ((-self.HALF_SIDE, 0), (0.2, self.HALF_SIDE)),
                 ((0, self.HALF_SIDE), (self.HALF_SIDE, 0.2)),
                 ((0, -self.HALF_SIDE), (self.HALF_SIDE, 0.2))]
        for pos, box in walls:
            bodyDef = b2BodyDef()
            bodyDef.position.Set(*pos)
            wall = self.world.CreateBody(bodyDef)
            shapeDef = b2PolygonDef()
            shapeDef.SetAsBox(*box)
            wall.CreateShape(shapeDef)
            wall.SetUserData({'name' : 'wall'})

    def init_paddle(self, radius, width, thickness, angle=0):
        anchorDef = b2BodyDef()
        anchorDef.position.Set(0,0)
        anchor = self.world.CreateBody(anchorDef)
        anchor.SetUserData({})
        
        bodyDef = b2BodyDef()
        bodyDef.position.Set(0, 0)
        bodyDef.angle = angle
        paddle = self.world.CreateBody(bodyDef)
        shapeDef = b2PolygonDef()
        points = [(radius - thickness / 2, width / 2),
                  (radius - thickness / 2, -width / 2),
                  (radius + thickness / 2, -width / 2),
                  (radius + thickness / 2, width / 2)]
        shapeDef.setVertices_tuple(points)
        shapeDef.density = 1
        paddle.CreateShape(shapeDef)
        paddle.SetMassFromShapes()

        jointDef = b2RevoluteJointDef()
        jointDef.Initialize(anchor, paddle, anchor.GetWorldCenter())
        jointDef.enableMotor = True
        jointDef.maxMotorTorque = self.MAX_MOTOR_TORQUE
        self.joint = self.world.CreateJoint(jointDef).getAsType()

        paddle.SetUserData({'name' : 'paddle',
                            'color' : self.PADDLE_COLOR})

        self.paddle = paddle

    def init_ball(self, radius=0.5):
        bodyDef = b2BodyDef()
        bodyDef.position.Set(0, 0)
        ball = self.world.CreateBody(bodyDef)
        shapeDef = b2CircleDef()
        shapeDef.radius = radius
        shapeDef.density = 1
        shapeDef.restitution = 1
        ball.CreateShape(shapeDef)
        ball.SetMassFromShapes()
        self.ball = ball

        # Set random speed.
        f = random.uniform(0, 2 * math.pi)
        x = math.cos(f) * self.INITIAL_BALL_SPEED
        y = math.sin(f) * self.INITIAL_BALL_SPEED
        ball.SetLinearVelocity(b2Vec2(x,y))

        ball.SetUserData({'color' : self.BALL_COLOR,
                          'name' : 'ball'})

    def step(self, dt):
        self.time += dt
        while self.time > self.time_step:
            self.time -= self.time_step
            vel_iters, pos_iters = 10, 8
            self.joint.SetMotorSpeed(self.paddle_direction * self.MOTOR_SPEED)
            self.world.Step(self.time_step, vel_iters, pos_iters)
        if self.game_over_flag:
            self.end_screen_callback(self.points)
                
    def point_scored(self):
        self.points += 1
        self.label.text = '%d' % self.points

    def game_over(self):
        self.game_over_flag = True
        pyglet.clock.unschedule(self.step)
        
    def draw_polygon(self, shape):
        polygon = shape.asPolygon()
        glBegin(GL_TRIANGLE_FAN)
        vertices = polygon.getVertices_tuple()
        for x, y in vertices:
            glVertex2f(x, y)
        glEnd()

    def draw_circle(self, shape):
        circle = shape.asCircle()
        glBegin(GL_TRIANGLE_FAN)
        steps = 20
        radius = circle.GetRadius()
        for i in xrange(steps + 1):
            f = i / float(steps) * 2 * math.pi
            glVertex2f(math.cos(f) * radius, math.sin(f) * radius)
        glEnd()

    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw world objects.
        for body in self.world:
            body_data = body.GetUserData()
            for shape in body:
                if body_data['name'] == 'wall':
                    break
                x, y = body.GetPosition().tuple()
                angle = body.GetAngle()
                glPushMatrix()
                glTranslatef(x, y, 0.0)
                glRotatef(math.degrees(angle), 0.0, 0.0, 1.0)
                glColor3f(*body_data['color'])
                type = shape.GetType()
                if type == e_polygonShape:
                    self.draw_polygon(shape)
                elif type == e_circleShape:
                    self.draw_circle(shape)
                glPopMatrix()

        self.draw_score_label()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.HALF_SIDE, self.HALF_SIDE,
                -self.HALF_SIDE, self.HALF_SIDE,
                -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.LEFT:
            self.paddle_direction = 1
        elif symbol == pyglet.window.key.RIGHT:
            self.paddle_direction = -1
        elif symbol == pyglet.window.key.ESCAPE:
            pyglet.clock.unschedule(self.step)
            self.end_screen_callback(None)

    def on_key_release(self, symbol, modifiers):
        if symbol in [pyglet.window.key.LEFT, pyglet.window.key.RIGHT]:
            self.paddle_direction = 0
