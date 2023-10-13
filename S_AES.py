import gf


class S_AES():
    K = []
    w = [[], [], [], [], [], []]
    NS = [[9, 4, 0xA, 0xB],
          [0xD, 1, 8, 5],
          [6, 2, 0, 3],
          [0xC, 0xE, 0xF, 7]]

    INS = [[0xA, 5, 9, 0xB],
           [1, 7, 8, 0xF],
           [6, 0, 2, 3],
           [0xC, 4, 0xD, 0xE]]

    RC = [[1, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 1, 0, 0, 0, 0]]
    MC = [[1, 4],
          [4, 1]]
    IMC = [[9, 2],
           [2, 9]]
    IV = []

    def SetIV(self, InputList: list):
        self.IV = InputList

    def GetIV(self):
        return ''.join(map(str, self.IV))

    def __init__(self):
        self.gf = gf.GF(4)

    def Encryption(self, InputBits):
        """应该给出16bit的明文。进行加密操作"""
        Pre_Trans = self.XOR(InputBits, self.w[0] + self.w[1])  # 加轮变换
        Sub_Trans = self.Nibble_Substitution(Pre_Trans, self.NS)  # 半字节替换
        Shift_Trans = self.ShiftRows(Sub_Trans)  # 行位移
        MC_Trans = self.MixColumns(Shift_Trans, self.MC)  # 列混淆
        Pre_Trans_2 = self.XOR(MC_Trans, self.w[2] + self.w[3])
        Sub_Trans_2 = self.Nibble_Substitution(Pre_Trans_2, self.NS)  # 半字节替换
        Shift_Trans_2 = self.ShiftRows(Sub_Trans_2)  # 行位移
        Pre_Trans_3 = self.XOR(Shift_Trans_2, self.w[4] + self.w[5])
        return Pre_Trans_3

    def Decryption(self, InputBits):
        """应该给出16bit的明文。进行加密操作"""
        Pre_Trans = self.XOR(InputBits, self.w[4] + self.w[5])  # 加轮变换
        Shift_Trans = self.ShiftRows(Pre_Trans)  # 逆行位移，在该情景下，逆行变换和行变换相同
        Sub_Trans = self.Nibble_Substitution(Shift_Trans, self.INS)  # 逆半字节替换
        Pre_Trans_2 = self.XOR(Sub_Trans, self.w[2] + self.w[3])
        MC_Trans = self.MixColumns(Pre_Trans_2, self.IMC)  # 逆列混淆
        Shift_Trans_2 = self.ShiftRows(MC_Trans)  # 逆行位移
        Sub_Trans_2 = self.Nibble_Substitution(Shift_Trans_2, self.INS)  # 逆半字节替换
        Pre_Trans_3 = self.XOR(Sub_Trans_2, self.w[0] + self.w[1])  # 加轮变换
        return Pre_Trans_3

    def Nibble_Substitution(self, InputBits, SubstitutionBox):
        """半字节替换函数，给定16bit以及替换盒子，返回16bit列表"""
        S00 = InputBits[0:4]
        S10 = InputBits[4:8]
        S01 = InputBits[8:12]
        S11 = InputBits[12:16]
        S_S00 = self.SBox(S00, SubstitutionBox)
        S_S10 = self.SBox(S10, SubstitutionBox)
        S_S01 = self.SBox(S01, SubstitutionBox)
        S_S11 = self.SBox(S11, SubstitutionBox)
        return S_S00 + S_S10 + S_S01 + S_S11

    def ShiftRows(self, InputBits):
        """行位移，把第二行的进行半字节循环位移"""
        S00 = InputBits[0:4]
        S10 = InputBits[4:8]
        S01 = InputBits[8:12]
        S11 = InputBits[12:16]
        return S00 + S11 + S01 + S10

    def MixColumns(self, InputBits, Matrix):
        S00 = InputBits[0:4]
        S10 = InputBits[4:8]
        S01 = InputBits[8:12]
        S11 = InputBits[12:16]
        S00 = self.BinaryList2Decimal(S00)
        S10 = self.BinaryList2Decimal(S10)
        S01 = self.BinaryList2Decimal(S01)
        S11 = self.BinaryList2Decimal(S11)
        Dec_MC_Trans = self.matrix_multiply(Matrix, [[S00, S01],
                                                     [S10, S11]])
        MC_Trans = []
        for i in range(len(Dec_MC_Trans)):
            for j in range(len(Dec_MC_Trans)):
                MC_Trans.append(self.Decimal2BinaryList(Dec_MC_Trans[j][i]))

        MC_Trans = [element for row in MC_Trans for element in row]

        return MC_Trans

    def matrix_multiply(self, A, B):
        rows_A = len(A)
        cols_A = len(A[0])
        rows_B = len(B)
        cols_B = len(B[0])
        C = [[0] * cols_B for _ in range(rows_A)]
        for i in range(rows_A):
            for j in range(cols_B):
                for k in range(cols_A):
                    C[i][j] = self.gf.add(C[i][j], self.gf.mul(A[i][k], B[k][j]))
        return C

    def XOR(self, list1, list2):
        return [bit1 ^ bit2 for bit1, bit2 in zip(list1, list2)]

    def SetKey(self, InputBits: list):
        """密钥设定"""
        self.K = InputBits
        self.w[0] = self.K[0:8]
        self.w[1] = self.K[8:16]  # 左闭右开
        self.w[2] = self.XOR(self.w[0], self.gFunction(self.w[1], 1))
        self.w[3] = self.XOR(self.w[2], self.w[1])
        self.w[4] = self.XOR(self.w[2], self.gFunction(self.w[3], 2))
        self.w[5] = self.XOR(self.w[4], self.w[3])

    def gFunction(self, InputBits: list, index):
        """给定一个8bit，返回其g变换结果，包含S变换和加轮密钥"""
        N1 = InputBits[-4:]
        N0 = InputBits[:4]
        _N1 = self.SBox(N1, self.NS)
        _N0 = self.SBox(N0, self.NS)
        return self.XOR(_N1 + _N0, self.RC[index - 1])

    def BinaryList2Decimal(self, InputBits: list):
        BinaryString = ''.join(str(bit) for bit in InputBits)
        Decimal = int(BinaryString, 2)
        return Decimal

    def Decimal2BinaryList(self, Number: int):
        BinaryString = bin(Number)
        BinaryList = [int(x) for x in BinaryString[2:]]
        while len(BinaryList) < 4:
            BinaryList.insert(0, 0)
        return BinaryList

    def SBox(self, InputBits, SubstitutionBox):
        # 混淆盒，需要用列表的形式传入4bit数据，并且给定二维数组混淆表
        RowBinary = [InputBits[0], InputBits[1]]
        ColumnBinary = [InputBits[2], InputBits[3]]
        Row = self.BinaryList2Decimal(RowBinary)
        Column = self.BinaryList2Decimal(ColumnBinary)
        return self.Decimal2BinaryList(SubstitutionBox[Row][Column])

    def GetKey(self):
        return ''.join(map(str, self.K))
    def Encryption_CBC(self,InputList:list):
        """输入一个完整字符串的Bit进行加密"""
        if len(InputList)==0:
            return []
        result=[]
        P = InputList[:16]
        print(P)

        Last_Vector = self.Encryption(self.XOR(self.IV, P))
        result.append([x for x in Last_Vector])

        for i in range(16,len(InputList),16):
            P=InputList[i:i+16]
            Last_Vector = self.Encryption(self.XOR(Last_Vector, P))
            result.append([x for x in Last_Vector])

        flattened_result = [element for sublist in result for element in sublist]
        return flattened_result

    def Decryption_CBC(self,InputList:list):
        """输入一个完整加密字符串的Bit进行解密"""
        if len(InputList)==0:
            return []
        result = []
        C = InputList[:16]
        Last_Vector=self.Decryption(C)
        P=self.XOR(self.IV, Last_Vector)

        result.append([x for x in P])

        for i in range(16, len(InputList), 16):
            C = InputList[i:i+16]
            Last_Vector = self.Decryption(C)
            P = self.XOR(InputList[i-16:i], Last_Vector)
            result.append([x for x in P])

        flattened_result = [element for sublist in result for element in sublist]
        return flattened_result

    def Encryption_Attack(self,InputList:list):
        result=[]
        for i in range(0,len(InputList),16):
            P=InputList[i:i+16]
            En = self.Encryption(P)
            result.append(En)
        return result
    def Decryption_Attack(self,InputList:list):
        result=[]
        for i in range(0,len(InputList),16):
            C=InputList[i:i+16]
            De = self.Decryption(C)
            result.append(De)
        return result

if __name__ == "__main__":
    a_E = S_AES()
    a_D = S_AES()
    text_key = [0, 0, 0, 0]

    matrix = [a_E.Decimal2BinaryList(x) for x in text_key]
    row_vector = [element for row in matrix for element in row]

    a_E.SetKey(row_vector)

    text_key_b = [7, 2, 1, 8]
    matrix = [a_E.Decimal2BinaryList(x) for x in text_key_b]
    row_vector = [element for row in matrix for element in row]
    a_D.SetKey(row_vector)

    P_list = [1, 1, 1, 1, 1, 1, 1, 1,
              1, 1, 1, 1, 1, 1, 1, 1]

    C_list = [1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1]

    binary_list = [1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1,
                   1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1,
                   0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1,
                   0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1,
                   0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1,
                   1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0,
                   0, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0,
                   1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0]

    a_D.SetIV(P_list)
    print(a_D.Decryption_CBC(a_D.Encryption_CBC(binary_list)))
    # print(a_D.Decryption(C_list))
    # print(a_E.Encryption(P_list))
    # key_list =       [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1]
    # plaintext_list = [0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0]
    # plaintext_list2 = [0,1,1,0,1,0,1,1,1,0,1,0,0,0,1,1]
    #
    #
    # g=gf.GF(4)
    # print(g.mul(4,7))
    # print(g.add(15,8))
    # a.SetKey(row_vector)
    # print(plaintext_list2)
    # #print(a.Encryption(plaintext_list))
    # print(a.Decryption(a.Encryption(plaintext_list2)))
    # print(a.Decryption(a.Encryption([1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0])))
