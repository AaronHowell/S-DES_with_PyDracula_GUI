import random
import time

from PyQt5.QtCore import QThread, pyqtSignal
from S_AES import *



class Multi_bruteForce_16(QThread):
    finished_signal = pyqtSignal(int)
    result_signal = pyqtSignal(list)
    process_signal= pyqtSignal(int)

    def __init__(self, id, start_point, end_point, P, C):
        super().__init__()
        self.id = id
        self.begin = [int(x) for x in start_point]
        self.end = [int(x) for x in end_point]
        self.P_list = [int(x) for x in P]
        self.C_list = [int(x) for x in C]
        self.Cipher_E = S_AES()
        self.Cipher_D = S_AES()

    def run(self):
        first_time = True
        #time.sleep(random.randint(0, 50) / 10.0)  #如果你想看到进度条一点点往上涨的话，你可以用这个模拟一下，破解太快了
        while first_time or self.begin != self.end:
            first_time = False
            self.Cipher_E.SetKey(self.begin)
            temp=[0,0,0,0,0,0,0,0,
                  0,0,0,0,0,0,0,0]
            while first_time or temp!=[1,1,1,1,1,1,1,1
                        ,1,1,1,1,1,1,1,1]:
                self.Cipher_D.SetKey(temp)
                if self.Cipher_E.Encryption_Attack(self.P_list)==self.Cipher_D.Decryption_Attack(self.C_list):
                    print(f"发送密钥{self.id, self.Cipher_E.GetKey()+self.Cipher_D.GetKey()}")
                    self.result_signal.emit([self.id, self.Cipher_E.GetKey()+self.Cipher_D.GetKey()])
                    print("完成发送")
                temp=self.binary_addition(temp,[1])
            self.begin = self.binary_addition(self.begin, [1])

            self.process_signal.emit(1)

        self.finished_signal.emit(self.id)

    def BinaryList2Decimal(self, InputBits: list):
        BinaryString = ''.join(str(bit) for bit in InputBits)
        Decimal = int(BinaryString, 2)
        return Decimal

    def binary_addition(self, bin_list1, bin_list2):
        max_len = max(len(bin_list1), len(bin_list2))
        bin_list1 = [0] * (max_len - len(bin_list1)) + bin_list1
        bin_list2 = [0] * (max_len - len(bin_list2)) + bin_list2

        result = []
        carry = 0

        for i in range(max_len - 1, -1, -1):
            bit1 = bin_list1[i]
            bit2 = bin_list2[i]

            # 计算当前位的和，考虑进位
            bit_sum = bit1 + bit2 + carry
            result.insert(0, bit_sum % 2)
            carry = bit_sum // 2

        if carry:
            result.insert(0, 1)

        return result
