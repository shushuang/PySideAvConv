import os
from config import GlobalConfig

class FF_CMD:
    def __init__(self, task):
        self.task = task

    def getCmd(self):
        outputfile = os.path.join(self.task.outputDir,
                                  self.task.outputFile + "." +
                                  self.task.preset.ext)
        cmdstr= "{} -i {} {} {} {} -strict experimental -preset medium -tune film -crf 0 -threads 4 {} ".format(
                                                     GlobalConfig.instance().binPath,
                                                     self.task.name,
                                                     self.getVCodec(),
                                                     self.getACodec(),
                                                     self.getResulution(),
                                                     outputfile)
        return cmdstr

    def getVCodec(self):
        return "-vcodec {}".format(self.task.preset.video_codecs)


    def getACodec(self):
        return "-acodec {}".format(self.task.preset.audio_codecs)

    def getResulution(self):
        if self.task.preset.video_width and self.task.preset.video_height:
            return "-s {}X{}".format(self.task.preset.video_width,
                                     self.task.preset.video_height)
        return ""

