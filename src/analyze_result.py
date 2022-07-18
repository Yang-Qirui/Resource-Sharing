import os
import random
import re

from matplotlib import pyplot as plt


def main():
    random_path = "../data/reports/random"
    all_file = os.listdir(random_path)
    dirs = list(filter(lambda x: os.path.isdir(
        '/'.join([random_path, x])), all_file))
    x = []
    y0 = []
    y1 = []
    y2 = []
    y3 = []
    y4 = []
    y5 = []

    for dir in dirs:
        params = re.findall(r"\d+", dir)
        m = int(params[1])
        n = int(params[2])
        c = int(params[3])
        x.append(m * n * (n - c))

        random_path = "../data/reports/random"
        greedy_path = "../data/reports/greedy"
        enum_path = "../data/reports/enum"
        mcts_path = "../data/reports/mcts"

        enum_dir_path = '/'.join([enum_path, dir])
        random_dir_path = '/'.join([random_path, dir])
        greedy_dir_path = '/'.join([greedy_path, dir])
        mcts_dir_enum_cost_path = '/'.join([mcts_path,
                                           dir, 'enum', 'cost_only'])
        mcts_dir_enum_visit_path = '/'.join([mcts_path,
                                             dir, 'enum', 'count_visit'])
        mcts_dir_random_cost_path = '/'.join([mcts_path,
                                              dir, 'random', 'cost_only'])
        mcts_dir_random_visit_path = '/'.join([mcts_path,
                                              dir, 'random', 'count_visit'])

        all_file = os.listdir(random_dir_path)

        enum_tot = 0
        random_tot = 0
        greedy_tot = 0
        mcts_e_c_tot = 0
        mcts_e_v_tot = 0
        mcts_r_c_tot = 0
        mcts_r_v_tot = 0

        for file in all_file:
            enum_file_path = '/'.join([enum_dir_path, file])
            random_file_path = '/'.join([random_dir_path, file])
            greedy_file_path = '/'.join([greedy_dir_path, file])
            mcts_file_enum_cost_path = '/'.join(
                [mcts_dir_enum_cost_path, file])
            mcts_file_enum_visit_path = '/'.join(
                [mcts_dir_enum_visit_path, file])
            mcts_file_random_cost_path = '/'.join(
                [mcts_dir_random_cost_path, file])
            mcts_file_random_visit_path = '/'.join(
                [mcts_dir_random_visit_path, file])

            ef = open(enum_file_path, 'r')
            rf = open(random_file_path, 'r')
            gf = open(greedy_file_path, 'r')
            mf_e_c = open(mcts_file_enum_cost_path, 'r')
            mf_e_v = open(mcts_file_enum_visit_path, 'r')
            mf_r_c = open(mcts_file_random_cost_path, 'r')
            mf_r_v = open(mcts_file_random_visit_path, 'r')

            e_cost = int(ef.readline())
            r_cost = int(rf.readline())
            g_cost = int(gf.readline())
            mf_e_c_cost = int(mf_e_c.readline())
            mf_e_v_cost = int(mf_e_v.readline())
            mf_r_c_cost = int(mf_r_c.readline())
            mf_r_v_cost = int(mf_r_v.readline())

            enum_tot += e_cost
            random_tot += r_cost
            greedy_tot += g_cost
            mcts_e_c_tot += mf_e_c_cost
            mcts_e_v_tot += mf_e_v_cost
            mcts_r_c_tot += mf_r_c_cost
            mcts_r_v_tot += mf_r_v_cost

            # enum.append(enum_tot)
            # random.append(random_tot)

            # if r_cost < e_cost:
            #     print(enum_file_path, random_file_path)
            #     exit(0)
            # if g_cost < e_cost:
            #     print(enum_file_path, greedy_file_path)
            #     exit(1)
            # if mf_e_c_cost < e_cost:
            #     print(mcts_file_enum_cost_path, enum_file_path)
            #     exit(2)
            # if mf_e_v_cost < e_cost:
            #     print(mcts_file_enum_visit_path, enum_file_path)
            #     exit(3)
            # if mf_r_c_cost < e_cost:
            #     print(mcts_dir_random_cost_path, enum_file_path)
            #     exit(4)
            # if mf_r_v_cost < e_cost:
            #     print(mcts_dir_random_visit_path, enum_file_path)
            #     exit(5)

        y0.append(random_tot - enum_tot)
        y1.append(greedy_tot - enum_tot)
        y2.append(mcts_e_c_tot - enum_tot)
        y3.append(mcts_e_v_tot - enum_tot)
        y4.append(mcts_r_c_tot - enum_tot)
        y5.append(mcts_r_v_tot - enum_tot)

    plt.title("Enum-Random")
    plt.scatter(x, y0)
    plt.savefig(
        "../data/figure/comparision_e_r.png")
    plt.clf()
    plt.title("Enum-Greedy")
    plt.scatter(x, y1)
    plt.savefig(
        "../data/figure/comparision_e_g.png")
    plt.clf()
    plt.title("Enum-MCTS_c")
    plt.scatter(x, y2)
    plt.savefig(
        "../data/figure/comparision_e_m_enum_cost-only.png"
    )
    plt.clf()
    plt.title("Enum-MCTS_v")
    plt.scatter(x, y3)
    plt.savefig(
        "../data/figure/comparision_e_m_enum_count-visit.png"
    )
    plt.clf()
    plt.title("Enum-MCTS_r_c")
    plt.scatter(x, y4)
    plt.savefig(
        "../data/figure/comparision_e_m_random_cost-only.png"
    )
    plt.clf()
    plt.title("Enum-MCTS_r_v")
    plt.scatter(x, y5)
    plt.savefig(
        "../data/figure/comparision_e_m_random_count-visit.png"
    )


if __name__ == "__main__":
    main()
