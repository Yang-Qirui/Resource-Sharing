import re
from gen_decision import *
import matplotlib.pyplot as plt


def main():
    base_path = "../data/matrix"
    all_file = os.listdir(base_path)
    dirs = list(filter(lambda x: os.path.isdir(
        '/'.join([base_path, x])), all_file))
    data = []
    for dir in dirs:
        params = re.findall(r"\d+", dir)
        m = params[0]
        n = params[1]
        c = params[2]
        case = params[3]
        print(f"m = {m}, n = {n}, c = {c}")
        print(f"x = {n * (n - c) * m}")
        dir_path = '/'.join([base_path, dir])
        all_test_files = os.listdir(dir_path)
        t_start = time.time()
        scatter_x = []
        scatter_y = []
        for i in range(len(all_test_files)):
            test_path = '/'.join([dir_path, all_test_files[i]])
            start = time.time()
            gen_decision(test_path)
            end = time.time()
            # print(Fore.BLUE + f"SPEND: {end - start} second.\n")
            scatter_x.append(i)
            scatter_y.append(end-start)
        plt.scatter(scatter_x, scatter_y)
        plt.savefig(f"../data/figure/m_{m}-n_{n}-c_{c}-case{case}.png")
        plt.clf()
        t_end = time.time()
        print(Fore.MAGENTA +
              f"TOTAL: {t_end - t_start} second, Average: {(t_end - t_start) / len(all_test_files)}")
        data.append((n * (n - c) * m, t_end - t_start))
    data.sort(key=lambda x: x[0])
    x = [item[0] for item in data]
    y = [item[1] for item in data]
    f0 = np.polyfit(x, y, 1)
    p0 = np.poly1d(f0)
    f1 = np.polyfit(x, y, 2)
    p1 = np.poly1d(f1)
    f2 = np.polyfit(x, y, 3)
    p2 = np.poly1d(f2)
    plt.scatter(x, y, label="raw data")
    plt.plot(x, p0(x), label="rank 1")
    plt.plot(x, p1(x), label="rank 2")
    plt.plot(x, p2(x), label="rank 3")
    plt.legend()
    plt.savefig("../data/figure/total.png")


if __name__ == "__main__":
    main()
