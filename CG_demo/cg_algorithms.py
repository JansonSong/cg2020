#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if x1 == x0 and y1 == y0:
            return [(x0, y0)]
        length = max(abs(x1 - x0), abs(y1 - y0))
        detax = (x1 - x0) / length
        detay = (y1 - y0) / length
        x = x0
        y = y0
        for i in range(length + 1):
            result.append((round(x), round(y)))
            x = x + detax
            y = y + detay
    elif algorithm == 'Bresenham':
        change = 0
        if abs(x0 - x1) < abs(y0 - y1):
            x0, y0, x1, y1 = y0, x0, y1, x1
            change = 1
        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        detax, detay = x1 - x0, y1 - y0
        signy = 1
        if y1 == y0:
            signy = 0
        elif y0 > y1:
            signy = -1
        x, y = x0, y0
        m = detay / detax
        b = y0 - m * x0
        c = 2*detay+detax*(2*b-signy)
        p = 2*detay*x-2*detax*y+c
        alpha = 2*detay-signy*2*detax
        detay2 = 2*detay2
        for i in range(abs(detax)+1):
            if change == 0:
                result.append((round(x), round(y)))
            else:
                result.append((round(y), round(x)))
            x = x + 1
            if p > 0:
                y = y + signy
                p = signy*(p+alpha)
            elif p <= 0:
                p = signy*(p + detay2)
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """

    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    change = 0
    if abs(x1 - x0) < abs(y0 - y1):
        x0, y0, x1, y1 = y0, x0, y1, x1
        change = 1
    deltax = (x1+x0)/2
    deltay = (y1+y0)/2
    a = abs(x1 - x0) / 2
    b = abs(y1 - y0) / 2
    aa, bb = a*a, b*b
    toaa, tobb = 2*aa, 2*bb
    thaa, thbb = 3*aa, 3*bb
    x, y = 0, round(b)
    p = bb-aa*b+aa/4
    alpha = toaa + thbb
    while aa*y >= bb*x:
        m, n = x, y
        if change == 1:
            m, n = y, x
        result.append((round(m+deltax), round(n+deltay)))
        result.append((round(-m+deltax), round(n+deltay)))
        result.append((round(m+deltax), round(-n+deltay)))
        result.append((round(-m+deltax), round(-n+deltay)))
        x = x + 1
        if p < 0:
            p = p+tobb*x+thbb
        else:
            p = p+tobb*x-toaa*y+alpha
            y = y - 1
        
    p = bb*(x+1/2)*(x+1/2)+aa*(y-1)*(y-1)-aa*bb
    alpha = tobb + thaa
    while y >= 0:
        m, n = x, y
        if change == 1:
            m, n = y, x
        result.append((round(m+deltax), round(n+deltay)))
        result.append((round(-m+deltax), round(n+deltay)))
        result.append((round(m+deltax), round(-n+deltay)))
        result.append((round(-m+deltax), round(-n+deltay)))
        y = y - 1
        if p <= 0:
            p = p+tobb*x-toaa*y+alpha
            x = x + 1
        else:
            p = p-toaa*y+thaa
    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    # result = []
    # n = len(p_list) - 1
    # u = 0
    # while u <= 1:
    #     tp_list = p_list.copy()
    #     for r in range(n):
    #         for i in range(n - r):
    #             tp_list[i][0] = (1 - u)*tp_list[i][0] + u*tp_list[i+1][0]
    #             tp_list[i][1] = (1 - u)*tp_list[i][1] + u*tp_list[i+1][1]
    #     result.append((round(tp_list[0][0]), round(tp_list[0][1])))
    #     u = u + 0.001


    result = []
    n = len(p_list) - 1
    def calculate_t(t, p_list):
        coefficient_list = [0] * (n + 1)
        # coefficient_list[0] = 1
        coefficient_list[0] = 1 - t
        coefficient_list[1] = t
        tmp = 0
        for r in range(2, n + 1):
            for i in range(r + 1):
                if i == 0:
                    tmp = coefficient_list[0]
                    coefficient_list[0] *= (1 - t)
                else:
                    tp = coefficient_list[i]
                    coefficient_list[i] = (1 - t) * coefficient_list[i] + t * tmp
                    tmp = tp

        sumval = [0, 0]
        for i in range(n + 1):
            sumval[0] += coefficient_list[i] * p_list[i][0]
            sumval[1] += coefficient_list[i] * p_list[i][1]
        
        return sumval
    t = 0
    while t <= 1:
        x_t, y_t = calculate_t(t, p_list)
        result.append((int(x_t), int(y_t)))
        t += 0.001
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    pass
