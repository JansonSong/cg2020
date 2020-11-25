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
        i = 0
        while i <= length:
            result.append((round(x), round(y)))
            x = x + detax
            y = y + detay
            i += 1
    elif algorithm == 'Bresenham':
        # TODO: this is a bit different from the test sample
        change = 0
        if x1 == x0 and y1 == y0:
            return [(x0, y0)]
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
        c = 2 * detay + detax * (2 * b - signy)
        p = 2 * detay * x - 2 * detax * y + c
        alpha = 2 * detay - signy * 2 * detax
        detay2 = 2 * detay
        for i in range(abs(detax)+1):
            if change == 0:
                result.append((round(x), round(y)))
            else:
                result.append((round(y), round(x)))
            x = x + 1
            if p > 0:
                y = y + signy
                p = p + signy * alpha
            elif p <= 0:
                p = p + signy * detay2
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
    # TODO: this is a bit different from the test sample
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if x0 == x1 or y0 == y1:
        return []
    result = []
    change = 0
    if abs(x1 - x0) < abs(y0 - y1):
        x0, y0, x1, y1 = y0, x0, y1, x1
        change = 1
    deltax = (x1+x0)/2
    deltay = (y1+y0)/2
    if change == 1:
        deltax, deltay = deltay, deltax
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
    result = []
    n = len(p_list) - 1
    if algorithm == 'Bezier':
        u = 0
        p_l = p_list
        while u <= 1:
            for r in range(1, n + 1):
                p_temp = []
                for i in range(0, n - r + 1):
                    x_t = p_l[i][0] * (1 - u) + p_l[i + 1][0] * u
                    y_t = p_l[i][1] * (1 - u) + p_l[i + 1][1] * u
                    p_temp.append([x_t, y_t])
                p_l = p_temp
            result.append((round(p_l[0][0]), round(p_l[0][1])))
            p_l = p_list
            u += 0.001
    elif algorithm == 'B-spline':
        def calculate_B(Bik, k, u, n):
            if k == 1:
                return
            calculate_B(Bik, k - 1, u, n)
            for i in range(n + 1):
                Bik[i] = ((u - i) * Bik[i] + (i + k - u) * Bik[i + 1]) / (k - 1)
            return
        k = 4
        u = k - 1
        while u <= n + 1:
            sum_list = [0, 0]
            Bik = []
            for i in range(n + k + 1):
                if i <= u and u < (i + 1):
                    Bik.append(1)
                else:
                    Bik.append(0)
            calculate_B(Bik, k, u, n)
            for i in range(n + 1):
                sum_list[0] += p_list[i][0] * Bik[i]
                sum_list[1] += p_list[i][1] * Bik[i]
            x, y = sum_list[0], sum_list[1]
            result.append((round(x), round(y)))
            u += 0.005
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for coord in p_list:
        x = coord[0] + dx
        y = coord[1] + dy
        result.append((round(x), round(y)))
    return result


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    cosr = math.cos(r * math.pi / 180)
    sinr = math.sin(r * math.pi / 180)
    for coord in p_list:
        xt = x + (coord[0] - x) * cosr - (coord[1] - y) * sinr
        yt = y + (coord[0] - x) * sinr + (coord[1] - y) * cosr
        result.append((round(xt), round(yt)))
    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    # TODO:如果是扩大，还要考虑插值问题，这留后续考虑
    result = []
    dx0 = (1 - s) * x
    dy0 = (1 - s) * y
    for coord in p_list:
        xt = s * coord[0] + dx0
        yt = s * coord[1] + dy0
        result.append((round(xt), round(yt)))
    return result


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
    result = []
    x1, y1, x2, y2 = p_list[0][0], p_list[0][1], p_list[1][0], p_list[1][1]
    if algorithm == 'Cohen-Sutherland':
        def encode(x, y):
            c = 0
            if x < x_min:
                c |= 1
            elif x > x_max:
                c |= (1 << 1)
            if y < y_min:
                c |= (1 << 2)
            elif y > y_max:
                c |= (1 << 3)
            return c
        c1 = encode(x1, y1)
        c2 = encode(x2, y2)
        if c1 & c2 != 0:
            return None
        elif c1 | c2 == 0:
            return p_list
        if c1 != 0:
            u = 0
            if c1 & 1:
                u = (x_min - x1) / (x2 - x1)
            if c1 & (1 << 1):
                u = max(u, (x_max - x1) / (x2 - x1))
            if c1 & (1 << 2):
                u = max(u, (y_min - y1) / (y2 - y1))
            if c1 & (1 << 3):
                u = max(u, (y_max - y1) / (y2 - y1))
            x1 = x1 + u * (x2 - x1)
            y1 = y1 + u * (y2 - y1)
        if c2 != 0:
            u = 0
            if c2 & 1:
                u = (x_min - x2) / (x1 - x2)
            if c2 & (1 << 1):
                u = max(u, (x_max - x2) / (x1 - x2))
            if c2 & (1 << 2):
                u = max(u, (y_min - y2) / (y1 - y2))
            if c2 & (1 << 3):
                u = max(u, (y_max - y2) / (y1 - y2))
            x2 = x2 + u * (x1 - x2)
            y2 = y2 + u * (y1 - y2)
        # 怎么处理边界条件，即如果求出的边界是带有小数怎么办，四舍五入还是有其他方法去解决
        result.append([round(x1), round(y1)])
        result.append([round(x2), round(y2)])
    elif algorithm == 'Liang-Barsky':
        p = [0] * 5
        q = [0] * 5
        p[1] = p[2] = x2 - x1
        p[3] = p[4] = y2 - y1
        q[1] = x1 - x_min
        q[2] = x_max - x1
        q[3] = y1 - y_min
        q[4] = y_max - y1
        u1, u2 = 0, 1
        if p[1] == 0:
            if q[1] < 0 or q[2] < 0:
                return None
        if p[3] == 0:
            if q[3] < 0 or q[4] < 0:
                return None
        # TODO: should consider more below
        for k in range(1, 5):
            r = 0
            if p[k] < 0:
                r = q[k] / p[k]
                u1 = max(u1, r)
            elif p[k] > 0:
                r = q[k] / p[k]
                if r < 0:
                    continue
                u2 = min(u2, r)
        if u1 > u2:
            return None
        x_1 = x1 + u1 * (x2 - x1)
        x_2 = x1 + u2 * (x2 - x1)
        y_1 = y1 + u1 * (y2 - y1)
        y_2 = y1 + u2 * (y2 - y1)
        result.append((round(x_1), round(y_1)))
        result.append((round(x_2), round(y_2)))
    return result
