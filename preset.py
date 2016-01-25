import os
import re
import json
import codecs
PRESETS_FOLDER = "presets"

ROOT_FOLDER = os.path.dirname(os.path.abspath(__file__))

class Preset:
    def __init__(self):
        self.name = None
        self.ext = None
        self.video_codecs = None
        self.audio_codecs = None
        self.video_width = None
        self.video_height = None


class PresetLibrary:
    def __init__(self):
        self.presets = {}
        presetsPath = os.path.join(ROOT_FOLDER, PRESETS_FOLDER)
        absfiles = [os.path.join(presetsPath, f) for f in os.listdir(presetsPath) if re.match(r".*?\.json$", f)]
        for f in absfiles:
            with codecs.open(f,encoding="utf8") as file_:
                print(f)
                data = file_.read()
                presetjson = json.loads(data)
                preset = Preset()
                if presetjson["name"]:
                    preset.name = str(presetjson["name"])
                if presetjson["ext"]:
                    preset.ext = str(presetjson["ext"])
                if presetjson["video_codecs"]:
                    preset.video_codecs = str(presetjson["video_codecs"])
                if presetjson["audio_codecs"]:
                    preset.audio_codecs = str(presetjson["audio_codecs"])
                self.presets[preset.name] = preset


    def getPresets(self):
        return [str(key) for key in self.presets.keys()]

    def loadPreset(self, name):
        return self.presets[name]

if __name__ == '__main__':
    presetLibrary = PresetLibrary()
    for key in presetLibrary.getPresets():
        print(presetLibrary.loadPreset(key).video_codecs)