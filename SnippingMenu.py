import os
import os.path
import os.path
import tkinter as tk
from tkinter import *
from PIL import ImageGrab
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QMessageBox

main_path = os.path.expanduser('~')
first_or_next = 0


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = tk.Tk()
        global numberFolder
        numberFolder = 0
        while os.path.exists(main_path + "/screen/" + str(numberFolder)):
            numberFolder = numberFolder + 1
        os.makedirs(main_path + "/screen/" + str(numberFolder))

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(' ')
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.3)
        self.num_snip = 0
        self.is_snipping = False
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()

    def paintEvent(self, event):
        if self.is_snipping:
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0
        else:
            brush_color = (128, 128, 255, 128)
            lw = 3
            opacity = 0.3

        self.setWindowOpacity(opacity)
        qp = QtGui.QPainter(self)

        global finalValueHeightForSnippingMenu
        global finalValueWidthForSnippingMenu
        global first_or_next
        if first_or_next == 0:
            qp.setPen(QtGui.QPen(QtGui.QColor('black'), lw))
            qp.setBrush(QtGui.QColor(*brush_color))
            qp.drawRect(QtCore.QRect(self.begin, self.end))

        if first_or_next == 1:
            file_names_first_image = main_path + '/screen/' + str(numberFolder) + '/snip1.png'
            print('File: ' + file_names_first_image)
            pimp = QPixmap(file_names_first_image)

            finalValueWidthForSnippingMenu = pimp.width()
            finalValueHeightForSnippingMenu = pimp.height()
            print(str(finalValueWidthForSnippingMenu))
            print(str(finalValueHeightForSnippingMenu))

            value_x = self.begin.x() - (finalValueWidthForSnippingMenu / 2)
            value_y = self.begin.y() - (finalValueHeightForSnippingMenu / 2)
            qp.drawRect(
                QtCore.QRect(value_x, value_y, finalValueWidthForSnippingMenu, finalValueHeightForSnippingMenu))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            print('Quit')
            self.close()
            QMessageBox.information(self, 'Informacja',
                                    'Obrazy zostały zapisane w następującym folderze: ' + main_path + '\screen\ ' + str(
                                        numberFolder))
        event.accept()

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        # self.close()
        global first_or_next
        self.num_snip += 1
        if first_or_next == 0:
            x1 = min(self.begin.x(), self.end.x())
            y1 = min(self.begin.y(), self.end.y())
            x2 = max(self.begin.x(), self.end.x())
            y2 = max(self.begin.y(), self.end.y())

        if first_or_next == 1:
            x1 = min(self.begin.x() - (finalValueWidthForSnippingMenu / 2),
                     self.end.x() - (finalValueWidthForSnippingMenu / 2))
            y1 = min(self.begin.y() - (finalValueHeightForSnippingMenu / 2),
                     self.end.y() - (finalValueHeightForSnippingMenu / 2))
            x2 = x1 + finalValueWidthForSnippingMenu
            y2 = y1 + finalValueHeightForSnippingMenu

        self.is_snipping = True
        self.repaint()
        QtWidgets.QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        self.is_snipping = False
        self.repaint()
        QtWidgets.QApplication.processEvents()
        if not os.path.exists(main_path + "/screen"):
            os.makedirs(main_path + "/screen")
        os.chdir(main_path)
        img_name = main_path + '/screen/' + str(numberFolder) + '/snip{}.png'.format(self.num_snip)
        img.save(img_name)
        if first_or_next == 0:
            first_or_next = 1


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())
