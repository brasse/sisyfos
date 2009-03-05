from pyglet.gl import *

class EnterHighScoreScreen(object):
    def __init__(self, width, height, score, window, end_screen_callback):
        self.width = width
        self.window = window
        self.end_screen_callback = end_screen_callback

        self.congrats_label = \
            pyglet.text.Label('Congratulations! You made the high score list!',
                              font_name=None,
                              font_size=20,
                              x=width//2, y=400,
                              anchor_x='center', anchor_y='center')

        self.instructions_label = \
            pyglet.text.Label('Enter your name below.',
                              font_name=None,
                              font_size=20,
                              x=width//2, y=365,
                              anchor_x='center', anchor_y='center')

        self.batch = pyglet.graphics.Batch()

        self.document = pyglet.text.document.UnformattedDocument('')
        self.document.set_style(0, len(self.document.text), 
                                dict(color=(255, 0, 0, 255),
                                     font_name=None,
                                     font_size=20))
        font = self.document.get_font()
        font_height = font.ascent - font.descent

        self.layout = \
            pyglet.text.layout.IncrementalTextLayout(self.document,
                                                     width, font_height,
                                                     multiline=False,
                                                     batch=self.batch)
        self.layout.x = width//2
        self.layout.y = 300

        self.caret = pyglet.text.caret.Caret(self.layout)
        window.push_handlers(self.caret)

        self.on_resize(width, height)

    def on_draw(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.layout.x = self.width//2 - self.layout.content_width//2
        self.batch.draw()
        self.congrats_label.draw()
        self.instructions_label.draw()

    def on_resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            self.window.pop_handlers()
            self.end_screen_callback(self.document.text)
    
    def on_key_release(self, symbol, modifiers):
        pass
