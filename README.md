# S-DES_with_PyDracula_GUI\n\n## 使用前准备\n\n### 环境准备\n\n使用之前，请先对照 `requirements.txt` 安装相应的环境，并且安装 `pyqt5-tools`，可以使用以下shell命令:\n\n```shell\npip install PyQt5==5.15.9\npip install PyQt5_sip==12.12.1\npip install pyqt5-tools\n```\n\n### 资源文件和UI文件以适应你的电脑\n\n在项目目录下，使用\n\n```shell\npyrcc5 resources.qrc -o resources_rc.py\n```\n对资源文件重编译\n\n```shell\npyuic5 main_r.ui -o main_r.py\n```\n对UI文件重新生成\n\n### 运行 `gui.py` 即可
