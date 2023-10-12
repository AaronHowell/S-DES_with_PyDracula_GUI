class GF:
    primitive_polynomial_dict = {4: 0b10011,  # x**4 + x + 1
                                 8: (1 << 8) + 0b11101,  # x**8 + x**4 + x**3 + x**2 + 1
                                 16: (1 << 16) + (1 << 12) + 0b1011,  # x**16 + x**12 + x**3 + x + 1
                                 32: (1 << 32) + (1 << 22) + 0b111,  # x**32 + x**22 + x**2 + x + 1
                                 64: (1 << 64) + 0b11011  # x**64 + x**4 + x**3 + x + 1
                                 }

    def __init__(self, w):
        self.w = w
        self.total = (1 << self.w)-1
        self.gflog = []
        self.gfilog = [1]  # g(0) = 1
        self.make_gf_dict(self.w, self.gflog, self.gfilog)

    def make_gf_dict(self, w, gflog, gfilog):
        gf_element_total_number = 1 << w
        primitive_polynomial = self.primitive_polynomial_dict[w]
        for i in range(1, gf_element_total_number - 1):
            temp = gfilog[i - 1] << 1  # g(i) = g(i-1) * 2
            if temp & gf_element_total_number:  # 判断溢出
                temp ^= primitive_polynomial  # 异或本原多项式
            gfilog.append(temp)
        assert (gfilog[gf_element_total_number - 2] << 1) ^ primitive_polynomial
        gfilog.append(None)
        for i in range(gf_element_total_number):
            gflog.append(None)
        for i in range(0, gf_element_total_number - 1):
            gflog[gfilog[i]] = i

    def add(self, a, b):
        return (a ^ b)

    def sub(self, a, b):
        return (a ^ b)

    def mul(self, a, b):
        if a == 0 or b == 0:
            return 0
        return self.gfilog[(self.gflog[a] + self.gflog[b]) % self.total]

    def div(self, a, b):
        return self.gfilog[(self.gflog[a] - self.gflog[b] + self.total) % self.total]


if __name__ == "__main__":
    # 使用示例
    gf = GF(4)
    import random

    t = 0
    while t <= 20:
        a = random.randint(1, 15)
        b = random.randint(1, 15)
        c = gf.add(a, b)
        d = gf.mul(a, b)
        print('%d + %d = %d' % (a, b, c))
        print('%d - %d = %d' % (c, a, gf.sub(c, a)))
        print('%d * %d = %d' % (a, b, d))
        print('%d / %d = %d' % (d, a, gf.div(d, a)))
        print()
        t += 1
