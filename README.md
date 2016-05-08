# PySideAvConv
基于python3-pySide和libavtools的**简易视频转码器**， 同类软件有winff， 提供实时进度显示，多任务转码管理。
通过添加preset中的json文件，参考已有两个json文件，可以扩展提供更多格式的支持。

在Ubuntu14.04LTS上测试通过，在其余linux系统应该也可以使用。
Dependencies: python3-pyside, libav-tools

##在Ubuntu上安装依赖项目
```
sudo apt-get install python3-pyside
sudo apt-get install libav-tools
```
## 运行
在项目目录下使用```python3 main.py```运行，或者执行```chmod u+x ./videoConverter.sh```然后双击sh文件运行
