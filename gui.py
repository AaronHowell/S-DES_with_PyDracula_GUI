from PyQt5.QtCore import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import *

from Multithreading import Multi_bruteForce
from S_DES import *
from main_r import *

import time


class gui(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建 Ui_MainWindow 实例并设置到主窗口
        self.algorithm_flag=False #False为DES模式，True为AES模式


        self.timer=None
        self.counter=0
        self.int_pattern = r"^(?:[1-9]|[1-9][0-9]|1[01][0-9]|12[0-7])$"  # 匹配1到128的整数
        self.int_validator = QRegExpValidator(QRegExp(self.int_pattern))
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_thread_status)
        self.timer.start(2000)
        self.flag = True
        self.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.threads = []
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setValidate()
        self.bottom_set()
        self.Cipher = S_DES()
        self.buttonSet(False)
        self.plainTextEdit_5.textChanged.connect(self.Encryption_word)
        self.plainTextEdit_6.textChanged.connect(self.Decryption_word)
        self.plainTextEdit.setReadOnly(True)
        self.lineEdit.setReadOnly(True)
        self.plainTextEdit_10.textChanged.connect(self.BitEncrption)
        self.plainTextEdit_12.textChanged.connect(self.BitDecrption)
        # 用正则表达式，限制输入的密钥必须是01字符串
        regex = QRegExp("^[01]+$")
        regex_validator = QRegExpValidator(regex)
        self.lineEdit_2.setValidator(regex_validator)
        self.lineEdit_3.setValidator(regex_validator)

        self.Group=QButtonGroup()
        self.Group.addButton(self.DES_button)
        self.Group.addButton(self.AES_button)
        self.DES_button.setChecked(True)
        self.setFixedSize(940,800)
        self.DES_button.toggled.connect(self.onRadioButtonToggled)

    def refresh(self):
        self.setValidate()
    def onRadioButtonToggled(self):
        # 获取选中的单选按钮
        selected_button = self.Group.checkedButton()
        if selected_button.text()=='S-DES':
            self.algorithm_flag=False
        elif selected_button.text()=='S-AES':
            self.algorithm_flag=True
        print(self.algorithm_flag)
    def check_thread_status(self):
        if len(self.threads) != 0:
            all_finished = all(thread.isFinished() for thread in self.threads)
            if all_finished:
                print("All threads have finished.")
                self.timer.stop()

    def setValidate(self):
        if self.algorithm_flag:
            self.lineEdit_4.setValidator(self.int_validator)
            self.plainTextEdit_8.textChanged.connect(self.validateInput_16bit) #暴力破解明文框
            self.plainTextEdit_7.textChanged.connect(self.validateInput_16bit) #暴力破解密文框
            self.plainTextEdit_10.textChanged.connect(self.validateInput)
            self.plainTextEdit_11.textChanged.connect(self.validateInput)
            self.plainTextEdit_12.textChanged.connect(self.validateInput)
        else:
            self.lineEdit_4.setValidator(self.int_validator)
            self.plainTextEdit_8.textChanged.connect(self.validateInput_8bit)
            self.plainTextEdit_7.textChanged.connect(self.validateInput_8bit)
            self.plainTextEdit_10.textChanged.connect(self.validateInput)
            self.plainTextEdit_11.textChanged.connect(self.validateInput)
            self.plainTextEdit_12.textChanged.connect(self.validateInput)
    def validateInput(self):
        """控制输入为01字符串"""
        sender = self.sender()
        if isinstance(sender, QPlainTextEdit):
            text = sender.toPlainText()
            valid_chars = '01'
            new_text = ''.join(char for char in text if char in valid_chars)
            if new_text != text:
                sender.setPlainText(new_text)
                cursor = sender.textCursor()
                cursor.movePosition(QTextCursor.End)
                sender.setTextCursor(cursor)
    def validateInput_8bit(self):
        """控制输入为01字符串，且为8bit"""
        sender = self.sender()
        if isinstance(sender, QPlainTextEdit):
            text = sender.toPlainText()
            valid_chars = '01'
            new_text = ''.join(char for char in text if char in valid_chars)
            if len(new_text) > 8:
                new_text = new_text[:8]
            if new_text != text:
                sender.setPlainText(new_text)
                cursor = sender.textCursor()
                cursor.movePosition(QTextCursor.End)
                sender.setTextCursor(cursor)
    def validateInput_16bit(self):
        """控制输入为01字符串，且为8bit"""
        sender = self.sender()
        if isinstance(sender, QPlainTextEdit):
            text = sender.toPlainText()
            valid_chars = '01'
            new_text = ''.join(char for char in text if char in valid_chars)
            if len(new_text) > 16:
                new_text = new_text[:16]
            if new_text != text:
                sender.setPlainText(new_text)
                cursor = sender.textCursor()
                cursor.movePosition(QTextCursor.End)
                sender.setTextCursor(cursor)

    def buttonSet(self, flag: bool):
        self.pushButton_2.setEnabled(flag)
        self.pushButton_3.setEnabled(flag)
        self.plainTextEdit_5.isReadOnly()
        if flag:
            self.plainTextEdit_5.setReadOnly(False)
            self.plainTextEdit_6.setReadOnly(False)
            self.plainTextEdit_10.setReadOnly(False)
            self.plainTextEdit_12.setReadOnly(False)
            self.pushButton_2.setStyleSheet('background-color: rgb(52, 59, 72);')
            self.pushButton_3.setStyleSheet('background-color: rgb(52, 59, 72);')
            self.plainTextEdit_5.setStyleSheet('background - color: rgb(33, 37, 43);')
            self.plainTextEdit_6.setStyleSheet('background - color: rgb(33, 37, 43);')
            self.plainTextEdit_10.setStyleSheet('background - color: rgb(33, 37, 43);')
            self.plainTextEdit_12.setStyleSheet('background - color: rgb(33, 37, 43);')

        else:
            self.plainTextEdit_5.setReadOnly(True)
            self.plainTextEdit_6.setReadOnly(True)
            self.plainTextEdit_10.setReadOnly(True)
            self.plainTextEdit_12.setReadOnly(True)
            self.plainTextEdit_10.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')
            self.plainTextEdit_12.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')

            self.plainTextEdit_5.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')
            self.plainTextEdit_6.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')
            self.pushButton_2.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')
            self.pushButton_3.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')

    def bottom_set(self):
        # 最小化按钮
        self.minimizeAppBtn.clicked.connect(lambda: self.showMinimized())
        # 关闭按钮
        self.closeAppBtn.clicked.connect(lambda: self.close())
        # 侧边栏
        self.btn_new.clicked.connect(self.buttonClick)
        self.btn_save.clicked.connect(self.buttonClick)
        self.pushButton.clicked.connect(self.buttonClick)
        self.pushButton_4.clicked.connect(self.buttonClick)
        self.pushButton_11.clicked.connect(self.buttonClick)
        self.pushButton_3.clicked.connect(self.buttonClick)
        self.pushButton_2.clicked.connect(self.buttonClick)
        self.pushButton_5.clicked.connect(self.buttonClick)
        self.btn_bit.clicked.connect(self.buttonClick)
        self.btn_try.clicked.connect(self.buttonClick)
        self.pushButton_13.clicked.connect(self.buttonClick)
        self.pushButton_12.clicked.connect(self.buttonClick)
        self.toggleButton.clicked.connect(lambda: self.toggleMenu(True))

    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()
        # SHOW HOME PAGE
        if btnName == "btn_try":
            self.stackedWidget.setCurrentWidget(self.home)
        if btnName == "btn_bit":
            self.stackedWidget.setCurrentWidget(self.bit_page)
        if btnName == 'btn_new':
            self.stackedWidget.setCurrentWidget(self.File)
        if btnName == 'btn_save':
            self.stackedWidget.setCurrentWidget(self.Text)
        if btnName == "pushButton":
            self.showFileDialog()
        if btnName == "pushButton_4":
            if self.algorithm_flag:
                text = self.lineEdit_2.text()
                if self.is_binary_string_16(text):
                    self.lineEdit_3.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
                    self.Cipher.SetKey([int(x) for x in text])
                    QMessageBox.warning(self, '确认', '密钥已写入。')
                    self.buttonSet(True)
                else:
                    QMessageBox.warning(self, '警告', '请输入合法的16位二进制密钥。')
                    text = self.Cipher.GetKey()
                    self.lineEdit_3.setText(text)
                    self.lineEdit_2.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
            else:
                text = self.lineEdit_2.text()
                if self.is_binary_string(text):
                    self.lineEdit_3.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
                    self.Cipher.SetKey([int(x) for x in text])
                    QMessageBox.warning(self, '确认', '密钥已写入。')
                    self.buttonSet(True)
                else:
                    QMessageBox.warning(self, '警告', '请输入合法的10位二进制密钥。')
                    text = self.Cipher.GetKey()
                    self.lineEdit_3.setText(text)
                    self.lineEdit_2.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
        if btnName == "pushButton_13":
            if self.algorithm_flag:
                text = self.plainTextEdit_11.toPlainText()
                if self.is_binary_string_16(text):
                    self.lineEdit_3.setText(text)
                    self.lineEdit_2.setText(text)
                    self.Cipher.SetKey([int(x) for x in text])
                    QMessageBox.warning(self, '确认', '密钥已写入。')
                    self.buttonSet(True)
                else:
                    QMessageBox.warning(self, '警告', '请输入合法的16位二进制密钥。')
                    text = self.Cipher.GetKey()
                    self.lineEdit_3.setText(text)
                    self.lineEdit_2.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
            else:
                text = self.plainTextEdit_11.toPlainText()
                if self.is_binary_string(text):
                    self.lineEdit_3.setText(text)
                    self.lineEdit_2.setText(text)
                    self.Cipher.SetKey([int(x) for x in text])
                    QMessageBox.warning(self, '确认', '密钥已写入。')
                    self.buttonSet(True)
                else:
                    QMessageBox.warning(self, '警告', '请输入合法的10位二进制密钥。')
                    text = self.Cipher.GetKey()
                    self.lineEdit_3.setText(text)
                    self.lineEdit_2.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
        if btnName == "pushButton_11":
            if self.algorithm_flag:
                text = self.lineEdit_3.text()
                if self.is_binary_string_16(text):
                    self.lineEdit_2.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
                    self.Cipher.SetKey([int(x) for x in text])
                    QMessageBox.warning(self, '确认', '密钥已写入。')
                    self.buttonSet(True)
                else:
                    QMessageBox.warning(self, '警告', '请输入合法的16位二进制密钥。')
                    text = self.Cipher.GetKey()
                    self.lineEdit_3.setText(text)
                    self.lineEdit_2.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
            else:
                text = self.lineEdit_3.text()
                if self.is_binary_string(text):
                    self.lineEdit_2.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
                    self.Cipher.SetKey([int(x) for x in text])
                    QMessageBox.warning(self, '确认', '密钥已写入。')
                    self.buttonSet(True)
                else:
                    QMessageBox.warning(self, '警告', '请输入合法的10位二进制密钥。')
                    text = self.Cipher.GetKey()
                    self.lineEdit_3.setText(text)
                    self.lineEdit_2.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
        if btnName == "pushButton_3":
            self.Encryption_file()
        if btnName == "pushButton_2":
            self.Decryption_file()
        if btnName == "pushButton_5":
            self.Save_File()
        if btnName == "pushButton_12":
            self.bruteForceAttack()
            self.plainTextEdit_9.setPlainText("")
    def ShowFinishMsg(self, id):
        self.counter+=1
        self.progressBar.setValue(int(self.counter/int(self.lineEdit_4.text())*100))

        if self.counter==int(self.lineEdit_4.text()):
            self.plainTextEdit_9.appendPlainText(f"Theard:{id}已退出")
            self.plainTextEdit_9.appendPlainText(f"破解完成，用时{time.perf_counter()-self.timer}")
        else:
            self.plainTextEdit_9.appendPlainText(f"Theard:{id}已退出")
    def ShowResultMsg(self, list):
        self.plainTextEdit_9.appendPlainText(f"Theard:{list[0]}找到结果{list[1]}")
    def bruteForceAttack(self):
        self.threads = []
        self.plainTextEdit_9.setPlainText("")
        self.progressBar.setValue(0)
        P_word = self.plainTextEdit_8.toPlainText()
        C_word = self.plainTextEdit_7.toPlainText()
        Thread_num = self.lineEdit_4.text()
        if len(P_word) == len(C_word) == 8 and Thread_num != "":
            Thread_num = int(Thread_num)
            task_list = self.divide_task(Thread_num)
            self.timer=time.perf_counter()

            for i in range(Thread_num):
                thread = Multi_bruteForce(i, task_list[i][0], task_list[i][1], P_word, C_word)
                thread.finished_signal.connect(self.ShowFinishMsg)
                thread.result_signal.connect(self.ShowResultMsg)
                thread.start()
                self.plainTextEdit_9.appendPlainText(f"Theard:{i}已启动")
                self.threads.append(thread)

        else:
            QMessageBox.warning(self, "警告", "请输入正确的明密和线程数量")
    def BitEncrption(self):
        self.plainTextEdit_12.textChanged.disconnect()
        Text = self.plainTextEdit_10.toPlainText()
        if len(Text) % 8 == 0:
            binary_string = ""
            BinaryList = [int(x) for x in Text]
            for i in range(0, len(BinaryList), 8):
                EncryptedList = self.Cipher.Encryption(BinaryList[i:i + 8])
                binary_string = binary_string + ''.join(map(str, EncryptedList))
            self.plainTextEdit_12.setPlainText(binary_string)
        self.plainTextEdit_12.textChanged.connect(self.BitDecrption)
    def BitDecrption(self):
        self.plainTextEdit_10.textChanged.disconnect()
        Text = self.plainTextEdit_12.toPlainText()
        if len(Text) % 8 == 0:
            binary_string = ""
            BinaryList = [int(x) for x in Text]
            for i in range(0, len(BinaryList), 8):
                DecryptedList = self.Cipher.Decryption(BinaryList[i:i + 8])
                binary_string = binary_string + ''.join(map(str, DecryptedList))
            self.plainTextEdit_10.setPlainText(binary_string)
        self.plainTextEdit_10.textChanged.connect(self.BitEncrption)
    def is_binary_string(self, s):
        # 检查字符串是否仅包含0和1
        if not all(char in '01' for char in s):
            return False
        # 检查字符串长度是否为8
        if len(s) != 10:
            return False
        # 如果通过了上述两个条件，字符串是有效的8位二进制字符串
        return True
    def is_binary_string_16(self, s):
        # 检查字符串是否仅包含0和1
        if not all(char in '01' for char in s):
            return False
        # 检查字符串长度是否为8
        if len(s) != 16:
            return False
        # 如果通过了上述两个条件，字符串是有效的8位二进制字符串
        return True
    def toggleMenu(self, enable):
        if enable:
            # GET WIDTH
            width = self.leftMenuBg.width()
            maxExtend = 320
            standard = 60

            # SET MAX WIDTH
            if width == 60:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # ANIMATION
            self.animation = QPropertyAnimation(self.leftMenuBg, b"minimumWidth")
            self.animation.setDuration(500)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()
    def Encryption_word(self):
        self.plainTextEdit_6.textChanged.disconnect()
        character = ""
        Text = self.plainTextEdit_5.toPlainText()
        AsciiText = [ord(char) for char in Text]
        bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]
        for Binary_word in bit_array_text:
            EncryptedList = self.Cipher.Encryption([int(x) for x in Binary_word])
            AsciiCode = int(''.join(map(str, EncryptedList)), 2)
            character = character + chr(AsciiCode)
        self.plainTextEdit_6.setPlainText(character)
        self.plainTextEdit_6.textChanged.connect(self.Decryption_word)
    def Decryption_word(self):
        self.plainTextEdit_5.textChanged.disconnect()
        character = ""
        Text = self.plainTextEdit_6.toPlainText()
        AsciiText = [ord(char) for char in Text]
        bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]
        for Binary_word in bit_array_text:
            EncryptedList = self.Cipher.Decryption([int(x) for x in Binary_word])
            AsciiCode = int(''.join(map(str, EncryptedList)), 2)
            character = character + chr(AsciiCode)
        self.plainTextEdit_5.setPlainText(character)
        self.plainTextEdit_5.textChanged.connect(self.Decryption_word)
    def showFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # 如果需要只读文件

        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Text Files (*.txt)')
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.lineEdit.setText(selected_files[0])
                with open(selected_files[0], 'r', encoding='utf-8') as file:
                    text = file.read()
                    self.plainTextEdit.setPlainText(text)
    def Encryption_file(self):
        character = ""
        Text = self.plainTextEdit.toPlainText()
        AsciiText = [ord(char) for char in Text]
        bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]
        for Binary_word in bit_array_text:
            EncryptedList = self.Cipher.Encryption([int(x) for x in Binary_word])
            AsciiCode = int(''.join(map(str, EncryptedList)), 2)
            character = character + chr(AsciiCode)
        self.plainTextEdit.setPlainText(character)
    def Decryption_file(self):
        character = ""
        Text = self.plainTextEdit.toPlainText()
        AsciiText = [ord(char) for char in Text]
        bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]
        for Binary_word in bit_array_text:
            EncryptedList = self.Cipher.Decryption([int(x) for x in Binary_word])
            AsciiCode = int(''.join(map(str, EncryptedList)), 2)
            character = character + chr(AsciiCode)
        self.plainTextEdit.setPlainText(character)
    def divide_task(self, num_segments):
        start = 0
        end = 1023
        if num_segments <= 0:
            return []

        segment_size = (end - start) // num_segments

        segments = []
        current_start = start

        for _ in range(num_segments):
            current_end = current_start + segment_size
            # 确保最后一个段不超出范围的终点
            if _ == num_segments - 1:
                current_end = end
            # 将起点和终点转换为8位二进制字符串
            start_binary = format(current_start, '010b')
            end_binary = format(current_end, '010b')
            segments.append((start_binary, end_binary))
            current_start = current_end + 1

        return segments
    def Save_File(self):
        text = self.plainTextEdit.toPlainText()
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # 设置文件对话框为只读模式
        # 打开文件对话框，让用户选择保存文件的目录和文件名
        file_dialog, _ = QFileDialog.getSaveFileName(self, "保存为txt文件", "", "Text Files (*.txt);;All Files (*)",
                                                     options=options)
        if file_dialog:
            try:
                with open(file_dialog, 'w', encoding="utf-8") as file:
                    file.write(text)
                print(f'文本已保存为 {file_dialog}')

                QMessageBox.information(self, "信息", "文件已保存")
            except Exception as e:
                QMessageBox.warning(self, '错误', '文件保存错误')
                print(f'保存文件时发生错误：{e}')






    def sizeHint(self):
        return QSize(600, 400)

    def eventFilter(self, obj, event):
        if obj == self.closeButton and event.type() == event.Enter:
            self.animateColor()
        return super(gui, self).eventFilter(obj, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # 如果鼠标左键按下
            self._dragPosition = event.globalPos() - self.frameGeometry().topLeft()  # 计算鼠标在窗口中的位置

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._dragPosition:  # 如果鼠标左键按下且已记录位置
            self.move(event.globalPos() - self._dragPosition)  # 移动窗口到新的位置

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  # 如果鼠标左键释放
            self._dragPosition = None  # 清空记录的位置


if __name__ == "__main__":
    app = QApplication([])
    main_window = gui()
    main_window.show()
    app.exec_()
