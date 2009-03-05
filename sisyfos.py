import highscore
from enterhighscore import EnterHighScoreScreen
from sisyfosgame import Sisyfos
from startscreen import StartScreen

import os

import pyglet

def get_settings_path(application):
    dir = pyglet.resource.get_settings_path(application)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir

class SisyfosWindow(pyglet.window.Window):
    SIDE = 600
    VERSION_STRING = '0.1'
    HIGH_SCORE_LIST_SIZE = 10

    def __init__(self):
        pyglet.window.Window.__init__(self,
                                      width=self.SIDE,
                                      height=self.SIDE,
                                      caption='sim')

        self.settings_path = get_settings_path('Sisyfos')
        self.high_score_list = highscore.load(self.settings_path)
        if not self.high_score_list:
            self.high_score_list = \
                highscore.HighScoreList(self.HIGH_SCORE_LIST_SIZE)
            self.high_score_list.insert_score('foo', 1)
        highscore.save(self.settings_path, self.high_score_list)
        self.start_screen = StartScreen(self.width, self.height,
                                        self.VERSION_STRING,
                                        self.high_score_list,
                                        5, self.start_game)
        self.mode = self.start_screen

    def on_resize(self, width, height):
        self.mode.on_resize(width, height)
        
    def on_draw(self):
        self.mode.on_draw()

    def on_key_press(self, symbol, modifiers):
        self.mode.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        self.mode.on_key_release(symbol, modifiers)

    def start_game(self):
        self.mode = Sisyfos(self.width, self.height, self.end_game)

    def end_game(self, points):
        if points:
            if (not self.high_score_list.full() or
                points > self.high_score_list[-1][1]):

                def save_high_score(name):
                    self.high_score_list.insert_score(name, points)
                    highscore.save(self.settings_path, self.high_score_list)
                    self.mode = self.start_screen
                    self.mode.on_resize(self.width, self.height)
                    self.mode.make_high_score_labels()

                self.mode = EnterHighScoreScreen(self.width, self.height,
                                                 points, self, save_high_score)
            else:
                self.mode = self.start_screen
                self.mode.on_resize(self.width, self.height)
        else:
            self.mode = self.start_screen
            self.mode.on_resize(self.width, self.height)

def main():
    window = SisyfosWindow()
    pyglet.app.run()

if __name__ == '__main__':
    main()
