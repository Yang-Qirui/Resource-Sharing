import os
import re

from matplotlib import pyplot as plt


def main():
    enum_path = "../data/reports/enum"
    all_file = os.listdir(enum_path)
    dirs = list(filter(lambda x: os.path.isdir(
        '/'.join([enum_path, x])), all_file))
    x = []
    y0 = []
    y1 = []
    # enum = []
    # random = []
    for dir in dirs:
        params = re.findall(r"\d+", dir)
        m = int(params[1])
        n = int(params[2])
        c = int(params[3])
        x.append(m * n * (n - c))
        random_path = "../data/reports/random"
        greedy_path = "../data/reports/greedy"
        enum_dir_path = '/'.join([enum_path, dir])
        random_dir_path = '/'.join([random_path, dir])
        greedy_dir_path = '/'.join([greedy_path, dir])
        all_enum_file = os.listdir(enum_dir_path)
        enum_tot = 0
        random_tot = 0
        greedy_tot = 0
        for file in all_enum_file:
            enum_file_path = '/'.join([enum_dir_path, file])
            random_file_path = '/'.join([random_dir_path, file])
            greedy_file_path = '/'.join([greedy_dir_path, file])
            ef = open(enum_file_path, 'r')
            rf = open(random_file_path, 'r')
            gf = open(greedy_file_path, 'r')
            e_cost = int(ef.readline())
            r_cost = int(rf.readline())
            g_cost = int(gf.readline())
            enum_tot += e_cost
            random_tot += r_cost
            greedy_tot += g_cost
        # enum.append(enum_tot)
        # random.append(random_tot)
            if r_cost < e_cost:
                print(enum_file_path, random_file_path)
                exit(0)
            if g_cost < e_cost:
                print(enum_file_path, greedy_file_path)
                exit(0)
        y0.append(random_tot - enum_tot)
        y1.append(greedy_tot - enum_tot)
    # plt.scatter(x, enum)
    # plt.scatter(x, random)
    plt.scatter(x, y0)
    plt.savefig(
        f"../data/figure/comparision_e_r.png")
    plt.clf()
    plt.scatter(x, y1)
    plt.savefig(
        f"../data/figure/comparision_e_g.png")


if __name__ == "__main__":
    main()
