from functools import reduce
import os
import random

test_cases = 30
random_times = 200
setting = []
m_max = 7
n_max = 7
max_cases = (m_max - 1) * reduce(lambda x, y: x + y, range(1, n_max - 1))


def gen_test():
    for i in range(test_cases):
        m = n = c = -1
        while not(m > 0 and n > 0 and c > 0 and (m, n, c) not in setting):
            m = random.randint(2, m_max)
            n = random.randint(3, n_max)
            c = random.randint(2, n - 1)

            if len(setting) >= max_cases:
                if i < test_cases - 1:
                    print(
                        f"There can't be {test_cases} combination for m_max = {m_max}, n_max = {n_max}, only generate {max_cases * random_times} cases.")
                return
        setting.append((m, n, c))
        path = f"../data/matrix/case{i}-m_{m}-n_{n}-c_{c}"
        for id in range(random_times):
            if not os.path.exists(path):
                os.makedirs(path)
            with open(f'{path}/s-matrix-{id}.txt', 'w') as f:
                for _ in range(m):
                    tag = random.sample(range(0, n), c)
                    tmp = ''
                    for i in range(n):
                        if i in tag:
                            tmp += '1'
                        else:
                            tmp += '0'
                    f.write(tmp + '\n')
                f.close()


if __name__ == "__main__":
    gen_test()
