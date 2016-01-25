import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = "config.json"
CONFIG_PATH = os.path.join(ROOT_DIR, CONFIG_FILE)
import json

class GlobalConfig:
    obj = None
    @classmethod
    def instance(cls):
        if not GlobalConfig.obj:
            GlobalConfig.obj = GlobalConfig()
        return GlobalConfig.obj

    def __init__(self):
        with open(CONFIG_PATH, "r") as f:
            data = f.read()
            obj = json.loads(data)
            self.outputDir = obj["outputDir"]
            self.binPath = obj["binPath"]

    def save(self):
        dict_ = {}
        dict_["outputDir"] = self.outputDir
        dict_["binPath"] = self.binPath
        with open(CONFIG_PATH, "w") as f:
            json_str = json.dumps(dict_)
            print(json_str)
            f.write(json_str)
