from pyglet.gl import *

class StartScreen(object):
    TITLE = 0
    HIGH_SCORE = 1

    def __init__(self, width, height, version_string, high_score_list,
                 display_time_s, end_screen_callback):
        self.width = width
        self.height = height
        self.high_score_list = high_score_list
        self.end_screen_callback = end_screen_callback
        self.sisyfos_label = \
            pyglet.text.Label('Sisyfos',
                              font_name=None,
                              font_size=75,
                              x=width//2, y=375,
                              anchor_x='center', anchor_y='center')
        self.instruction_label = \
            pyglet.text.Label('Press space to play!',
                              font_name=None,
                              font_size=36,
                              x=width//2, y=275,
                              anchor_x='center', anchor_y='center')
        self.version_label = \
            pyglet.text.Label(version_string,
                              font_name=None,
                              font_size=12,
                              x=5, y=5)
        self.mode = self.TITLE

        def switch_mode(dt):
            if self.mode == self.TITLE:
                self.mode = self.HIGH_SCORE
                self.make_high_score_labels()
            else:
                assert(self.mode == self.HIGH_SCORE)
                self.mode = self.TITLE

        pyglet.clock.schedule_interval(switch_mode, display_time_s)
        self.on_resize(self.width, self.height)

    def make_high_score_labels(self):
        self.labels = []
        y_base = self.height - 110
        for i, (name, score) in enumerate(self.high_score_list):
            label = \
                  pyglet.text.Label('%d. %s %d' % (i + 1, name, score),
                                    font_name=None,
                                    font_size=20,
                                    x=self.width//2, y=y_base - i * 40,
                                    anchor_x='center', anchor_y='center')
            self.labels.append(label)
    
    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        if self.mode == self.TITLE:
            self.sisyfos_label.draw()
            self.instruction_label.draw()
            self.version_label.draw()
        else:
            assert(self.mode == self.HIGH_SCORE)
            for label in self.labels:
                label.draw()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.end_screen_callback()

    def on_key_release(self, symbol, modifiers):
        pass
