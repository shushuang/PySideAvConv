import subprocess
import shlex
import re
import signal
import os
from PySide.QtCore import *
from PySide.QtGui import *
from config import GlobalConfig
import time
from ffcmd import FF_CMD

NAME = 0
PROGRESS_RATE = 1


class ConvTask(QObject):
    RUN = 1
    PAUSE = 2
    STOP = 3
    COMPLETE = 4
    def __init__(self, name):
        super(ConvTask, self).__init__()
        self.name = name
        self.outputFile = os.path.split(os.path.splitext(name)[0])[-1]+"_Converted"
        print(self.outputFile)
        self.outputDir = GlobalConfig.instance().outputDir
        self.progressRate = 0
        self.proc = None
        self.duration = self.getDuration()
        self.status = ConvTask.STOP
        self.error = False
        self.logfile = "tmp{}.txt".format(time.time())
        self.preset = None

    def outputPath(self):
        return os.path.join(self.outputDir, self.outputFile + "." + self.preset.ext)

    def setPreset(self, preset):
        self.preset = preset


    def postComplete(self):
        os.remove(self.logfile)

    def getDuration(self):
        cmdstr = "{} -i {}".format(GlobalConfig.instance().binPath,self.name)
        print("getDuration cmd:{}".format(cmdstr))
        proc = subprocess.Popen(cmdstr, shell=True,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE
                                  )
        output = proc.communicate(0)[1]
        print(output)
        duration_pat = "(Duration:\s*(?P<hour>[\d]+):(?P<minute>[\d]+):(?P<second>[\d]+)\.(\d)+,)"
        m = re.search(duration_pat, str(output))
        seconds = int(m.group("hour")) * 3600 + int(m.group("minute"))*60 + int(m.group("second"))
        print("duration{0:d}".format(seconds))
        return seconds

    def continueTask(self):
        if self.status == ConvTask.PAUSE:
            self.proc.send_signal(signal.SIGCONT)
            self.status = ConvTask.RUN

    def startTask(self):
        cmdstr = FF_CMD(self).getCmd()
        print(cmdstr)
        self.status = ConvTask.RUN
        with open(self.logfile, 'wb') as f:
            self.proc = subprocess.Popen(shlex.split(cmdstr), stdout=f,
                                         stderr=subprocess.STDOUT, shell=False)

    def pauseTask(self):
        print("click pause")
        self.proc.send_signal(signal.SIGSTOP)
        self.status = ConvTask.PAUSE

    def stopTask(self):
        print("click stop")
        if self.status == ConvTask.RUN:
            self.proc.kill()
            self.status = ConvTask.STOP
            self.postComplete()

    def updateProgress(self):
        if self.status == ConvTask.STOP:
            self.progressRate = 0
            return
        if self.status == ConvTask.COMPLETE:
            return
        with open(self.logfile, "r") as f:
            lastline = f.readlines()[-1]
            print(lastline)
            time_pat = "time=(?P<second>\d+).(\d+)"
            m = re.search(time_pat, lastline)
            if(not m):
                return_status = self.proc.poll()
                # 任务完整结束
                if return_status == 0:
                    self.progressRate = 100
                    self.status = ConvTask.COMPLETE
                    self.postComplete()
               # self.progressRate = 100
               # self.status = ConvTask.COMPLETE
               ## self.status = ConvTask.STOP
            else:
                current_time = int(m.group("second"))
                print("second:{0:d}".format(current_time))
                self.progressRate = int(100.0*current_time/self.duration)


class ConvTaskModel(QAbstractTableModel):
    def __init__(self):
        super(ConvTaskModel,self).__init__()
        self.tasks = []

    def rowCount(self, index=QModelIndex()):
        return len(self.tasks)

    def columnCount(self, index=QModelIndex()):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        task = self.tasks[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == NAME:
                return task.name
            elif column == PROGRESS_RATE:
                return task.progressRate
        elif role == Qt.TextAlignmentRole:
            # if column == NAME:
            #     return int(Qt.AlignRight|Qt.AlignVCenter)
            return int(Qt.AlignLeft|Qt.AlignVCenter)
        # elif role == Qt.SizeHint:
        #     if column == NAME:
        #         return QSize(400, 30)
        return  ""

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QAbstractItemModel.headerData(self, section, orientation, role)
        if orientation == Qt.Horizontal and role==Qt.DisplayRole:
            if section == NAME:
                return "任务名称"
            elif section == PROGRESS_RATE:
                return "转码进度"
        return int(section + 1)

    def addTask(self, task):
        self.tasks.append(task)

class ConvTaskDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(ConvTaskDelegate, self).__init__()
        self.parent = parent

    def paint(self, painter, option, index):
        if index.column() == PROGRESS_RATE:
            # thisCellsWidget = self.parent.taskTableView.indexWidget(index)
            # if thisCellsWidget == None:
            #     thisCellsWidget = QProgressBar()
            #     self.parent.taskTableView.setIndexWidget(index, thisCellsWidget)
            progressbarOption = QStyleOptionProgressBar()
            progressbarOption.rect = option.rect
            progress = self.parent.convTaskModel.tasks[index.row()].progressRate
            progressbarOption.minimum = 0
            progressbarOption.maximum = 100
            progressbarOption.textAlignment = Qt.AlignHCenter
            progressbarOption.progress = progress
            progressbarOption.text = "{0}%".format(progress)
            progressbarOption.textVisible = True
            QApplication.style().drawControl(QStyle.CE_ProgressBar, progressbarOption, painter)
        else:
            QItemDelegate.paint(self, painter, option, index);


class ConvTaskTableView(QTableView):
    clickOnRow = Signal(int)
    deleteTaskSig = Signal()
    def __init__(self, parent=None):
        super(ConvTaskTableView, self).__init__()
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().show()
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.clicked.connect(self.onclick)


    @Slot()
    def onclick(self, index):
        self.clickOnRow.emit(index.row())

    @Slot()
    def continueConvert(self, index):
        def func():
            self.model().tasks[index.row()].continueTask()
        return func

    @Slot()
    def pauseConvert(self, index):
        def func():
            self.model().tasks[index.row()].pauseTask()
        return func

    @Slot()
    def stopConvert(self, index):
        def func():
            self.model().tasks[index.row()].stopTask()
        return func

    @Slot()
    def deleteTask(self, index):
        def func():
            self.model().tasks[index.row()].stopTask()
            del self.model().tasks[index.row()]
            self.model().layoutChanged.emit()
            self.deleteTaskSig.emit()
        return func

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        menu = QMenu()
        convertAction = QAction(self)
        convertAction.setText("继续")
        convertAction.setIcon(QIcon('./images/convert.png'))
        convertAction.triggered.connect(self.continueConvert(index))
        pauseAction = QAction(self)
        pauseAction.setText("暂停")
        pauseAction.triggered.connect(self.pauseConvert(index))
        stopAction = QAction(self)
        stopAction.setText("停止")
        stopAction.triggered.connect(self.stopConvert(index))

        deleteAction = QAction(self)
        deleteAction.setText("删除任务")
        deleteAction.triggered.connect(self.deleteTask(index))
        menu.addActions([convertAction,pauseAction, deleteAction])
        ## 只有选定行弹出菜单
        if index.row() >= 0:
            menu.exec_(event.globalPos())
            event.accept()
        else:
            event.ignore()