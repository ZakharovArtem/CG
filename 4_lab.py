from PyQt5.QtCore import pyqtSignal, QPoint, QSize, Qt
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QOpenGLWidget, QSlider,
                             QWidget)

from OpenGL.GL import *
from OpenGL.GLUT import *

from math import *

g_fViewDistance = 4.
g_Width = 600
g_Height = 600

g_nearPlane = 1.
g_farPlane = 1000.
zoom = 65.

class Window(QWidget):

    def __init__(self):
        super(Window, self).__init__()

        self.glWidget = GLWidget()

        self.ambient_slider = self.createSlider()
        self.diffuse_slider = self.createSlider()
        self.position_slider = self.createSlider()

        self.position_slider.setRange(1, 100)
        self.position_slider.setValue(40)
        self.position_slider.setSingleStep(10)

        self.ambient_slider.valueChanged.connect(self.glWidget.setAmbient)
        self.glWidget.ambient_changed.connect(self.ambient_slider.setValue)
        self.diffuse_slider.valueChanged.connect(self.glWidget.setDiffuse)
        self.glWidget.diffuse_changed.connect(self.diffuse_slider.setValue)
        self.position_slider.valueChanged.connect(self.glWidget.setPosition)
        self.glWidget.position_changed.connect(self.position_slider.valueChanged)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        mainLayout.addWidget(self.ambient_slider)
        mainLayout.addWidget(self.diffuse_slider)
        mainLayout.addWidget(self.position_slider)
        self.setLayout(mainLayout)

        self.ambient_slider.setValue(1)

        self.setWindowTitle("Lab 4")

    def createSlider(self):
        slider = QSlider(Qt.Vertical)

        slider.setRange(0, 10)
        slider.setSingleStep(1)
        slider.setPageStep(15)
        slider.setTickInterval(15)
        slider.setTickPosition(QSlider.TicksRight)

        return slider

class GLWidget(QOpenGLWidget):
    ambient_changed = pyqtSignal(int)
    diffuse_changed = pyqtSignal(int)
    specular_changed = pyqtSignal(int)
    position_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        self.object = 0
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0

        self.lastPos = QPoint()

        self.radius = 1.0
        self.latitudes = 100
        self.longitudes = 100

        self.theta = 0
        self.height = 0

        self.value = 0

        # light source position
        self.position = [1.0, 10.0, 1.0, 1.0]
        # light ambient
        self.ambient = [.2, .2, .2, 1.0]
        # light diffuse
        self.diffuse = [1.0, 1.0, 1.0, 1.0]
        # light specular
        self.specular = [1.0, 1.0, 1.0, 1.0]

        # types
        self.surface = GL_SMOOTH
        self.colorize = GL_DEPTH_TEST  # init GL_DEPTH_TEST

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(600, 600)

    def setPosition(self, val):
        self.position = [1.0 * (val - 1.0), 10.0 * (val - 10.0), 1.0 * (val - 1.0), 1.0 * (val - 1.0)]
        self.update()

    def setAmbient(self, val):
        self.ambient = [.2 * val, .2 * val, .2 * val, 1.0 * val]
        self.update()

    def setDiffuse(self, val):
        self.diffuse = [1.0 * val, 1.0 * val, 1.0 * val, 1.0 * val]
        self.update()

    def setSpecular(self, val):
        self.specular = [1.0 - (val / 10), 1.0 - (val / 10), 1.0 - (val / 10), 1.0 - (val / 10)]
        print(self.specular)
        self.update()

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.update()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.update()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.update()

    def light(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_NORMALIZE)
        glLightfv(GL_LIGHT0, GL_POSITION, self.position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)

    def initializeGL(self):
        self.light()

        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glEnable(self.colorize)
        glDepthFunc(GL_LESS)
        glShadeModel(self.surface)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslated(0.0 + float(self.position[1] / 2000), 0.0 + float(self.position[1] / 2000), -10.0 + float(self.position[2] / 1000))
        self.light()
        glScalef(0.05 + float(self.position[0] / 100), 0.05 + float(self.position[0] / 100), .05 + float(self.position[0] / 100))

        glRotated(-self.xRot / 16, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16, 0.0, 0.0, 1.0)

        self.makeObject()

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return glViewport((width - side) // 2, (height - side) // 2, side, side)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        glMatrixMode(GL_MODELVIEW)
        GL_PROJECTION

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)

        elif event.buttons() & Qt.RightButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)

        self.lastPos = event.pos()

    def makeObject(self):
        for i in range(20, self.latitudes - 20):
            lat = pi * (-0.5 + float(float(i - 1) / float(self.latitudes)))
            z0 = sin(lat)
            zr0 = cos(lat)

            lat0 = pi * (-0.5 + float(float(i) / float(self.latitudes)))
            z1 = sin(lat0)
            zr1 = cos(lat0)

            glBegin(GL_QUAD_STRIP)

            for j in range(0, self.longitudes + 1):
                lng = 2 * pi * float(float(j - 1) / float(self.longitudes))
                x = cos(lng)
                y = sin(lng)
                glNormal3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr0, y * zr0, z0)
                glNormal3f(x * zr1, y * zr1, z1)
                glVertex3f(x * zr1, y * zr1, z1)

            glEnd()

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = Window()
    window.show()

    sys.exit(app.exec_())