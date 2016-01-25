import sys
import os
from PySide.QtCore import *
from PySide.QtGui import *
from convert import ConvTask, ConvTaskModel, ConvTaskDelegate, ConvTaskTableView
from preset import PresetLibrary,Preset
from config import GlobalConfig



class SettingDialog(QDialog):
    def __init__(self,parent=None):
        super(SettingDialog, self).__init__(parent)
        mainLayout = QGridLayout()
        ffmpegLabel = QLabel("ffmpeg或avconv工具路径")
        self.ffmpegEdit = QLineEdit("")
        ffmpegEditBtn = QPushButton("...")
        outputDirLabel = QLabel("默认输出文件夹路径")
        self.oDirEdit = QLineEdit("")
        oDirEditBtn = QPushButton("...")
        mainLayout.addWidget(ffmpegLabel, 0, 0)
        mainLayout.addWidget(self.ffmpegEdit, 1, 0)
        mainLayout.addWidget(ffmpegEditBtn, 1, 1)
        mainLayout.addWidget(outputDirLabel, 2, 0)
        mainLayout.addWidget(self.oDirEdit, 3, 0)
        mainLayout.addWidget(oDirEditBtn, 3, 1)
        self.setLayout(mainLayout)
        self.setWindowTitle("设置")
        ffmpegEditBtn.clicked.connect(self.findFFmpeg)
        oDirEditBtn.clicked.connect(self.oDir)
        self.loadFromConfig()

    def loadFromConfig(self):
        self.oDirEdit.setText(GlobalConfig.instance().outputDir)
        self.ffmpegEdit.setText(GlobalConfig.instance().binPath)

    def findFFmpeg(self):
        fname = QFileDialog.getOpenFileName(self, "选择目录",
                                                     QDir.currentPath())
        if fname[0]:
            path = fname[0]
            self.ffmpegEdit.setText(path)
            GlobalConfig.instance().binPath = path
            GlobalConfig.instance().save()


    def oDir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目录",
                                                     QDir.currentPath())
        if directory:
            self.oDirEdit.setText(directory)
            GlobalConfig.instance().outputDir = directory
            GlobalConfig.instance().save()


class GeneralSettingWidget(QWidget):
    def __init__(self, parent=None):
        super(GeneralSettingWidget, self).__init__(parent)
        self.presetLibrary = PresetLibrary()
        mainLayout = QGridLayout()

        presetLabel = QLabel()
        presetLabel.setText("Preset:")
        self.presetComboBox = QComboBox()
        self.presetComboBox.addItems(self.presetLibrary.getPresets())
        self.presetComboBox.currentIndexChanged.connect(self.changePreset)

        fNameLabel = QLabel(self)
        fNameLabel.setText("输出文件名:")

        fnameEditComboWidget = QWidget(self)
        fnameEditlayout = QVBoxLayout()
        fnameEditComboWidget.setLayout(fnameEditlayout)
        self.fnameEdit = QLineEdit(self)
        # self.startConvertBtn = QToolButton(self)
        # self.startConvertBtn.setText("开始转码")
        fnameEditlayout.addWidget(fNameLabel)
        fnameEditlayout.addWidget(self.fnameEdit)
        # fnameEditlayout.addWidget(self.startConvertBtn)

        dirLabel = QLabel(self)
        dirLabel.setText("输出文件夹:")
        dirEditComboWidget = QWidget(self)
        dirEditLayout = QHBoxLayout()
        dirEditComboWidget.setLayout(dirEditLayout)
        self.dirEdit = QLineEdit(self)
        dirEditBtn = QToolButton(self)
        dirEditBtn.setText("...")
        dirEditBtn.clicked.connect(self.openDir)
        dirEditLayout.addWidget(self.dirEdit)
        dirEditLayout.addWidget(dirEditBtn)

        mainLayout.addWidget(presetLabel, 0, 0)
        mainLayout.addWidget(self.presetComboBox, 1, 0)
        mainLayout.addWidget(fNameLabel, 2, 0)
        mainLayout.addWidget(fnameEditComboWidget, 3, 0)
        mainLayout.addWidget(dirLabel, 4, 0)
        mainLayout.addWidget(dirEditComboWidget, 5, 0)
        self.setLayout(mainLayout)
        self.setDisabled(True)
        # self.startConvertBtn.clicked.connect(self.startConvert)


    def changePreset(self, index):
        if not self.task:
            print("task not intialized")
        else:
            preset_name = self.presetComboBox.itemText(index)
            self.task.setPreset(self.presetLibrary.loadPreset(preset_name))

    def setTask(self, task):
        self.setDisabled(False)
        self.task = task
        self.changePreset(self.presetComboBox.currentIndex())
        self.fnameEdit.setText(task.outputFile)
        self.dirEdit.setText(task.outputDir)

    def saveParameters(self):
        oFileFullName = self.fnameEdit.text() + "." + self.task.preset.ext
        # check file if exists
        outputDir = self.dirEdit.text()
        outputPath = os.path.join(outputDir, oFileFullName)
        if os.path.exists(outputPath):
            QMessageBox.critical(self, "Error",
                                    "通用设置：存在同名文件，请重命名")
            return False
        self.task.outputFile = self.fnameEdit.text()
        self.task.outputDir = outputDir
        return True

    def openDir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目录",
                                                     QDir.currentPath())
        if directory:
            self.dirEdit.setText(directory)


class VideoSettingWidget(QWidget):
    def __init__(self, parent=None):
        super(VideoSettingWidget, self).__init__(parent)
        gridLayout = QGridLayout()
        resolutionLabel = QLabel()
        resolutionLabel.setText("视频分辨率")
        gridLayout.addWidget(resolutionLabel, 0, 0)
        resolutionWidget = QWidget()
        resolutionLayout = QHBoxLayout()
        resolutionWidget.setLayout(resolutionLayout)
        self.widthEdit = QLineEdit()
        self.widthEdit.setFixedSize(60,30)
        multiLabel = QLabel("X")
        multiLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        multiLabel.setFixedWidth(30)
        self.heightEdit = QLineEdit()
        self.heightEdit.setFixedSize(60, 30)
        resolutionLayout.addWidget(self.widthEdit)
        resolutionLayout.addWidget(multiLabel)
        resolutionLayout.addWidget(self.heightEdit)
        resolutionLayout.setAlignment(self.heightEdit, Qt.AlignLeft)
        gridLayout.addWidget(resolutionWidget, 0, 1)
        self.setLayout(gridLayout)

    def setTask(self, task):
        self.task = task

    def saveParameters(self):
        width = self.widthEdit.text().strip()
        height = self.heightEdit.text().strip()
        if width == "" and height == "":
            return True
        try:
            int_width = int(width)
            int_height = int(height)
            print(int_width)
            if int_width<0 or int_height < 0:
                raise Exception()
        except:
            QMessageBox.critical(self, "Error", "视频参数设置，输入正确的视频分辨率")
            return False
        self.task.preset.video_width = width
        self.task.preset.video_height = height
        return True


class AudioSettingWidget(QWidget):
    def __init__(self, parent=None):
        super(AudioSettingWidget, self).__init__(parent)


class Window(QMainWindow):
    addNewTask = Signal()
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.resize(640,480)
        self.task = None
        self.settingDialog = None
        # create actions
        newAction = QAction(self)
        newAction.setText("添加文件")
        newAction.setIcon(QIcon('./images/new.png'))
        newAction.triggered.connect(self.addMediaFile)

        # removeAction = QAction(self)
        # removeAction.setText("删除文件")
        # removeAction.setIcon(QIcon('./images/remove.png'))

        convertAction = QAction(self)
        convertAction.setText("开始转码")
        convertAction.setIcon(QIcon('./images/convert.png'))

        settingAction = QAction(self)
        settingAction.setText("设置")

        aboutAction = QAction(self)
        aboutAction.setText("关于")

        # Begin MenuBar
        self.menuBar = QMenuBar(self)
        self.menuBar.setObjectName("menuBar")
        # self.menuBar.setGeometry(QtCore.QRect(0, 0, 400, 20))
        self.menuFile = QMenu(self.menuBar)
        self.menuFile.setTitle("文件")
        self.setMenuBar(self.menuBar)
        # self.actionAdd_Media = QAction(self)
        # self.actionAdd_Media.setText("Add Media")
        self.menuFile.addAction(newAction)
        # self.menuFile.addAction(removeAction)
        self.menuFile.addAction(convertAction)
        self.menuBar.addAction(self.menuFile.menuAction())

        menuEdit = QMenu(self.menuBar)
        menuEdit.setTitle("编辑")
        menuEdit.addAction(settingAction)
        self.menuBar.addAction(menuEdit.menuAction())
        # menuOption = QMenu(self.menuBar)
        # menuOption.setTitle("选项")
        # self.menuBar.addAction(menuOption.menuAction())
        menuHelp = QMenu(self.menuBar)
        menuHelp.setTitle("帮助")
        menuHelp.addAction(aboutAction)
        self.menuBar.addAction(menuHelp.menuAction())
        # End MenuBar

        # Start toolbar
        mainToolBar = QToolBar(self)
        mainToolBar.setObjectName("mainToolBar")
        self.addToolBar(mainToolBar)
        mainToolBar.addAction(newAction)
        # mainToolBar.addAction(removeAction)
        mainToolBar.addAction(convertAction)
        # End toolbar

        # splitter
        self.mainSplitter = QSplitter(Qt.Vertical)
        self.setCentralWidget(self.mainSplitter)
        self.mainSplitter.setStretchFactor(0, 3)
        self.mainSplitter.setStretchFactor(1, 1)

        # timely update progress rate
        # use add file to add task
        self.convTaskModel = ConvTaskModel()
        # for test use
        # convTask = ConvTask("/home/ss/Test1.mp4")
        # self.convTaskModel.addTask(convTask)

        self.taskTableView = ConvTaskTableView()
        self.taskTableView.setModel(self.convTaskModel)
        self.taskTableView.setItemDelegate(ConvTaskDelegate(self))
        self.taskTableView.setColumnWidth(0, 400)

        # self.taskListWidget = QWidget()
        # self.mainSplitter.addWidget(self.taskListWidget)
        self.mainSplitter.addWidget(self.taskTableView)
        self.mainTabWidget = QTabWidget()
        self.mainSplitter.addWidget(self.mainTabWidget)

        # Begin info tabWidget
        self.generalSettingWidget = GeneralSettingWidget(self)
        self.mainTabWidget.addTab(self.generalSettingWidget, "通用设置")
        # End info tabWidget

        # Begin tab2Widget
        self.vSettingWidget = VideoSettingWidget()
        self.mainTabWidget.addTab(self.vSettingWidget, "视频参数设置")
        # End tab2Widget

        # self.aSettingWidget = AudioSettingWidget()
        # self.mainTabWidget.addTab(self.aSettingWidget, "音频参数设置")
        #
        # self.tab_4 = QWidget()
        # self.mainTabWidget.addTab(self.tab_4, "转码命令行")

        self.statusBar = QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.setStatusBar(self.statusBar)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refreshProgress)
        self.timer.start(1500)

        self.taskTableView.clickOnRow.connect(self.clickOnRow)
        self.taskTableView.deleteTaskSig.connect(self.deleteTask)
        convertAction.triggered.connect(self.startConvert)
        aboutAction.triggered.connect(self.about)
        #self.convTaskModel.tasks[0].startTask()
        settingAction.triggered.connect(self.setting)


    @Slot()
    def setting(self):
        if not self.settingDialog:
            self.settingDialog = SettingDialog()
        self.settingDialog.show()
        self.settingDialog.raise_()
        self.settingDialog.activateWindow()



    @Slot()
    def about(self):
        QMessageBox.about(self, self.tr("About"), "本软件基于ffmpeg或libav， 目标是提供一个简易的图形界面视频转码器\n 作者：疏爽")

    @Slot()
    def deleteTask(self):
        self.generalSettingWidget.setDisabled(True)

    @Slot()
    def clickOnRow(self, row):
        task = self.convTaskModel.tasks[row]
        self.task = task
        self.generalSettingWidget.setTask(self.convTaskModel.tasks[row])
        self.vSettingWidget.setTask(task)

    @Slot()
    def startConvert(self):
        if self.generalSettingWidget.saveParameters():
            if self.vSettingWidget.saveParameters():
                self.task.startTask()


    @Slot()
    def addMediaFile(self):
        filename = QFileDialog.getOpenFileName(self, "Find File", QDir.currentPath())
        print(filename[0])
        if filename[0]:
            convTask = ConvTask(filename[0])
            self.convTaskModel.addTask(convTask)
            self.convTaskModel.layoutChanged.emit()

    @Slot()
    def refreshProgress(self):
        for task in self.convTaskModel.tasks:
            if(task.status == ConvTask.RUN):
                task.updateProgress()
        self.taskTableView.reset()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.setWindowTitle("简易视频转码器")
    window.show()
    sys.exit(app.exec_())