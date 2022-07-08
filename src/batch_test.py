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
        m = int(params[0])
        n = int(params[1])
        c = int(params[2])
        case = int(params[3])
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
            cost, columns = gen_decision(test_path)
            if cost > n - 1:
                print(Fore.RED + f"Exceed {n-1} operations")
                # exit(4)
            print(Fore.GREEN + f'{cost},{columns}')
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
        data.append((n, c, t_end - t_start))
    data.sort(key=lambda x: x[0])
    n = [item[0] for item in data]
    c = [item[1] for item in data]
    y = [item[2] for item in data]
    fn0 = np.polyfit(n, y, 1)
    fc0 = np.polyfit(c, y, 1)
    pn0 = np.poly1d(fn0)
    pc0 = np.poly1d(fc0)
    fn1 = np.polyfit(n, y, 2)
    fc1 = np.polyfit(c, y, 2)
    pn1 = np.poly1d(fn1)
    pc1 = np.poly1d(fc1)
    fn2 = np.polyfit(n, y, 3)
    fc2 = np.polyfit(c, y, 3)
    pn2 = np.poly1d(fn2)
    pc2 = np.poly1d(fc2)
    plt.scatter(n, y, label="raw n data")
    plt.plot(n, pn0(n), label="rank 1")
    plt.plot(n, pn1(n), label="rank 2")
    plt.plot(n, pn2(n), label="rank 3")
    plt.legend()
    plt.savefig("../data/figure/total_n.png")
    plt.scatter(c, y, label="raw c data")
    plt.plot(c, pc0(c), label="rank 1")
    plt.plot(c, pc1(c), label="rank 2")
    plt.plot(c, pc2(c), label="rank 3")
    plt.legend()
    plt.savefig("../data/figure/total_c.png")


if __name__ == "__main__":
    main()
