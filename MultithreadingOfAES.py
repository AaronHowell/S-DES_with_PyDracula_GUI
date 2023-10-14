import multiprocessing
import pickle
import random
import time

from PyQt5.QtCore import QThread, pyqtSignal
from S_AES import *

from multiprocessing import *

class Multi_bruteForce_16(Process):
    def __init__(self, id, start_point, end_point, P, C,Queue,finshQueue,Progress,lock,event,T_Queue):
        super().__init__()
        self.id = id
        self.begin = [int(x) for x in start_point]
        self.end = [int(x) for x in end_point]
        self.P_list = [int(x) for x in P]
        self.C_list = [int(x) for x in C]
        self.Cipher_E = S_AES()
        self.Cipher_D = S_AES()
        self.Queue=Queue
        self.finshQueue = finshQueue
        self.PgQueue=Progress
        self.En_list=[]
        self.De_list=[]
        self.lock=lock
        self.event:multiprocessing.Event=event
        self.Trans=T_Queue
        self.dic=None

    def run(self):
        first_time = True
        begin_copy=self.begin

        while first_time or self.begin != self.end:
            first_time=False
            self.Cipher_E.SetKey(self.begin)
            self.Cipher_D.SetKey(self.begin)
            En=self.Cipher_E.Encryption_Attack(self.P_list)
            De=self.Cipher_D.Decryption_Attack(self.C_list)
            En_str=''.join(''.join(str(bit) for bit in sublist) for sublist in En)

            De_str=''.join(''.join(str(bit) for bit in sublist) for sublist in De)
            self.En_list.append([self.Cipher_E.GetKey(),En_str])
            self.De_list.append([self.Cipher_D.GetKey(), De_str])
            self.begin = self.binary_addition(self.begin, [1])


        with self.lock:
            with open('En.pkl', 'ab') as file1:
                with open('De.pkl', 'ab') as file2:
                    pickle.dump(self.En_list,file1)
                    pickle.dump(self.De_list,file2)

        self.finshQueue.put(self.id)
        self.event.wait()
        self.dic=self.Trans.get()

        with self.lock:
            all_data2 = []
            # 打开.pkl文件以读取数据
            with open('De.pkl', 'rb') as file2:
                while True:
                    try:
                        data2 = pickle.load(file2)
                        all_data2.append(data2)
                    except EOFError:
                        break
            # 打印所有加载的数据
            self.De_list=[]
            for data in all_data2:
                self.De_list += data
        sorted_array = sorted(self.De_list, key=lambda x: x[1])  # 先按第二个元素排序
        for key, value in self.dic.items():
            find=self.binary_search_tuples(sorted_array,value)
            self.PgQueue.put(1)
            for i in find:
                self.Queue.put([self.id, key + i[0]])






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

    def binary_search_tuples(self,data, target_value):
        left, right = 0, len(data) - 1
        matching_tuples = []

        while left <= right:
            mid = (left + right) // 2
            if data[mid][1] == target_value:
                matching_tuples.append(data[mid])
                # 继续查找左边的匹配项
                left = mid + 1
            elif data[mid][1] < target_value:
                left = mid + 1
            else:
                right = mid - 1

        return matching_tuples
if __name__=='__main__':

    import pickle

    file_path1 = 'En.pkl'
    file_path2 = 'De.pkl'

    loaded_data1 = []
    loaded_data2 = []

    # 读取第一个.pkl文件的前两行数据
    with open(file_path1, 'rb') as file1:
        data1 = pickle.load(file1)
        print(data1)
        print(len(data1))

    # 存储所有数据的列表
    all_data2 = []

    # 打开.pkl文件以读取数据
    with open(file_path2, 'rb') as file2:
        while True:
            try:
                data2 = pickle.load(file2)
                all_data2.append(data2)
            except EOFError:
                break

    # 打印所有加载的数据
    for data in all_data2:
        loaded_data2 +=data
    print(len(loaded_data2))


