from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math
import os
import json
import argparse
import PIL
from PIL import Image

PIL.Image.MAX_IMAGE_PIXELS = None

import numpy as np

parser = argparse.ArgumentParser(description='rsync')
parser.add_argument('--path', type=str, help='learning rate')


args = parser.parse_args()


class SubQGraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(SubQGraphicsScene, self).__init__(parent)

    def mouseMoveEvent(self, event):
        pos = event.scenePos()
        #  print(pos)
        super(SubQGraphicsScene, self).mouseMoveEvent(event)


class QViewer(QGraphicsView):

    def __init__(self, parent=None):
        super(QViewer, self).__init__(parent)
        self.scene = SubQGraphicsScene()
        self.setScene(self.scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
        self.setFrameShape(QFrame.NoFrame)

        #
        self.setAlignment(Qt.AlignLeft |
                          Qt.AlignTop)
        self.size = 256
        self.item = QGraphicsRectItem(QRectF(0, 0, self.size, self.size))
        self.item.setPos(0, 0)
        #  self.item.setBrush(Qt.red)
        pen = QPen()
        pen.setWidth(5)
        pen.setBrush(Qt.red)
        pen.setStyle(Qt.DashDotDotLine)
        self.item.setPen(pen)
        self.item.setOpacity(1)

        #  pixmap = QPixmap()
        path = '/Users/carry/Downloads/test-rgb.jpeg'
        path = '/Users/carry/Downloads/指环王密码.jpg'
        self.image_path = args.path
        self.json_path = os.path.splitext(self.image_path)[0] + '.json'
        self.cloud_path = os.path.splitext(self.image_path)[
            0] + '.tiff_CloudExtraction.jpg'
        self.photo = QGraphicsPixmapItem()
        self.photo.setZValue(-1)
        self.imageData = process(self.image_path, None)
        image = QImage.fromData(self.imageData)
        pixmap = QPixmap.fromImage(image)
        self.photo.setPixmap(pixmap)

        self.scene.addItem(self.photo)
        if os.path.exists(self.json_path):
            print('load from ', self.json_path)
            s = load_pickle(self.json_path)
        else:
            s = {}
        if os.path.exists(self.cloud_path):
            img = np.array(PIL.Image.open(self.cloud_path))
            s_cloud = {}
            h, w = img.shape[0], img.shape[1]
            for i in range(0, w, 256):
                for j in range(0, h, 256):
                    tmp = np.sum(img[i:i + 256, j:j + 256]) / (256 * 256 * 255)
                    if tmp > 0.2:
                        s_cloud[(j, i)] = 1
        else:
            s_cloud = {}

        idx_color_dict = {1: Qt.green, 2: Qt.blue,
                          3: Qt.yellow, 4: Qt.gray}
        for i in range(0, int(pixmap.rect().width()), self.size):
            for j in range(0, int(pixmap.rect().height()), self.size):
                item = QGraphicsRectItem(QRectF(0, 0, self.size, self.size))
                #  item = QGraphicsRectItem(
                #      QRectF(i, j, self.size, self.size))
                #  item.setBrush(Qt.red)
                if (i, j) in s:
                    item.setBrush(idx_color_dict[s[(i, j)]])
                    item.idx = s[(i, j)]
                if (i, j) in s_cloud:
                    item.setBrush(idx_color_dict[s_cloud[(i, j)]])
                    item.idx = s_cloud[(i, j)]
                item.setPos(i, j)
                item.setOpacity(0.1)
                self.scene.addItem(item)

        self.scene.addItem(self.item)
        self.current_item = None

        self.rubberband = QRubberBand(
            QRubberBand.Rectangle, self)
        #  self.setMouseTracking(True)
        self.flag_is_select = False
        #
        #  self.setDragMode(self.ScrollHandDrag)
        #  self.setOptimizationFlag(self.DontSavePainterState)
        #  self.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing |
        #                      QPainter.SmoothPixmapTransform)
        #  self.setResizeAnchor(self.AnchorUnderMouse)
        #  self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        #  self.setTransformationAnchor(self.AnchorUnderMouse)
        #  self.setViewportUpdateMode(self.SmartViewportUpdate)

    #  def setPhoto(self, pixmap=None):
    #
    #      if pixmap and not pixmap.isNull():
    #          #  self.setDragMode(QGraphicsView.ScrollHandDrag)
    #          # 没想好要不要自适应显示
    #          self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
    #
    #          self.pixmap = pixmap
    #          # Set scene size to image size.
    #          #  self.setSceneRect(QRectF(pixmap.rect()))
    #          self.photo.setPixmap(self.pixmap)
    #          for i in range(0, int(pixmap.rect().width()), self.size):
    #              for j in range(0, int(pixmap.rect().height()), self.size):
    #                  item = QGraphicsRectItem(
    #                      QRectF(i, j, self.size, self.size))
    #                  #  item.setBrush(Qt.red)
    #                  item.setOpacity(0.1)
    #                  self.scene.addItem(item)
    #
    #          self.scene.addItem(self.item)
    #      else:
    #          self.setDragMode(QGraphicsView.NoDrag)
    #          self.photo.setPixmap(QPixmap())
    #
    def mouseDoubleClickEvent(self, event):
        #  print(event.pos())
        pos = self.mapToScene(event.pos())
        x, y = pos.x(), pos.y()
        x, y = self.size * (x // self.size), self.size * (y // self.size)
        #  print(x, y)
        self.item.setPos(x, y)
        super(QViewer, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(
            QRect(self.origin, QSize()))
        self.rubberband.show()
        super(QViewer, self).mousePressEvent(event)
    #

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QRect(self.origin, event.pos()).normalized())
    #          #  rect = self.rubberband.geometry()
    #          #  x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    #          #
    #          #  items = self.scene.items(
    #          #      x + 5, y + 5, w, h, Qt.IntersectsItemShape, True)
    #
    #      QWidget.mouseMoveEvent(self, event)
        super(QViewer, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.flag_is_select = True
            self.rubberband.hide()
            rect = self.rubberband.geometry()
            rect_scene = self.mapToScene(rect).boundingRect()
            #  print(rect_scene)
            items = self.scene.items(rect_scene)
            if len(items) < 3:
                self.flag_is_select = False
            #  print(len(selected))
            #  x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            #  print(x, y, w, h)
            #  pos = self.mapToScene(x, y)
            #  x, y = pos.x(), pos.y()
            #  pos = self.mapToScene(w, h)
            #  w, h = pos.x(), pos.y()
            #  print(x, y, w, h)

            #  items = self.scene.items(
            #      x + 5, y + 5, w, h, Qt.IntersectsItemShape, True)
            #  #  print(len(items))
            if len(items) < 3:
                return
            for item in items:
                if (item != self.item) and (item != self.photo):

                    pen = QPen()
                    pen.setWidth(3)
                    pen.setBrush(Qt.black)
                    pen.setStyle(Qt.DashDotDotLine)
                    item.setPen(pen)
                    item.setOpacity(0.8)
                    #  item.setOpacity(0.3)
    #          #  for child in self.scene.items():
    #          #      if rect.intersects(child.boundingRect()):
    #          #          selected.append(child)
    #          #  if selected:
    #          #      print('  '.join(
    #          #          'Button: %s\n' % child.text() for child in selected))
    #          #  else:
    #          #      print(' Nothing\n')
        #  QWidget.mouseReleaseEvent(self, event)
    #

    def wheelEvent(self, event):
        # 滑轮事件
        if event.modifiers() & Qt.ControlModifier:
            self.scaleView(math.pow(2.0, -event.angleDelta().y() / 240))
            return event.accept()
        super(QViewer, self).wheelEvent(event)

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(
            scaleFactor, scaleFactor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scaleFactor, scaleFactor)

    def keyPressEvent(self, event):
        key = event.key()

        color_dict = {Qt.Key_1: Qt.green, Qt.Key_2: Qt.blue,
                      Qt.Key_3: Qt.yellow, Qt.Key_4: Qt.gray}
        id_dict = {Qt.Key_1: 1, Qt.Key_2: 2, Qt.Key_3: 3, Qt.Key_4: 4}

        #  def set_color(key, color_dict):
        #      color = color_dict[key]
        #      #  self.current_item.setBrush(color)
        #      #  print(self.current_item.opacity())
        #      for item in selected_items:
        #          item.setBrush(color)
        #          item.setOpacity(0.1)

        if self.flag_is_select is True:
            print('true')
            selected_items = []
            for item in self.scene.items():
                if item.opacity() == 0.8:
                    selected_items.append(item)
            if key in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4]:
                color = color_dict[key]
                id = id_dict[key]
                for item in selected_items:
                    item.setBrush(color)
                    item.setOpacity(0.1)
                    item.idx = id
            else:
                for item in selected_items:
                    item.setOpacity(0.1)

            self.flag_is_select = False
            return

        if key == Qt.Key_R:
            self.resetTransform()
        if key == Qt.Key_S and Qt.ControlModifier:
            self.save()
        if key == Qt.Key_Right:
            #  print('move right')
            self.item.moveBy(self.size, 0)
        if key == Qt.Key_Left:
            #  print('move right')
            self.item.moveBy(-self.size, 0)
        if key == Qt.Key_Up:
            #  print('move up')
            self.item.moveBy(0, -self.size)
        if key == Qt.Key_Down:
            #  print('move down')
            self.item.moveBy(0, self.size)
        x = self.item.pos().x()
        y = self.item.pos().y()
        print(x, y)
        items = self.scene.items(
            x + 5, y + 5, 10, 10, Qt.IntersectsItemShape, True)
        self.current_item = items[1]
        self.current_item.setOpacity(0.1)

        if key in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4]:
            color = color_dict[key]
            id = id_dict[key]
            self.current_item.setBrush(color)
            self.current_item.idx = id

    def save(self):
        s = {}
        for item in self.scene.items():
            if (item != self.item) and (item != self.photo) and hasattr(item, 'idx'):
                x = item.scenePos().x()
                y = item.scenePos().y()
                idx = item.idx
                s[(int(x), int(y))] = idx
        save_pickle(s, self.json_path)

    def loadImageFromFile(self, fileName=""):
        """ Load an image from file.
        Without any arguments, loadImageFromFile() will popup a file dialog to choose the image file.
        With a fileName argument, loadImageFromFile(fileName) will attempt to load the specified image file directly.
        """
        if len(fileName) == 0:
            if QT_VERSION_STR[0] == '4':
                fileName = QFileDialog.getOpenFileName(
                    self, "Open image file.")
            elif QT_VERSION_STR[0] == '5':
                fileName, dummy = QFileDialog.getOpenFileName(
                    self, "Open image file.")
        if len(fileName) and os.path.isfile(fileName):
            print(fileName)
            self.setImage(fileName)


def save_pickle(object, save_path):

    import pickle
    f = open(save_path, 'wb')
    pickle.dump(object, f)
    f.close()


def load_pickle(path):
    import pickle
    f = open(path, 'rb')
    object = pickle.load(f)
    f.close()
    return object


def process(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self,).__init__()
        #  self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.Widget)
        self.viewer = QViewer(self)
        self.setCentralWidget(self.viewer)
        self.showMaximized()
        self.setWindowTitle("Pan AI Lab Labelme")
        #  self.viewer.loadImageFromFile()

        #  self.open_image()

    def open_image(self):
        #  path = '/Users/carry/Downloads/test-rgb.jpeg'
        #  path = '/Users/carry/Downloads/指环王密码.jpg'
        self.imageData = process(path, None)
        image = QImage.fromData(self.imageData)
        self.viewer.setPhoto(QPixmap.fromImage(image))

    def closeEvent(self, event):
        print('quit')
        self.viewer.save()


if __name__ == '__main__':
    import sys
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    mainWindow = MainWindow()
    mainWindow.show()
    try:
        app.exec_()
    except Exception as e:
        print(e)
        print('fuck')
