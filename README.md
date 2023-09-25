# S-DES_with_PyDracula_GUI

## 使用前准备
##### 环境准备

使用之前，请先对照requirements.txt 安装相应的环境，并且安装pyqt5-tools，可以使用一下shell命令:

pip install PyQt5==5.15.9

pip install PyQt5_sip==12.12.1

pip install pyqt5-tools

##### 资源文件和UI文件以适应你的电脑
在项目目录下，使用

pyrcc5 resources.qrc -o resources_rc.py
对资源文件重编译

pyuic5 main_r.ui -o main_r.py
对UI文件重新生成

##### 运行gui.py即可