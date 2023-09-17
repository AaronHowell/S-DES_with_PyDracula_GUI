from PyQt5.QtCore import QThread, pyqtSignal
import time

from S_DES import S_DES


class Multi_bruteForce(QThread):
    finished_signal = pyqtSignal(int)
    result_signal=pyqtSignal(list)
    def __init__(self, id,start_point, end_point,P,C):
        super().__init__()
        self.id=id
        self.begin=[int(x) for x in start_point]
        self.end=[int(x) for x in end_point]
        self.P_list=[int(x) for x in P]
        self.C_list = [int(x) for x in C]
        self.Cipher=S_DES()


    def run(self):
        first_time = True

        while first_time or self.begin!=self.end:
            first_time = False
            self.Cipher.SetKey(self.begin)

            if self.C_list==self.Cipher.Encryption(self.P_list):
                print(f"发送密钥{self.id,self.Cipher.GetKey()}")

                self.result_signal.emit([self.id,self.Cipher.GetKey()])
                print("完成发送")
            self.begin=self.binary_addition(self.begin,[1])
        self.finished_signal.emit(self.id)

    def binary_addition(self,bin_list1, bin_list2):
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