import argparse
import os
import re
import time
from gen_decision import *
import matplotlib.pyplot as plt


def main(args):
    print(Fore.GREEN + f"Present algorithm used: {args.m}")
    base_path = "../data/matrix"
    all_file = os.listdir(base_path)
    dirs = list(filter(lambda x: os.path.isdir(
        '/'.join([base_path, x])), all_file))
    data = []
    for dir in dirs:
        params = re.findall(r"\d+", dir)
        case = int(params[0])
        m = int(params[1])
        n = int(params[2])
        c = int(params[3])
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
            cost, decision = gen_decision(test_path, args)
            # print(decision)
            log_name = ''.join([all_test_files[i].split('.')[0], '.log'])
            log_dir = f'../data/reports/{args.m.lower()}/case{case}-m_{m}-n_{n}-c_{c}'
            if args.r:
                log_dir += '/random'
            else:
                log_dir += '/enum'
            if args.v:
                log_dir += '/count_visit'
            else:
                log_dir += '/cost_only'
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            f = open(
                f'{log_dir}/{log_name}', 'w')
            f.write(str(cost) + '\n')
            f.write(str(decision))
            end = time.time()
            scatter_x.append(i)
            scatter_y.append(end-start)
        plt.scatter(scatter_x, scatter_y)
        figure_dir = f"../data/figure/{args.m.lower()}"
        figure_name = f"case{case}-m_{m}-n_{n}-c_{c}-{args.m.lower()}"
        if args.r:
            figure_name += "-random"
        if args.v:
            figure_name += "-count_visit"
        figure_name += '.png'
        if not os.path.exists(figure_dir):
            os.makedirs(figure_dir)
        plt.savefig(
            f'{figure_dir}/{figure_name}')
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
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-m', help='Resource sharing method. [ENUM, RANDOM, GREEDY, MCTS]', default='RANDOM')
    arg_parser.add_argument('-t', help='Time limit for MCTS', default=1)
    arg_parser.add_argument(
        '-r', help='Random exploration for MCTS', action='store_true')
    arg_parser.add_argument(
        '-v', help='Add visit time into MCTS make_decision consideration', action='store_true')

    args = arg_parser.parse_args()
    main(args)
