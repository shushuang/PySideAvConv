import sys
import os
from PySide.QtCore import *
from PySide.QtGui import *
from convert import ConvTask, ConvTaskModel, ConvTaskDelegate, ConvTaskTableView
from config import GlobalConfig

class GeneralSettingWidget(QWidget):
    def __init__(self, parent=None):
        super(GeneralSettingWidget, self).__init__(parent)
        mainLayout = QVBoxLayout()
        fNameLabel = QLabel(self)
        fNameLabel.setText("  输出文件名:")

        fnameEditComboWidget = QWidget(self)
        fnameEditlayout = QHBoxLayout()
        fnameEditComboWidget.setLayout(fnameEditlayout)
        self.fnameEdit = QLineEdit(self)
        self.fnameEdit.setText("")
        fnameSaveBtn = QToolButton(self)
        fnameSaveBtn.setText("开始转码")
        fnameSaveBtn.clicked.connect(self.startConvert)
        fnameEditlayout.addWidget(self.fnameEdit)
        fnameEditlayout.addWidget(fnameSaveBtn)


        self.dirLabel = QLabel(self)
        self.dirLabel.setText("  输出文件夹:")
        dirEditComboWidget = QWidget(self)
        dirEditLayout = QHBoxLayout()
        dirEditComboWidget.setLayout(dirEditLayout)
        self.dirEdit = QLineEdit(self)
        self.dirEdit.setText("/home/ss/")
        dirEditBtn = QToolButton(self)
        dirEditBtn.setText("...")
        dirEditBtn.clicked.connect(self.openDir)
        dirEditLayout.addWidget(self.dirEdit)
        dirEditLayout.addWidget(dirEditBtn)

        mainLayout.addWidget(fNameLabel)
        mainLayout.addWidget(fnameEditComboWidget)
        mainLayout.addWidget(self.dirLabel)
        mainLayout.addWidget(dirEditComboWidget)
        self.setLayout(mainLayout)
        self.setDisabled(True)

    def setTask(self, task):
        self.setDisabled(False)
        self.task = task
        self.fnameEdit.setText(task.outputFile)

    def startConvert(self):
        if self.saveParameters():
            self.task.startTask()

    def saveParameters(self):
        oFileFullName = self.fnameEdit.text() + "." + self.task.ext
        # check file if exists
        outputDir = self.dirEdit.text()
        outputPath = os.path.join(outputDir, oFileFullName)
        if os.path.exists(outputPath):
            QMessageBox.warning(self, "错误",
                                    "存在同名文件，请重命名")
            return False
        self.task.outputFile = self.fnameEdit.text()
        self.task.outputDir = outputDir
        return True

    def openDir(self):
        directory = QFileDialog.getExistingDirectory(self, "选择目录",
                                                     QDir.currentPath())
        self.dirEdit.setText(directory)


class Window(QMainWindow):
    addNewTask = Signal()
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.resize(640,480)

        # create actions
        newAction = QAction(self)
        newAction.setText("添加文件")
        newAction.setIcon(QIcon('./images/new.png'))
        newAction.triggered.connect(self.addMediaFile)

        removeAction = QAction(self)
        removeAction.setText("删除文件")
        removeAction.setIcon(QIcon('./images/remove.png'))

        convertAction = QAction(self)
        convertAction.setText("开始转码")
        convertAction.setIcon(QIcon('./images/convert.png'))

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
        self.menuFile.addAction(removeAction)
        self.menuFile.addAction(convertAction)
        self.menuBar.addAction(self.menuFile.menuAction())

        menuEdit = QMenu(self.menuBar)
        menuEdit.setTitle("编辑")
        self.menuBar.addAction(menuEdit.menuAction())
        menuOption = QMenu(self.menuBar)
        menuOption.setTitle("选项")
        self.menuBar.addAction(menuOption.menuAction())
        menuHelp = QMenu(self.menuBar)
        menuHelp.setTitle("帮助")
        self.menuBar.addAction(menuHelp.menuAction())
        # End MenuBar

        # Start toolbar
        mainToolBar = QToolBar(self)
        mainToolBar.setObjectName("mainToolBar")
        self.addToolBar(mainToolBar)
        mainToolBar.addAction(newAction)
        mainToolBar.addAction(removeAction)
        mainToolBar.addAction(convertAction)
        # End toolbar

        # splitter
        self.mainSplitter = QSplitter(Qt.Vertical)
        self.setCentralWidget(self.mainSplitter)
        self.mainSplitter.setStretchFactor(0, 3)
        self.mainSplitter.setStretchFactor(1, 1)

        convTask = ConvTask("/home/ss/Test1.mp4")

        # timely update progress rate
        # use add file to add task
        self.convTaskModel = ConvTaskModel()
        self.convTaskModel.addTask(convTask)

        self.taskTableView = ConvTaskTableView()
        self.taskTableView.setModel(self.convTaskModel)
        self.taskTableView.setItemDelegate(ConvTaskDelegate(self))
        self.taskTableView.setColumnWidth(0, 400)

        # self.taskListWidget = QWidget()
        # self.mainSplitter.addWidget(self.taskListWidget)
        self.mainSplitter.addWidget(self.taskTableView)
        self.generalSettingTabWidget = QTabWidget()
        self.mainSplitter.addWidget(self.generalSettingTabWidget)

        # Begin info tabWidget
        self.generalSettingWidget = GeneralSettingWidget(self)
        self.generalSettingTabWidget.addTab(self.generalSettingWidget, "通用设置")
        # End info tabWidget

        # Begin tab2Widget
        self.tab_2 = QWidget()
        self.generalSettingTabWidget.addTab(self.tab_2, "视频参数设置")
        # End tab2Widget

        self.tab_3 = QWidget()
        self.generalSettingTabWidget.addTab(self.tab_3, "音频参数设置")

        self.tab_4 = QWidget()
        self.generalSettingTabWidget.addTab(self.tab_4, "转码命令行")

        self.statusBar = QStatusBar(self)
        self.statusBar.setObjectName("statusBar")
        self.setStatusBar(self.statusBar)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refreshProgress)
        self.timer.start(2000)

        self.taskTableView.clickOnRow.connect(self.clickOnRow)
        self.taskTableView.deleteTaskSig.connect(self.deleteTask)
        #self.convTaskModel.tasks[0].startTask()

    @Slot()
    def deleteTask(self):
        self.generalSettingWidget.setDisabled(True)

    @Slot()
    def clickOnRow(self, row):
        self.generalSettingWidget.setTask(self.convTaskModel.tasks[row])

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
        # progressRate = self.convTaskModel.tasks[0].progressRate
        # if progressRate < 100:
        #     progressRate += 1
        # self.convTaskModel.tasks[0].progressRate = progressRate
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