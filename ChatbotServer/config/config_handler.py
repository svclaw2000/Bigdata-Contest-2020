import json
from collections import OrderedDict

class ConfigParser(OrderedDict):
    def __init__(self):
        super().__init__()

    def loads(self, raw_text):
        conf = json.loads(raw_text)
        for x in conf:
            self[x] = conf[x]

    def load_from_file(self, filepath):
        raw_lines = ''
        with open(filepath, 'r', encoding='utf-8') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if line and line[0] == '#':
                    continue
                raw_lines += line
        self.loads(raw_lines)