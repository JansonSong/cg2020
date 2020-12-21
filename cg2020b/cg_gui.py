#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem, )
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QMoveEvent
from PyQt5.QtCore import QRectF, Qt
from PyQt5.Qt import QPalette, QColorDialog, QPen, QInputDialog, QFileDialog
import math
import numpy as np
from PIL import Image


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None

        self.begin_position = []
        self.end_position = []
        self.begin_p_list = []
        self.center_point = []

        self.clip_rect_item = None

        self.draw_status = 'end'

        self.pen_color = QColor(0, 0, 0)

    def reset_canvas(self, item_id):
        self.item_dict = {}
        self.status = ''
        self.draw_status = 'end'
        self.temp_id = item_id
        self.temp_item = None

    def set_pen_color(self, color):
        self.pen_color = color

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = item_id

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def delete_action(self):
        if self.selected_id == '':
            return False, ''
        delete_id = self.selected_id
        self.selected_id = ''
        count = self.list_widget.count()
        index = 0
        for i in range(count):
            if self.list_widget.item(i).text() == delete_id:
                index = i
        if self.item_dict[delete_id].selected:
            self.list_widget.takeItem(index)
            self.scene().removeItem(self.item_dict[delete_id])
            self.item_dict.pop(delete_id)
        return True, delete_id

    def select_action(self):
        self.status = 'select'

    def translate_action(self):
        self.status = 'translate'

    def rotate_action(self):
        self.status = 'rotate'

    def scale_action(self):
        self.status = 'scale'

    def clip_action(self, algorithm):
        self.status = 'clip'
        self.temp_algorithm = algorithm

    def finish_draw(self):
        self.main_window.set_id()
        self.temp_id = self.main_window.get_id()

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        if selected == '':
            return
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        if self.status != 'select':
            self.status = ''
        self.updateScene([self.sceneRect()])

    def get_selected_item(self):
        for item in self.scene().items():
            if item.id == self.selected_id:
                return item
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.draw_status == 'start' and \
                self.status != 'polygon' and self.status != 'curve':
            self.temp_item.status = 'finish'
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
            self.temp_item = None
            self.draw_status = 'end'
            self.updateScene([self.sceneRect()])
        if event.button() == Qt.LeftButton:
            self.get_mouse_left_event(event)
        elif event.button() == Qt.RightButton:
            self.get_mouse_right_event(event)

    def get_mouse_left_event(self, event: QMouseEvent):
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,
                                    pen_color=self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon':
            if self.temp_item is None:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,
                                        pen_color=self.pen_color)
                self.scene().addItem(self.temp_item)
                self.draw_status = 'start'
            else:
                self.temp_item.p_list.append([x, y])
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,
                                    pen_color=self.pen_color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'curve':
            if self.temp_item is None:
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm,
                                        pen_color=self.pen_color, status='start')
                self.scene().addItem(self.temp_item)
                self.draw_status = 'start'
            else:
                self.temp_item.p_list.append([x, y])
        elif self.status == 'select':
            for item in self.scene().items():
                if item.is_in_bounding_rect(x, y):
                    self.selection_changed(item.id)
                    break
        elif self.status == 'translate':
            self.temp_item = self.get_selected_item()
            if self.temp_item is None:
                return
            self.begin_position = [x, y]
            self.begin_p_list = []
            for point in self.temp_item.p_list:
                self.begin_p_list.append(point.copy())
        elif self.status == 'rotate':
            self.temp_item = self.get_selected_item()
            if self.temp_item is None:
                return
            self.begin_position = [x, y]
            rect = self.temp_item.boundingRect().getRect()
            self.center_point = [rect[0] + rect[2] / 2, rect[1] + rect[3] / 2]
            self.begin_p_list = []
            for point in self.temp_item.p_list:
                self.begin_p_list.append(point.copy())
        elif self.status == 'scale':
            self.temp_item = self.get_selected_item()
            if self.temp_item is None:
                return
            self.begin_position = [x, y]
            rect = self.temp_item.boundingRect().getRect()
            self.center_point = [rect[0] + rect[2] / 2, rect[1] + rect[3] / 2]
            self.begin_p_list = []
            for point in self.temp_item.p_list:
                self.begin_p_list.append(point.copy())
        elif self.status == 'clip':
            self.temp_item = self.get_selected_item()
            if self.temp_item is None or self.temp_item.item_type != 'line':
                self.temp_item = None
                return
            self.clip_rect_item = MyItem('clip', self.status, [[x, y], [x, y]], None, None)
            self.scene().addItem(self.clip_rect_item)
            self.begin_position = [x, y]
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def get_mouse_right_event(self, event: QMouseEvent):
        if self.temp_item is None:
            return
        if self.status == 'polygon' or self.status == 'curve':
            self.temp_item.status = 'finish'
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
            self.temp_item = None
            self.draw_status = 'end'
        self.updateScene([self.sceneRect()])
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.temp_item is None:
            return
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon':
            point_count = len(self.temp_item.p_list)
            self.temp_item.p_list[point_count - 1] = [x, y]
        elif self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'curve':
            pass
        elif self.status == 'translate':
            self.temp_item.p_list = alg.translate(self.begin_p_list, x - self.begin_position[0],
                                                  y - self.begin_position[1])
        elif self.status == 'rotate':
            angle1 = math.atan2(self.begin_position[1] - self.center_point[1],
                                self.begin_position[0] - self.center_point[0])
            angle2 = math.atan2(y - self.center_point[1], x - self.center_point[0])
            angle = angle2 - angle1
            angle = int(angle * 180 / math.pi)
            self.temp_item.p_list = alg.rotate(self.begin_p_list, self.center_point[0], self.center_point[1], angle)
        elif self.status == 'scale':
            a = math.sqrt((self.begin_position[0] - self.center_point[0]) ** 2 + (
                    self.begin_position[1] - self.center_point[1]) ** 2)
            b = math.sqrt((x - self.center_point[0]) ** 2 + (y - self.center_point[1]) ** 2)
            s = b / a
            self.temp_item.p_list = alg.scale(self.begin_p_list, self.center_point[0], self.center_point[1], s)
        elif self.status == 'clip':
            self.clip_rect_item.p_list[1] = [x, y]
            self.end_position = [x, y]
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.temp_item is None:
            return
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
            self.temp_item = None
        elif self.status == 'polygon':
            pass
        elif self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
            self.temp_item = None
        elif self.status == 'curve':
            pass
        elif self.status == 'translate':
            pass
        elif self.status == 'rotate':
            self.begin_p_list = []
            for point in self.temp_item.p_list:
                self.begin_p_list.append(point.copy())
        elif self.status == 'scale':
            self.begin_p_list = []
            for point in self.temp_item.p_list:
                self.begin_p_list.append(point.copy())
        elif self.status == 'clip':
            xmin = min(self.begin_position[0], self.end_position[0])
            xmax = max(self.begin_position[0], self.end_position[0])
            ymin = min(self.begin_position[1], self.end_position[1])
            ymax = max(self.begin_position[1], self.end_position[1])
            self.temp_item.p_list = alg.clip(self.temp_item.p_list, xmin, ymin, xmax, ymax, self.temp_algorithm)
            if len(self.temp_item.p_list) == 0:
                count = self.list_widget.count()
                index = 0
                for i in range(count):
                    if self.list_widget.item(i).text() == self.temp_item.id:
                        index = i
                self.list_widget.takeItem(index)
                self.scene().removeItem(self.temp_item)
                self.selected_id = ''
            self.scene().removeItem(self.clip_rect_item)
            self.clip_rect_item = None
            self.updateScene([self.sceneRect()])
        super().mouseReleaseEvent(event)

    def save_current_canvas(self, filepath, width, height):
        canvas = np.zeros([height, width, 3], np.uint8)
        canvas.fill(255)
        for item in self.item_dict.values():
            item.get_canvas(canvas)
        Image.fromarray(canvas).save(filepath)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', parent: QGraphicsItem = None,
                 pen_color=QColor(255, 0, 0), status='finish'):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.pen_color = pen_color

        self.status = status

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen_color)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                pen = QPen(Qt.DashLine)
                pen.setColor(QColor(255, 0, 0))
                painter.setPen(pen)
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                pen = QPen(Qt.DashLine)
                pen.setColor(QColor(255, 0, 0))
                painter.setPen(pen)
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                pen = QPen(Qt.DashLine)
                pen.setColor(QColor(255, 0, 0))
                painter.setPen(pen)
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            if self.status != 'finish':
                for point in self.p_list:
                    pixels = alg.draw_curve_point(point)
                    for p in pixels:
                        painter.drawPoint(*p)
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                pen = QPen(Qt.DashLine)
                pen.setColor(QColor(255, 0, 0))
                for point in self.p_list:
                    pixels = alg.draw_curve_point(point)
                    for p in pixels:
                        painter.drawPoint(*p)
                painter.setPen(pen)
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'clip':
            pen = QPen(Qt.DashLine)
            pen.setColor(QColor(0, 0, 255))
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if len(self.p_list) == 0:
            return QRectF(0, 0, 0, 0)
        if self.item_type == 'line' or self.item_type == 'clip':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'curve':
            xmin, ymin = self.p_list[0]
            xmax, ymax = xmin, ymin
            for point in self.p_list:
                xmin = min(xmin, point[0])
                ymin = min(ymin, point[1])
                xmax = max(xmax, point[0])
                ymax = max(ymax, point[1])
            x, y = xmin, ymin
            w, h = xmax - xmin, ymax - ymin
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)

    def is_in_bounding_rect(self, x_pos, y_pos):
        rect = self.boundingRect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        if x < x_pos < x + w and y < y_pos < y + h:
            return True
        return False

    def get_canvas(self, canvas):
        pen_color = np.zeros(3, np.uint8)
        pen_color[0] = self.pen_color.red()
        pen_color[1] = self.pen_color.green()
        pen_color[2] = self.pen_color.blue()
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for x, y in item_pixels:
                canvas[y, x] = pen_color
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for x, y in item_pixels:
                canvas[y, x] = pen_color
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            for x, y in item_pixels:
                canvas[y, x] = pen_color
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for x, y in item_pixels:
                canvas[y, x] = pen_color


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.item_cnt = 0

        # TODO:使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_image_act = file_menu.addAction('保存图片')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        delete_act = edit_menu.addAction('删除')
        select_act = edit_menu.addAction('选择')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_image_act.triggered.connect(self.save_image_action)
        exit_act.triggered.connect(qApp.quit)

        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)

        delete_act.triggered.connect(self.delete_action)
        select_act.triggered.connect(self.select_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)

        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG SJQ')

        # self.setCursor(Qt.CursorShape.DragMoveCursor)

    def get_id(self):
        _id = str(self.item_cnt)
        return _id

    def set_id(self):
        self.item_cnt += 1

    def set_pen_action(self):
        # 设置画笔颜色
        QColorDialog.setCustomColor(3, QColor(10, 60, 200))
        color = QColorDialog.getColor(QColorDialog.customColor(3), self, 'Select Color')
        self.canvas_widget.set_pen_color(color)

    def reset_canvas_action(self):
        # 重置画布
        width, ok_pressed = QInputDialog.getInt(self, "Get Width", "Width:", 600, 600, 1000)
        width = width if ok_pressed else 600
        height, ok_pressed = QInputDialog.getInt(self, "Get Height", "Height:", 600, 600, 1000)
        height = height if ok_pressed else 600

        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.item_cnt = 0
        self.scene.clear()
        self.scene.setSceneRect(0, 0, width, height)
        self.resize(width, height)
        self.canvas_widget.setFixedSize(width, height)
        self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])
        self.canvas_widget.reset_canvas(self.get_id())
        self.list_widget.clear()

    def save_image_action(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'save image', './output', 'Image files(*.bmp)')
        if file_path != '':
            self.canvas_widget.save_current_canvas(file_path, self.canvas_widget.width(), self.canvas_widget.height())

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive draw line')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA draw line')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham draw line')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA draw polygon')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham draw polygon')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('draw ellipse')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier draw curve')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('B-spline draw curve')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def delete_action(self):
        flag, delete_id = self.canvas_widget.delete_action()
        if flag:
            self.statusBar().showMessage('delete 图元' + delete_id)
        else:
            self.statusBar().showMessage('fail to delete')

    def select_action(self):
        self.canvas_widget.select_action()
        self.statusBar().showMessage('select')

    def translate_action(self):
        self.canvas_widget.translate_action()
        self.statusBar().showMessage('translate')

    def rotate_action(self):
        self.canvas_widget.rotate_action()
        self.statusBar().showMessage('rotate')

    def scale_action(self):
        self.canvas_widget.scale_action()
        self.statusBar().showMessage('scale')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.clip_action('Cohen-Sutherland')
        self.statusBar().showMessage('Cohen-Sutherland algorithm clip line')

    def clip_liang_barsky_action(self):
        self.canvas_widget.clip_action('Liang-Barsky')
        self.statusBar().showMessage('Liang-Barsky algorithm clip line')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
