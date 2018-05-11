#coding:utf-8

from graphics import *
from math import *

import numpy as np
import datetime

GRID_WIDTH = 40

COLUMN = 15
ROW = 15

list1 = []  # AI
list2 = []  # human
list3 = []  # all

list_all = []        # 整个棋盘的点
next_point = [0, 0]  # AI下一步最应该下的位置

ratio = 1  # 进攻的系数：大于1 进攻型，小于1防守型
DEPTH = 3  # 搜索深度：只能是单数！！如果是双数，评估函数评估的的是自己多少步之后的自己得分的最大值，并不意味着是最好的棋，评估函数的问题


# 棋型的评估分数
shape_score = [(50, (0, 1, 1, 0, 0)),
               (50, (0, 0, 1, 1, 0)),
               (200, (1, 1, 0, 1, 0)),
               (500, (0, 0, 1, 1, 1)),
               (500, (1, 1, 1, 0, 0)),
               (5000, (0, 1, 1, 1, 0)),
               (5000, (0, 1, 0, 1, 1, 0)),
               (5000, (0, 1, 1, 0, 1, 0)),
               (5000, (1, 1, 1, 0, 1)),
               (5000, (1, 1, 0, 1, 1)),
               (5000, (1, 0, 1, 1, 1)),
               (5000, (1, 1, 1, 1, 0)),
               (5000, (0, 1, 1, 1, 1)),
               (50000, (0, 1, 1, 1, 1, 0)),
               (99999999, (1, 1, 1, 1, 1))]


def ai():
    global cut_count      # 统计剪枝次数
    global search_count   # 统计搜索次数
    cut_count = 0
    search_count = 0
    negamax(True, DEPTH, -99999999, 99999999)
    print("本次共剪枝次数：" + str(cut_count))
    print("本次共搜索次数：" + str(search_count))
    print("请黑子下~~~")

    return next_point[0], next_point[1]


# 负值极大算法搜索 alpha + beta 剪枝，alpha为下界，beta为上界
def negamax(is_ai, depth, alpha, beta):
    # 游戏是否结束 | | 探索的递归深度是否到边界
    if game_win(list1) or game_win(list2) or depth == 0:
        return evaluation(is_ai)

    # set.difference获得差集，存在于第一个（list_all)，但是不存在于第二个集合（list3）
    # 获得棋盘上还没有落子的点
    blank_list = list(set(list_all).difference(set(list3)))

    # 搜索顺序排序，将最后落子的附近的点移到了前面，提高剪枝效率
    order(blank_list)

    # 遍历每一个候选步
    for next_step in blank_list:
        # 每遍历一个侯选步，搜索次数加1
        global search_count
        search_count += 1

        # 如果要评估的位置没有相邻的子（说明是孤立的一步），则不去评估，减少计算
        if not has_neightnor(next_step):
            continue

        # 先将这一步加入到list当中，以便于计算下一步的收益
        if is_ai:
            list1.append(next_step)
        else:
            list2.append(next_step)
        list3.append(next_step)

        # 估算下一步human落子位置的分数，对于对手来说，极大极小值是相反的
        value = -negamax(not is_ai, depth - 1, -beta, -alpha)

        # 将刚加入的那一步去掉
        if is_ai:
            list1.remove(next_step)
        else:
            list2.remove(next_step)
        list3.remove(next_step)

        if value > alpha:
            #print(str(value) + "alpha:" + str(alpha) + "beta:" + str(beta))
            #print(list3)
            if depth == DEPTH:
                next_point[0] = next_step[0]
                next_point[1] = next_step[1]
            # alpha + beta剪枝点
            if value >= beta:
                global cut_count
                cut_count += 1
                return beta
            alpha = value

    return alpha


#  最后落下的两个子的邻居最有可能是最优点
def order(blank_list):
    # 获得最后一个和倒数第二个落下的棋子
    list_len = len(list3)
    if list_len >= 2:
        last_pt = [list3[-2], list3[-1]]
    else:
        last_pt = [list3[-1]]
    # 相当于在最后落子位置的周围的八个方向进行了遍历
    for cnt in range(0, 2):
        if list_len < 2 and cnt == 1:
            break
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if (last_pt[cnt][0] + i, last_pt[cnt][1] + j) in blank_list:
                    # 把挨着最后一个落子点的位置挪到list的最前面
                    # 因为list是有序的，只能先remove再insert
                    # list.insert(index, obj0
                    blank_list.remove((last_pt[cnt][0] + i, last_pt[cnt][1] + j))
                    blank_list.insert(0, (last_pt[cnt][0] + i, last_pt[cnt][1] + j))


def has_neightnor(pt):
    # 在周围八个方向查找是否有子，如果有子就返回TRUE，没有返回false
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if (pt[0] + i, pt[1]+j) in list3:
                return True
    return False


# 评估函数
def evaluation(is_ai):
    total_score = 0

    if is_ai:
        # AI
        my_list = list1
        # human
        enemy_list = list2
    else:
        # human
        my_list = list2
        # AI
        enemy_list = list1

    # 算自己的得分
    # 得分形状的位置 用于计算如果有相交 得分翻倍
    score_all_arr = []
    my_score = 0

    for pt in my_list:
        # the source
        m = pt[0]
        # the shape
        n = pt[1]
        my_score += cal_score(m, n, 0, 1, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, 1, 0, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, 1, 1, enemy_list, my_list, score_all_arr)
        my_score += cal_score(m, n, -1, 1, enemy_list, my_list, score_all_arr)

    #  算敌人的得分， 并减去
    score_all_arr_enemy = []
    enemy_score = 0
    for pt in enemy_list:
        # the source
        m = pt[0]
        # the shape
        n = pt[1]
        enemy_score += cal_score(m, n, 0, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 0, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, 1, 1, my_list, enemy_list, score_all_arr_enemy)
        enemy_score += cal_score(m, n, -1, 1, my_list, enemy_list, score_all_arr_enemy)

    total_score = my_score - enemy_score * ratio * 0.1

    return total_score


# 每个方向上的分值计算
def cal_score(m, n, x_direct, y_direct, enemy_list, my_list, score_all_arr):
    # 加分项
    add_score = 0
    # 在一个方向上， 只取最大的得分项
    max_score_shape = (0, None)

    # 如果此方向上，该点已经有得分形状，不重复计算
    for item in score_all_arr:
        for pt in item[1]:
            if m == pt[0] and n == pt[1] and x_direct == item[2][0] and y_direct == item[2][1]:
                return 0

    # 在落子点 左右方向上循环查找得分形状
    for offset in range(-5, 1):
        # offset = -2
        pos = []
        for i in range(0, 6):
            if (m + (i + offset) * x_direct, n + (i + offset) * y_direct) in enemy_list:
                pos.append(2)
            elif (m + (i + offset) * x_direct, n + (i + offset) * y_direct) in my_list:
                pos.append(1)
            else:
                pos.append(0)
        tmp_shap5 = (pos[0], pos[1], pos[2], pos[3], pos[4])
        tmp_shap6 = (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])

        for (score, shape) in shape_score:
            if tmp_shap5 == shape or tmp_shap6 == shape:
                if tmp_shap5 == (1,1,1,1,1):
                    print('wwwwwwwwwwwwwwwwwwwwwwwwwww')
                if score > max_score_shape[0]:
                    max_score_shape = (score, ((m + (0+offset) * x_direct, n + (0+offset) * y_direct),
                                               (m + (1+offset) * x_direct, n + (1+offset) * y_direct),
                                               (m + (2+offset) * x_direct, n + (2+offset) * y_direct),
                                               (m + (3+offset) * x_direct, n + (3+offset) * y_direct),
                                               (m + (4+offset) * x_direct, n + (4+offset) * y_direct)), (x_direct, y_direct))

    # 计算两个形状相交， 如两个3活 相交， 得分增加 一个子的除外
    if max_score_shape[1] is not None:
        for item in score_all_arr:
            for pt1 in item[1]:
                for pt2 in max_score_shape[1]:
                    if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
                        add_score += item[0] + max_score_shape[0]

        score_all_arr.append(max_score_shape)

    return add_score + max_score_shape[0]

# 传入的是AI或者human的棋盘，在最后落子点的各个方向上判断是否赢
def game_win(list):
    if len(list) <= 4:
        return False

    last_pt = list[-1]
    dir = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for k in range(0, 4):
        pt1, pt2 = last_pt[0], last_pt[1]
        cnt = 1
        for i in range(0, 4):
            if (pt1 + dir[k][0], pt2 + dir[k][1]) in list:
                pt1 += dir[k][0]
                pt2 += dir[k][1]
                cnt += 1
            else:
                break
        pt1, pt2 = last_pt[0], last_pt[1]
        for i in range(0, 4):
            if (pt1 - dir[k][0], pt2 - dir[k][1]) in list:
                pt1 -= dir[k][0]
                pt2 -= dir[k][1]
                cnt += 1
            else:
                break
        if cnt == 5:
            return True
    return False


def gobangwindow():
    win = GraphWin("Gobang Game change by Violet Guo", GRID_WIDTH * COLUMN, GRID_WIDTH * ROW)
    win.setBackground("yellow")
    i1 = 0

    while i1 <= GRID_WIDTH * COLUMN:
        l = Line(Point(i1, 0), Point(i1, GRID_WIDTH * COLUMN))
        l.draw(win)
        i1 = i1 + GRID_WIDTH
    i2 = 0

    while i2 <= GRID_WIDTH * ROW:
        l = Line(Point(0, i2), Point(GRID_WIDTH * ROW, i2))
        l.draw(win)
        i2 = i2 + GRID_WIDTH
    return win


def main():
    # 获得五子棋游戏的窗口
    window = gobangwindow()

    # 获得整个棋盘的所有点
    for i in range(COLUMN+1):
        for j in range(ROW+1):
            list_all.append((i, j))

    # change代表对弈的次数，人是先手，AI是后手
    # game_continue代表游戏是否继续，值为1，游戏继续；值为0，游戏结束
    change = 0
    game_continue = 1
    m = 0
    n = 0

    while game_continue == 1:
        # 若change是奇数，代表该AI下了
        if change % 2 == 1:
            time1 = datetime.datetime.now()
            pos = ai()

            if pos in list3:
                message = Text(Point(200, 200), "不可用的位置" + str(pos[0]) + "," + str(pos[1]))
                message.draw(window)
                game_continue = 0

            list1.append(pos)
            list3.append(pos)

            # AI是白子，往棋盘上画白子
            piece = Circle(Point(GRID_WIDTH * pos[0], GRID_WIDTH * pos[1]), 16)
            piece.setFill('white')
            piece.draw(window)

            # 计算AI落子的时间
            time2 = datetime.datetime.now()
            interval = time2 - time1
            sec = interval.days * 24 * 3600 + interval.seconds
            print("AI use time : %d" % (sec))

            # 判断AI是否赢了
            if game_win(list1):
                message = Text(Point(100, 100), "white win.")
                message.draw(window)
                game_continue = 0
            change = change + 1
        else:
            # 若change是偶数，代表该human下了
            p2 = window.getMouse()
            if not ((round((p2.getX()) / GRID_WIDTH), round((p2.getY()) / GRID_WIDTH)) in list3):
                a2 = round((p2.getX()) / GRID_WIDTH)
                b2 = round((p2.getY()) / GRID_WIDTH)
                list2.append((a2, b2))
                list3.append((a2, b2))

                # human是黑子，往棋盘上画黑子
                piece = Circle(Point(GRID_WIDTH * a2, GRID_WIDTH * b2), 16)
                piece.setFill('black')
                piece.draw(window)

                # 判断human是否赢了
                if game_win(list2):
                    message = Text(Point(100, 100), "black win.")
                    message.draw(window)
                    game_continue = 0

                change = change + 1

    message = Text(Point(100, 120), "Click anywhere to quit.")
    message.draw(window)
    window.getMouse()
    window.close()


if __name__ == "__main__":
    main()
