from preset import Preset

def getCmd(task):
    return "avconv -i {} {}".format(task.inputFile, task.outputFile)
