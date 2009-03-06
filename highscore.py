from __future__ import with_statement

import cPickle as pickle
import os

HIGH_SCORE_FILE = 'scores'

class HighScoreList(object):
    def __init__(self, max_size):
        self.max_size = max_size
        self.list = []

    def __len__(self):
        return len(self.list)
    
    def __iter__(self):
        return iter(self.list)

    def __str__(self):
        return str(self.list)

    def __getitem__(self, i):
        return self.list[i]

    def full(self):
        return len(self.list) == self.max_size

    def insert_score(self, name, score):
        self.list.append((name, score))
        self.list.sort(reverse=True, key=lambda x: x[1])
        self.list = self.list[:self.max_size]

def load(settings_path):
    file_path = os.path.join(settings_path, HIGH_SCORE_FILE)
    if os.path.exists(file_path):
        with open(file_path) as f:
            return pickle.load(f)
    else:
        return None

def save(settings_path, list):
    file_path = os.path.join(settings_path, HIGH_SCORE_FILE)
    with open(file_path, 'w') as f:
        pickle.dump(list, f)
