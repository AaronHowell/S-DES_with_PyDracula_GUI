import multiprocessing
import time
from multiprocessing import *

from PyQt5.QtCore import *
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import *

from Multithreading import Multi_bruteForce
from MultithreadingOfAES import *
from S_AES import *
from S_DES import *
from main_r import *


class gui(Ui_MainWindow, QMainWindow):
    def __init__(self):
        super().__init__()
        self.T_Queue=Queue()
        self.timerOfStep1=QTimer()
        self.timerOfStep1.timeout.connect(self.ShowFinishMsg_16)
        self.timerOfStep1.start(1000)

        self.timerOfStep2=QTimer()
        self.timerOfStep2.timeout.connect(self.Step2Finsh)


        self.event=Event()
        self.Encryption_flag = 0
        self.flag_CBC_2 = False
        self.flag_CBC_1 = False
        self.read_lock=multiprocessing.Lock()
        # 创建 Ui_MainWindow 实例并设置到主窗口
        self.algorithm_flag = False  # False为DES模式，True为AES模式
        self.timer = None
        self.counter = 0
        self.int_pattern = r"^(?:[1-9]|[1-9][0-9]|1[01][0-9]|12[0-7])$"  # 匹配1到128的整数
        self.int_validator = QRegExpValidator(QRegExp(self.int_pattern))
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.check_thread_status)
        self.timer2.start(1000)
        self.flag = True
        self.setupUi(self)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.threads = []
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setValidate()
        self.bottom_set()
        self.Cipher = S_DES()
        self.Cipher_AES = S_AES()
        self.Cipher_AES_mul_1 = S_AES()
        self.Cipher_AES_mul_2 = S_AES()
        self.Cipher_AES_mul_3 = S_AES()
        self.MulTextEditSetUnable()
        self.buttonSet(False)
        self.plainTextEdit_5.textChanged.connect(self.Encryption_word)
        self.plainTextEdit_6.textChanged.connect(self.Decryption_word)

        self.plainTextEdit_13.textChanged.connect(self.MulEncryption)
        self.plainTextEdit_14.textChanged.connect(self.MulDecryption)

        self.plainTextEdit.setReadOnly(True)
        self.lineEdit.setReadOnly(True)
        self.plainTextEdit_10.textChanged.connect(self.BitEncrption)
        self.plainTextEdit_12.textChanged.connect(self.BitDecrption)
        # 用正则表达式，限制输入的密钥必须是01字符串
        regex = QRegExp("^[01]+$")
        regex_validator = QRegExpValidator(regex)
        self.lineEdit_2.setValidator(regex_validator)
        self.lineEdit_3.setValidator(regex_validator)

        self.Group = QButtonGroup()
        self.Group.addButton(self.DES_button)
        self.Group.addButton(self.AES_button)
        self.DES_button.setChecked(True)
        self.setFixedSize(940, 800)
        self.DES_button.toggled.connect(self.onRadioButtonToggled)
        self.comboBox.currentTextChanged.connect(self.SetEncryptionWays)
        self.onRadioButtonToggled()
        self.plainTextEdit_15.textChanged.connect(self.CBC_Encrption)
        self.plainTextEdit_16.textChanged.connect(self.CBC_Decrption)


        self.P_Queue = Queue()  # 多进程通信管道
        self.F_Queue = Queue()
        self.Pg_Queue = Queue()
        self.counter2 = 0

    def Show16Process(self):
        while not (self.Pg_Queue.empty()):
            self.counter2 += 1
            print(self.counter2)
            self.Pg_Queue.get()
            self.progressBar.setValue(int(self.counter2 / (65535) * 100))




    def MulEncryption(self):
        if self.Encryption_flag == 0 or self.Encryption_flag == 1:
            self.plainTextEdit_14.textChanged.disconnect()
            character = ""
            Text = self.plainTextEdit_13.toPlainText()
            AsciiText = [ord(char) for char in Text]
            bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]
            # Ensure the length is even by adding a space if needed
            if len(bit_array_text) % 2 != 0:
                bit_array_text.append('0' * 8)  # Add a space (8 zeros) to make it even
            # Initialize an empty list to store the 16-bit binary strings
            bit_array_16bit = []
            for i in range(0, len(bit_array_text), 2):
                # Combine two 8-bit binary strings into one 16-bit string
                binary_word = bit_array_text[i] + bit_array_text[i + 1]
                bit_array_16bit.append(binary_word)
            if self.Encryption_flag == 0:
                for Binary_word in bit_array_16bit:
                    EncryptedList = self.Cipher_AES.Encryption([int(x) for x in Binary_word])
                    EncryptedList = self.Cipher_AES_mul_2.Encryption(EncryptedList)
                    AsciiCode1 = int(''.join(map(str, EncryptedList[:8])), 2)
                    AsciiCode2 = int(''.join(map(str, EncryptedList[8:])), 2)
                    character = character + chr(AsciiCode1) + chr(AsciiCode2)
            elif self.Encryption_flag == 1:
                for Binary_word in bit_array_16bit:
                    EncryptedList = self.Cipher_AES_mul_1.Encryption([int(x) for x in Binary_word])
                    EncryptedList = self.Cipher_AES_mul_2.Encryption(EncryptedList)
                    EncryptedList = self.Cipher_AES_mul_3.Encryption(EncryptedList)
                    AsciiCode1 = int(''.join(map(str, EncryptedList[:8])), 2)
                    AsciiCode2 = int(''.join(map(str, EncryptedList[8:])), 2)
                    character = character + chr(AsciiCode1) + chr(AsciiCode2)
            self.plainTextEdit_14.setPlainText(character)
            self.plainTextEdit_14.textChanged.connect(self.MulDecryption)
        elif self.Encryption_flag == 2:
            self.plainTextEdit_14.textChanged.disconnect()  # 串加密，密文

            Text = self.plainTextEdit_13.toPlainText()  # 串加密，明文
            if len(Text) % 16 == 0:
                binary_string = ""
                BinaryList = [int(x) for x in Text]
                for i in range(0, len(BinaryList), 16):
                    EncryptedList = self.Cipher_AES_mul_1.Encryption(BinaryList[i:i + 16])
                    EncryptedList = self.Cipher_AES_mul_2.Encryption(EncryptedList)
                    binary_string = binary_string + ''.join(map(str, EncryptedList))
                self.plainTextEdit_14.setPlainText(binary_string)
            self.plainTextEdit_14.textChanged.connect(self.MulDecryption)

    def MulDecryption(self):
        if self.Encryption_flag == 0 or self.Encryption_flag == 1:
            self.plainTextEdit_13.textChanged.disconnect()
            character = ""
            Text = self.plainTextEdit_14.toPlainText()
            AsciiText = [ord(char) for char in Text]
            bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]
            if len(bit_array_text) % 2 != 0:
                bit_array_text.append('0' * 8)
            bit_array_16bit = []
            for i in range(0, len(bit_array_text), 2):
                binary_word = bit_array_text[i] + bit_array_text[i + 1]
                bit_array_16bit.append(binary_word)
            if self.Encryption_flag == 0:
                for Binary_word in bit_array_16bit:
                    DecryptedList = self.Cipher_AES_mul_2.Decryption([int(x) for x in Binary_word])
                    DecryptedList = self.Cipher_AES_mul_1.Decryption(DecryptedList)
                    AsciiCode1 = int(''.join(map(str, DecryptedList[:8])), 2)
                    AsciiCode2 = int(''.join(map(str, DecryptedList[8:])), 2)
                    character = character + chr(AsciiCode1) + chr(AsciiCode2)
            elif self.Encryption_flag == 1:
                for Binary_word in bit_array_16bit:
                    DecryptedList = self.Cipher_AES_mul_3.Decryption([int(x) for x in Binary_word])
                    DecryptedList = self.Cipher_AES_mul_2.Decryption(DecryptedList)
                    DecryptedList = self.Cipher_AES_mul_1.Decryption(DecryptedList)
                    AsciiCode1 = int(''.join(map(str, DecryptedList[:8])), 2)
                    AsciiCode2 = int(''.join(map(str, DecryptedList[8:])), 2)
                    character = character + chr(AsciiCode1) + chr(AsciiCode2)

            self.plainTextEdit_13.setPlainText(character)
            self.plainTextEdit_13.textChanged.connect(self.MulEncryption)
        elif self.Encryption_flag == 2:
            self.plainTextEdit_13.textChanged.disconnect()  # 串加密，密文

            Text = self.plainTextEdit_14.toPlainText()  # 串加密，明文
            if len(Text) % 16 == 0:
                binary_string = ""
                BinaryList = [int(x) for x in Text]
                for i in range(0, len(BinaryList), 16):
                    DecryptedList = self.Cipher_AES_mul_2.Decryption(BinaryList[i:i + 16])
                    DecryptedList = self.Cipher_AES_mul_1.Decryption(DecryptedList)
                    binary_string = binary_string + ''.join(map(str, DecryptedList))
                self.plainTextEdit_13.setPlainText(binary_string)
            self.plainTextEdit_13.textChanged.connect(self.MulDecryption)

    def CheckInputOfAES(self):
        if self.Encryption_flag == 0 or self.Encryption_flag == 2:
            text = self.lineEdit_5.text()
            if self.is_hex_string_hex_8(text):
                Key_List = self.hex_string_to_binary_list(text)
                if len(Key_List) < 32:
                    # 计算需要添加的零的数量
                    num_zeros_to_add = 32 - len(Key_List)
                    # 在列表前面添加零
                    Key_List = [0] * num_zeros_to_add + Key_List
                self.Cipher_AES_mul_1.SetKey(Key_List[:16])
                self.Cipher_AES_mul_2.SetKey(Key_List[16:])
                self.MulTextEditSetable()
                QMessageBox.warning(self, '提示', '已写入双重加密密钥。')
            else:
                QMessageBox.warning(self, '警告', '请输入合法的8位十六进制密钥。')
                text = self.Cipher_AES_mul_1.GetKey() + self.Cipher_AES_mul_2.GetKey()
                hex_string = self.binary_string_to_hex(text)
                if len(hex_string) < 8:
                    num_zeros_to_add = 8 - len(hex_string)
                    # 在字符串前面添加零
                    hex_string = "0" * num_zeros_to_add + hex_string
                self.lineEdit_5.setText(hex_string)


        elif self.Encryption_flag == 1:
            text = self.lineEdit_5.text()
            if self.is_hex_string_hex_12(text):
                Key_List = self.hex_string_to_binary_list(text)
                if len(Key_List) < 48:
                    # 计算需要添加的零的数量
                    num_zeros_to_add = 48 - len(Key_List)
                    # 在列表前面添加零
                    Key_List = [0] * num_zeros_to_add + Key_List
                self.Cipher_AES_mul_1.SetKey(Key_List[:16])
                self.Cipher_AES_mul_2.SetKey(Key_List[16:32])
                self.Cipher_AES_mul_3.SetKey(Key_List[32:])
                self.MulTextEditSetable()
                QMessageBox.warning(self, '提示', '已写入三重加密密钥。')
            else:
                QMessageBox.warning(self, '警告', '请输入合法的12位十六进制密钥。')
                text = self.Cipher_AES_mul_1.GetKey() + self.Cipher_AES_mul_2.GetKey() + self.Cipher_AES_mul_3.GetKey()

                hex_string = self.binary_string_to_hex(text)
                if len(hex_string) < 8:
                    num_zeros_to_add = 8 - len(hex_string)
                    # 在字符串前面添加零
                    hex_string = "0" * num_zeros_to_add + hex_string
                self.lineEdit_5.setText(hex_string)

    def refresh(self):
        self.setValidate()

    def onRadioButtonToggled(self):
        # 获取选中的单选按钮
        selected_button = self.Group.checkedButton()
        if selected_button.text() == 'S-DES':
            self.algorithm_flag = False
            self.btn_multiple.setDisabled(True)
            self.btn_multiple.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;'
                                            'background-image: url(:/icons/images/icons/cil-loop-circular.png);')
            self.refresh()
        elif selected_button.text() == 'S-AES':
            self.algorithm_flag = True
            self.btn_multiple.setDisabled(False)
            self.btn_multiple.setStyleSheet('background-color: rgb(33, 37, 43);'
                                            ".QPushButton:hover {\n"
                                            "    background-color: rgb(40, 44, 52);\n"
                                            "}\n"
                                            ".QPushButton:pressed {    \n"
                                            "    background-color: rgb(189, 147, 249);\n"
                                            "    color: rgb(255, 255, 255);\n"
                                            "}\n"
                                            ".QPushButton {    \n"
                                            "    background-position: left center;\n"
                                            "    background-repeat: no-repeat;\n"
                                            "    border: none;\n"
                                            "    border-left: 20px solid transparent;\n"
                                            "    background-color:transparent;\n"
                                            "    text-align: left;\n"
                                            "    padding-left: 44px;\n"
                                            "}\n"
                                            ".QPushButton:hover {\n"
                                            "    background-color: rgb(40, 44, 52);\n"
                                            "}\n"
                                            ".QPushButton:pressed {    \n"
                                            "    background-color: rgb(189, 147, 249);\n"
                                            "    color: rgb(255, 255, 255);\n"
                                            "}\n"
                                            'background-image: url(:/icons/images/icons/cil-loop-circular.png);'
                                            )
            self.btn_multiple.setStyleSheet('background-image: url(:/icons/images/icons/cil-loop-circular.png);')
            self.refresh()
    def Step2Finsh(self):
        while not(self.F_Queue.empty()):
            self.plainTextEdit_9.appendPlainText(f"Process:{self.F_Queue.get()}已退出")
            self.counter += 1
            if self.counter%int(self.lineEdit_4.text())==0:
                self.plainTextEdit_9.appendPlainText(f"破解完成，用时{time.perf_counter() - self.timer}")
    def check_thread_status(self):
        if self.algorithm_flag:
            self.Show16Process()
            self.ShowResultMsg_16()


        else:
            if len(self.threads) != 0:
                all_finished = all(thread.isFinished() for thread in self.threads)
                if all_finished:
                    print("All threads\Processes have finished.")

    def setValidate(self):
        if self.algorithm_flag:
            self.lineEdit_4.setValidator(self.int_validator)
            self.plainTextEdit_8.disconnect()
            self.plainTextEdit_7.disconnect()
            self.plainTextEdit_8.textChanged.connect(self.validateInput_16bit)  # 暴力破解明文框
            self.plainTextEdit_7.textChanged.connect(self.validateInput_16bit)  # 暴力破解密文框
        else:
            self.lineEdit_4.setValidator(self.int_validator)
            self.plainTextEdit_8.disconnect()
            self.plainTextEdit_7.disconnect()
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
        """控制输入为01字符串，且为16bit"""
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

    def MulTextEditSetUnable(self):
        self.plainTextEdit_13.setReadOnly(True)
        self.plainTextEdit_14.setReadOnly(True)
        self.plainTextEdit_13.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')
        self.plainTextEdit_14.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')

    def MulTextEditSetable(self):
        self.plainTextEdit_13.setReadOnly(False)
        self.plainTextEdit_14.setReadOnly(False)
        self.plainTextEdit_13.setStyleSheet('background - color: rgb(33, 37, 43);')
        self.plainTextEdit_14.setStyleSheet('background - color: rgb(33, 37, 43);')

    def bottom_set(self):
        # 最小化按钮
        self.minimizeAppBtn.clicked.connect(lambda: self.showMinimized())
        # 关闭按钮
        self.closeAppBtn.clicked.connect(lambda: self.close())
        # 侧边栏
        self.btn_multiple.clicked.connect(self.buttonClick)
        self.pushButton_15.clicked.connect(self.buttonClick)
        self.pushButton_16.clicked.connect(self.buttonClick)
        self.pushButton_6.clicked.connect(self.buttonClick)
        self.btn_new.clicked.connect(self.buttonClick)
        self.btn_save.clicked.connect(self.buttonClick)
        self.pushButton.clicked.connect(self.buttonClick)
        self.pushButton_4.clicked.connect(self.buttonClick)
        self.pushButton_11.clicked.connect(self.buttonClick)
        self.pushButton_3.clicked.connect(self.buttonClick)
        self.pushButton_2.clicked.connect(self.buttonClick)
        self.pushButton_5.clicked.connect(self.buttonClick)
        self.pushButton_14.clicked.connect(self.buttonClick)
        self.btn_bit.clicked.connect(self.buttonClick)
        self.btn_try.clicked.connect(self.buttonClick)
        self.pushButton_13.clicked.connect(self.buttonClick)
        self.pushButton_12.clicked.connect(self.buttonClick)
        self.pushButton_17.clicked.connect(self.buttonClick)
        self.toggleButton.clicked.connect(lambda: self.toggleMenu(True))
        self.CBC_Text_Set()

    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()
        # SHOW HOME PAGE
        if btnName == "pushButton_17":
            self.stackedWidget.setCurrentWidget(self.mul)
        if btnName == "pushButton_6":
            self.stackedWidget.setCurrentWidget(self.CBC)
        if btnName == "btn_try":
            self.stackedWidget.setCurrentWidget(self.home)
        if btnName == "btn_bit":
            self.stackedWidget.setCurrentWidget(self.bit_page)
        if btnName == 'btn_new':
            self.stackedWidget.setCurrentWidget(self.File)
        if btnName == 'btn_save':
            self.stackedWidget.setCurrentWidget(self.Text)
        if btnName == 'btn_multiple':
            self.stackedWidget.setCurrentWidget(self.mul)
        if btnName == "pushButton":
            self.showFileDialog()
        if btnName == "pushButton_4":
            if self.algorithm_flag:
                text = self.lineEdit_2.text()
                if self.is_binary_string_16(text):
                    self.lineEdit_3.setText(text)
                    self.plainTextEdit_11.setPlainText(text)
                    self.Cipher_AES.SetKey([int(x) for x in text])
                    QMessageBox.warning(self, '确认', '密钥已写入。')
                    self.buttonSet(True)
                else:
                    QMessageBox.warning(self, '警告', '请输入合法的16位二进制密钥。')
                    text = self.Cipher_AES.GetKey()
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
                    self.Cipher_AES.SetKey([int(x) for x in text])
                    QMessageBox.warning(self, '确认', '密钥已写入。')

                    self.buttonSet(True)
                else:
                    QMessageBox.warning(self, '警告', '请输入合法的16位二进制密钥。')
                    text = self.Cipher_AES.GetKey()
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
                    self.Cipher_AES.SetKey([int(x) for x in text])
                    QMessageBox.warning(self, '确认', '密钥已写入。')
                    self.buttonSet(True)
                else:
                    QMessageBox.warning(self, '警告', '请输入合法的16位二进制密钥。')
                    text = self.Cipher_AES.GetKey()
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
        if btnName == "pushButton_14":
            self.CheckInputOfAES()
        if btnName == "pushButton_3":
            self.Encryption_file()
        if btnName == "pushButton_2":
            self.Decryption_file()
        if btnName == "pushButton_5":
            self.Save_File()
        if btnName == "pushButton_12":
            self.bruteForceAttack()
            self.plainTextEdit_9.setPlainText("")
        if btnName == "pushButton_15":
            text = self.lineEdit_7.text()
            if self.is_binary_string_16(text):
                self.Cipher_AES.SetKey([int(x) for x in text])
                QMessageBox.warning(self, '确认', '密钥已写入。')
                self.flag_CBC_1=True
                self.CBC_Text_Set()
                self.buttonSet(True)
            else:
                QMessageBox.warning(self, '警告', '请输入合法的16位二进制密钥。')
                self.flag_CBC_1 = False
                self.CBC_Text_Set()
                text = self.Cipher_AES.GetKey()
                self.lineEdit_7.setText(text)
        if btnName == "pushButton_16":
            text = self.lineEdit_6.text()
            if self.is_binary_string_16(text):
                self.Cipher_AES.SetIV([int(x) for x in text])
                QMessageBox.warning(self, '确认', '初始向量已写入。')
                self.flag_CBC_2 = True
                self.CBC_Text_Set()
                self.buttonSet(True)
            else:
                QMessageBox.warning(self, '警告', '请输入合法的16位初始向量。')
                self.flag_CBC_2 = False
                self.CBC_Text_Set()
                text = self.Cipher_AES.GetIV()
                self.lineEdit_6.setText(text)

    def CBC_Text_Set(self):
        if self.flag_CBC_1 and self.flag_CBC_2:
            self.plainTextEdit_15.setReadOnly(False)
            self.plainTextEdit_16.setReadOnly(False)
            self.plainTextEdit_15.setStyleSheet('background - color: rgb(33, 37, 43);')
            self.plainTextEdit_16.setStyleSheet('background - color: rgb(33, 37, 43);')
        else:
            self.plainTextEdit_15.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')
            self.plainTextEdit_16.setStyleSheet('background-color: rgba(50, 50, 50, 0.8); color: #999999;')
            self.plainTextEdit_15.setReadOnly(True)
            self.plainTextEdit_16.setReadOnly(True)

    def ShowFinishMsg_16(self):
        while not(self.F_Queue.empty()):
            self.plainTextEdit_9.appendPlainText(f"Theard:{self.F_Queue.get()}已退出")
            self.counter += 1
            if self.counter == int(self.lineEdit_4.text()):
                self.plainTextEdit_9.appendPlainText(f"第一阶段完成，用时{time.perf_counter() - self.timer}")
                all_data2=[]
                loaded=[]
                with open('En.pkl','rb')as file:
                    while True:
                        try:
                            data2 = pickle.load(file)
                            all_data2.append(data2)
                        except EOFError:
                            break
                for data in all_data2:
                    loaded += data
                dictionary = {item[0]: item[1] for item in loaded}
                Thread_num = int(self.lineEdit_4.text())
                result=self.split_dict(dictionary,Thread_num)
                for i in result:
                    self.T_Queue.put(i)
                for _ in result:
                    self.event.set()
                self.timerOfStep1.stop()
                self.timerOfStep2.start(1000)

    def split_dict(self,input_dict, num_chunks):
        # 计算每个子字典的大小
        chunk_size = len(input_dict) // num_chunks
        remainder = len(input_dict) % num_chunks

        result = []
        start = 0

        for _ in range(num_chunks):
            end = start + chunk_size + (1 if remainder > 0 else 0)
            chunk = {key: input_dict[key] for key in list(input_dict.keys())[start:end]}
            result.append(chunk)
            start = end
            if remainder > 0:
                remainder -= 1

        return result

    def ShowFinishMsg(self, id):
        self.counter += 1
        self.progressBar.setValue(int(self.counter / int(self.lineEdit_4.text()) * 100))

        if self.counter == int(self.lineEdit_4.text()):
            self.plainTextEdit_9.appendPlainText(f"Theard:{id}已退出")
            self.plainTextEdit_9.appendPlainText(f"破解完成，用时{time.perf_counter() - self.timer}")
        else:
            self.plainTextEdit_9.appendPlainText(f"Theard:{id}已退出")

    def ShowResultMsg(self, list):
        self.plainTextEdit_9.appendPlainText(f"Theard:{list[0]}找到结果{list[1]}")

    def ShowResultMsg_16(self):
        if self.counter2 != 0:
            self.plainTextEdit_9.appendPlainText(f"计算完成，开始输出结果")
        self.counter2=0
        num = self.P_Queue.qsize()
        while not(self.P_Queue.empty()):
            self.counter2+=1
            self.progressBar.setValue(int(self.counter2 / num * 100))
            list = self.P_Queue.get()
            hex_string = self.binary_string_to_hex(list[1])
            if len(hex_string) < 8:
                num_zeros_to_add = 8 - len(hex_string)
                # 在字符串前面添加零
                hex_string = "0" * num_zeros_to_add + hex_string
            self.lineEdit_5.setText(hex_string)
            self.plainTextEdit_9.appendPlainText(f"Theard:{list[0]}找到结果{hex_string}")
        if self.counter2!=0:
            self.plainTextEdit_9.appendPlainText(f"输出完毕，共找到密钥对{num}个")

    def bruteForceAttack(self):
        if self.algorithm_flag:
            self.counter = 0
            self.processes = []
            self.plainTextEdit_9.setPlainText("")
            self.progressBar.setValue(0)
            P_word = self.plainTextEdit_8.toPlainText()

            C_word = self.plainTextEdit_7.toPlainText()
            Thread_num = self.lineEdit_4.text()
            if (len(P_word) % 16 == 0) and (len(C_word) % 16 == 0) and (
                    len(P_word) == len(C_word)) and Thread_num != "":
                Thread_num = int(Thread_num)
                task_list = self.divide_task_16bit(Thread_num)
                self.timer = time.perf_counter()
                for i in range(Thread_num):
                    with open('En.pkl','wb') as file1:
                        pass
                    with open('De.pkl','wb') as file2:
                        pass
                    process = Multi_bruteForce_16(i, task_list[i][0], task_list[i][1], P_word, C_word, self.P_Queue,
                                                  self.F_Queue, self.Pg_Queue,self.read_lock,self.event,self.T_Queue)
                    process.start()
                    self.plainTextEdit_9.appendPlainText(f"Theard:{i}已启动")
                    self.processes.append(process)
            else:
                QMessageBox.warning(self, "警告",
                                    f"请输入正确的明密文和线程数量。\n明文长度:{len(P_word)}\n密文长度:{len(C_word)}")
        else:
            self.counter = 0
            self.threads = []
            self.plainTextEdit_9.setPlainText("")
            self.progressBar.setValue(0)
            P_word = self.plainTextEdit_8.toPlainText()
            C_word = self.plainTextEdit_7.toPlainText()
            Thread_num = self.lineEdit_4.text()
            if len(P_word) == len(C_word) == 8 and Thread_num != "":
                Thread_num = int(Thread_num)
                task_list = self.divide_task(Thread_num)

                self.timer = time.perf_counter()

                for i in range(Thread_num):
                    thread = Multi_bruteForce(i, task_list[i][0], task_list[i][1], P_word, C_word)
                    thread.finished_signal.connect(self.ShowFinishMsg)
                    thread.result_signal.connect(self.ShowResultMsg)
                    thread.start()
                    self.plainTextEdit_9.appendPlainText(f"Theard:{i}已启动")
                    self.threads.append(thread)
            else:
                QMessageBox.warning(self, "警告", "请输入正确的明密文和线程数量")

    def BitEncrption(self):
        if self.algorithm_flag:
            self.plainTextEdit_12.textChanged.disconnect()  # 串加密，密文
            Text = self.plainTextEdit_10.toPlainText()  # 串加密，明文
            if len(Text) % 16 == 0:
                binary_string = ""
                BinaryList = [int(x) for x in Text]
                for i in range(0, len(BinaryList), 16):
                    print(f"明文:{BinaryList[i:i + 16]}")
                    EncryptedList = self.Cipher_AES.Encryption(BinaryList[i:i + 16])

                    binary_string = binary_string + ''.join(map(str, EncryptedList))
                    print(f"秘文:{binary_string}")
                self.plainTextEdit_12.setPlainText(binary_string)
            self.plainTextEdit_12.textChanged.connect(self.BitDecrption)
        else:
            self.plainTextEdit_12.textChanged.disconnect()  # 串加密，密文
            Text = self.plainTextEdit_10.toPlainText()  # 串加密，明文
            if len(Text) % 8 == 0:
                binary_string = ""
                BinaryList = [int(x) for x in Text]
                for i in range(0, len(BinaryList), 8):
                    EncryptedList = self.Cipher.Encryption(BinaryList[i:i + 8])
                    binary_string = binary_string + ''.join(map(str, EncryptedList))
                self.plainTextEdit_12.setPlainText(binary_string)
            self.plainTextEdit_12.textChanged.connect(self.BitDecrption)

    def BitDecrption(self):
        if self.algorithm_flag:
            self.plainTextEdit_10.textChanged.disconnect()
            Text = self.plainTextEdit_12.toPlainText()
            if len(Text) % 16 == 0:
                binary_string = ""
                BinaryList = [int(x) for x in Text]
                for i in range(0, len(BinaryList), 16):
                    DecryptedList = self.Cipher_AES.Decryption(BinaryList[i:i + 16])
                    binary_string = binary_string + ''.join(map(str, DecryptedList))
                self.plainTextEdit_10.setPlainText(binary_string)
            self.plainTextEdit_10.textChanged.connect(self.BitEncrption)
        else:
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
        if self.algorithm_flag:
            self.plainTextEdit_6.textChanged.disconnect()
            character = ""
            Text = self.plainTextEdit_5.toPlainText()
            AsciiText = [ord(char) for char in Text]
            bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]
            # Ensure the length is even by adding a space if needed
            if len(bit_array_text) % 2 != 0:
                bit_array_text.append('0' * 8)  # Add a space (8 zeros) to make it even
            # Initialize an empty list to store the 16-bit binary strings
            bit_array_16bit = []
            for i in range(0, len(bit_array_text), 2):
                # Combine two 8-bit binary strings into one 16-bit string
                binary_word = bit_array_text[i] + bit_array_text[i + 1]
                bit_array_16bit.append(binary_word)
            for Binary_word in bit_array_16bit:
                EncryptedList = self.Cipher_AES.Encryption([int(x) for x in Binary_word])
                AsciiCode1 = int(''.join(map(str, EncryptedList[:8])), 2)
                AsciiCode2 = int(''.join(map(str, EncryptedList[8:])), 2)
                character = character + chr(AsciiCode1) + chr(AsciiCode2)
            self.plainTextEdit_6.setPlainText(character)
            self.plainTextEdit_6.textChanged.connect(self.Decryption_word)
        else:
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
        if self.algorithm_flag:
            self.plainTextEdit_5.textChanged.disconnect()
            character = ""
            Text = self.plainTextEdit_6.toPlainText()
            AsciiText = [ord(char) for char in Text]
            bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]

            if len(bit_array_text) % 2 != 0:
                bit_array_text.append('0' * 8)

            bit_array_16bit = []
            for i in range(0, len(bit_array_text), 2):
                binary_word = bit_array_text[i] + bit_array_text[i + 1]
                bit_array_16bit.append(binary_word)

            for Binary_word in bit_array_16bit:
                DecryptedList = self.Cipher_AES.Decryption([int(x) for x in Binary_word])
                AsciiCode1 = int(''.join(map(str, DecryptedList[:8])), 2)
                AsciiCode2 = int(''.join(map(str, DecryptedList[8:])), 2)
                character = character + chr(AsciiCode1) + chr(AsciiCode2)
            self.plainTextEdit_5.setPlainText(character)
            self.plainTextEdit_5.textChanged.connect(self.Decryption_word)
        else:
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
        if self.algorithm_flag:
            character = ""
            Text = self.plainTextEdit.toPlainText()
            AsciiText = [ord(char) for char in Text]
            bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]
            # Ensure the length is even by adding a space if needed
            if len(bit_array_text) % 2 != 0:
                bit_array_text.append('0' * 8)  # Add a space (8 zeros) to make it even
            # Initialize an empty list to store the 16-bit binary strings
            bit_array_16bit = []
            for i in range(0, len(bit_array_text), 2):
                # Combine two 8-bit binary strings into one 16-bit string
                binary_word = bit_array_text[i] + bit_array_text[i + 1]
                bit_array_16bit.append(binary_word)

            for Binary_word in bit_array_16bit:
                EncryptedList = self.Cipher_AES.Encryption([int(x) for x in Binary_word])
                AsciiCode1 = int(''.join(map(str, EncryptedList[:8])), 2)
                AsciiCode2 = int(''.join(map(str, EncryptedList[8:])), 2)
                character = character + chr(AsciiCode1) + chr(AsciiCode2)
            self.plainTextEdit.setPlainText(character)
        else:
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
        if self.algorithm_flag:
            character = ""
            Text = self.plainTextEdit.toPlainText()
            AsciiText = [ord(char) for char in Text]
            bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]

            if len(bit_array_text) % 2 != 0:
                bit_array_text.append('0' * 8)

            bit_array_16bit = []
            for i in range(0, len(bit_array_text), 2):
                binary_word = bit_array_text[i] + bit_array_text[i + 1]
                bit_array_16bit.append(binary_word)

            for Binary_word in bit_array_16bit:
                DecryptedList = self.Cipher_AES.Decryption([int(x) for x in Binary_word])
                AsciiCode1 = int(''.join(map(str, DecryptedList[:8])), 2)
                AsciiCode2 = int(''.join(map(str, DecryptedList[8:])), 2)
                character = character + chr(AsciiCode1) + chr(AsciiCode2)
            self.plainTextEdit.setPlainText(character)
        else:
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

    def divide_task_16bit(self, num_segments):
        start = 0
        end = 65535
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
            start_binary = format(current_start, '016b')
            end_binary = format(current_end, '016b')
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

    def binary_string_to_hex(self, binary_string):
        try:
            # 使用int将二进制字符串转换为整数
            binary_int = int(binary_string, 2)
            # 使用hex将整数转换为十六进制字符串，并去掉前缀'0x'
            hex_string = hex(binary_int)[2:]
            return hex_string.upper()  # 转换为大写字母的十六进制字符串
        except:
            return ""

    def SetEncryptionWays(self, text):
        if text == '双重加密':
            self.Encryption_flag = 0
            self.CleanPlainText()
            self.MulTextEditSetUnable()
        elif text == "三重加密":
            self.Encryption_flag = 1
            self.MulTextEditSetUnable()
            self.CleanPlainText()
        elif text == "双重加密(bit)":
            self.Encryption_flag = 2
            self.MulTextEditSetUnable()
            self.CleanPlainText()

    def CleanPlainText(self):
        self.plainTextEdit_13.textChanged.disconnect()
        self.plainTextEdit_14.textChanged.disconnect()
        self.plainTextEdit_14.setPlainText("")
        self.plainTextEdit_13.setPlainText("")
        self.plainTextEdit_13.textChanged.connect(self.MulEncryption)
        self.plainTextEdit_14.textChanged.connect(self.MulDecryption)

    def is_hex_string_hex_8(self, s):
        if not all(char in '0123456789ABCDEFabcdef' for char in s):
            return False
        if len(s) != 8:
            return False
        return True

    def is_hex_string_hex_12(self, s):
        # 检查字符串是否仅包含十六进制字符
        if not all(char in '0123456789ABCDEFabcdef' for char in s):
            return False
        # 检查字符串长度是否为16
        if len(s) != 12:
            return False
        # 如果通过了上述两个条件，字符串是有效的16位十六进制字符串
        return True

    def hex_string_to_binary_list(self, hex_string):
        # 使用int将十六进制字符串转换为整数
        hex_int = int(hex_string, 16)
        # 使用bin将整数转换为二进制字符串，并去掉前缀'0b'
        binary_string = bin(hex_int)[2:]
        # 将二进制字符串分割成一个二进制列表
        binary_list = [int(bit) for bit in binary_string]
        return binary_list

    def CBC_Encrption(self):
        self.plainTextEdit_16.textChanged.disconnect()
        character = ""
        Text = self.plainTextEdit_15.toPlainText()
        AsciiText = [ord(char) for char in Text]
        bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]
        # Ensure the length is even by adding a space if needed
        if len(bit_array_text) % 2 != 0:
            bit_array_text.append('0' * 8)  # Add a space (8 zeros) to make it even
        # Initialize an empty list to store the 16-bit binary strings
        bit_array_16bit = []
        for i in range(0, len(bit_array_text), 2):
            # Combine two 8-bit binary strings into one 16-bit string
            binary_word = bit_array_text[i] + bit_array_text[i + 1]
            bit_array_16bit.append(binary_word)

        EncryptedList = self.Cipher_AES.Encryption_CBC(
            [int(element) for sublist in bit_array_16bit for element in sublist])
        ascii_chars = []
        for i in range(0, len(EncryptedList), 8):
            byte = EncryptedList[i:i + 8]
            ascii_char = chr(int(''.join(map(str, byte)), 2))
            ascii_chars.append(ascii_char)
        result = ''.join(ascii_chars)
        self.plainTextEdit_16.setPlainText(result)
        self.plainTextEdit_16.textChanged.connect(self.CBC_Decrption)

    def CBC_Decrption(self):
        self.plainTextEdit_15.textChanged.disconnect()
        character = ""
        Text = self.plainTextEdit_16.toPlainText()
        AsciiText = [ord(char) for char in Text]
        bit_array_text = [bin(char)[2:].zfill(8) for char in AsciiText]

        if len(bit_array_text) % 2 != 0:
            bit_array_text.append('0' * 8)

        bit_array_16bit = []
        for i in range(0, len(bit_array_text), 2):
            binary_word = bit_array_text[i] + bit_array_text[i + 1]
            bit_array_16bit.append(binary_word)
        DecryptedList = self.Cipher_AES.Decryption_CBC(
            [int(element) for sublist in bit_array_16bit for element in sublist])
        ascii_chars = []
        for i in range(0, len(DecryptedList), 8):
            byte = DecryptedList[i:i + 8]
            ascii_char = chr(int(''.join(map(str, byte)), 2))
            ascii_chars.append(ascii_char)
        result = ''.join(ascii_chars)
        self.plainTextEdit_15.setPlainText(result)
        self.plainTextEdit_15.textChanged.connect(self.CBC_Encrption)

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
