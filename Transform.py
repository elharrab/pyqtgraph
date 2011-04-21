# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from Point import Point
import numpy as np

class Transform(QtGui.QTransform):
    """Transform that can always be represented as a combination of 3 matrices: scale * rotate * translate
    
    This transform always has 0 shear."""
    def __init__(self, init=None):
        QtGui.QTransform.__init__(self)
        self.reset()
        
        if isinstance(init, dict):
            self.restoreState(init)
        elif isinstance(init, Transform):
            self._state = {
                'pos': Point(init._state['pos']),
                'scale': Point(init._state['scale']),
                'angle': init._state['angle']
            }
            self.update()
        elif isinstance(init, QtGui.QTransform):
            self.setFromQTransform(init)

    def reset(self):
        self._state = {
            'pos': Point(0,0),
            'scale': Point(1,1),
            'angle': 0.0  ## in degrees
        }
        self.update()
        
    def setFromQTransform(self, tr):
        p1 = Point(tr.map(0., 0.))
        p2 = Point(tr.map(1., 0.))
        p3 = Point(tr.map(0., 1.))
        
        dp2 = Point(p2-p1)
        dp3 = Point(p3-p1)
        
        self._state = {
            'pos': Point(p1),
            'scale': Point(dp2.length(), dp3.length()),
            'angle': np.arctan2(dp2[1], dp2[0]) * 180. / np.pi
        }
        self.update()
        
    def translate(self, *args):
        """Acceptable arguments are: 
           x, y
           [x, y]
           Point(x,y)"""
        t = Point(*args)
        self.setTranslate(self._state['pos']+t)
        
    def setTranslate(self, *args):
        """Acceptable arguments are: 
           x, y
           [x, y]
           Point(x,y)"""
        self._state['pos'] = Point(*args)
        self.update()
        
    def scale(self, *args):
        """Acceptable arguments are: 
           x, y
           [x, y]
           Point(x,y)"""
        s = Point(*args)
        self.setScale(self._state['scale'] * s)
        
    def setScale(self, *args):
        """Acceptable arguments are: 
           x, y
           [x, y]
           Point(x,y)"""
        self._state['scale'] = Point(*args)
        self.update()
        
    def rotate(self, angle):
        """Rotate the transformation by angle (in degrees)"""
        self.setRotate(self._state['angle'] + angle)
        
    def setRotate(self, angle):
        """Set the transformation rotation to angle (in degrees)"""
        self._state['angle'] = angle
        self.update()

    def __div__(self, t):
        """A / B  ==  B^-1 * A"""
        dt = t.inverted()[0] * self
        return Transform(dt)
        
    def __mul__(self, t):
        return Transform(QtGui.QTransform.__mul__(self, t))

    def saveState(self):
        p = self._state['pos']
        s = self._state['scale']
        return {'pos': (p[0], p[1]), 'scale': (s[0], s[1]), 'angle': self._state['angle']}

    def restoreState(self, state):
        self._state['pos'] = Point(state.get('pos', (0,0)))
        self._state['scale'] = Point(state.get('scale', (0,0)))
        self._state['angle'] = state.get('angle', 0)
        self.update()

    def update(self):
        QtGui.QTransform.reset(self)
        ## modifications to the transform are multiplied on the right, so we need to reverse order here.
        QtGui.QTransform.translate(self, *self._state['pos'])
        QtGui.QTransform.rotate(self, self._state['angle'])
        QtGui.QTransform.scale(self, *self._state['scale'])

    def __repr__(self):
        return str(self.saveState())
        
    def matrix(self):
        return np.array([[self.m11(), self.m12(), self.m13()],[self.m21(), self.m22(), self.m23()],[self.m31(), self.m32(), self.m33()]])
        
if __name__ == '__main__':
    import widgets
    import GraphicsView
    from functions import *
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    win.show()
    cw = GraphicsView.GraphicsView()
    #cw.enableMouse()  
    win.setCentralWidget(cw)
    s = QtGui.QGraphicsScene()
    cw.setScene(s)
    
    b = QtGui.QGraphicsRectItem(-5, -5, 10, 10)
    b.setPen(QtGui.QPen(mkPen('y')))
    t1 = QtGui.QGraphicsTextItem()
    t1.setHtml('<span style="color: #F00">R</span>')
    s.addItem(b)
    s.addItem(t1)
    
    tr1 = Transform()
    tr2 = Transform()
    tr3 = QtGui.QTransform()
    tr3.translate(20, 0)
    tr3.rotate(45)
    print "QTransform -> Transform:", Transform(tr3)
    
    print "tr1:", tr1
    
    tr2.translate(20, 0)
    tr2.rotate(45)
    print "tr2:", tr2
    
    dt = tr2/tr1
    print "tr2 / tr1 = ", dt
    
    print "tr2 * tr1 = ", tr2*tr1
    
    w1 = widgets.TestROI((0,0), (50, 50))
    w2 = widgets.TestROI((0,0), (150, 150))
    s.addItem(w1)
    s.addItem(w2)
    w1Base = w1.getState()
    w2Base = w2.getState()
    def update():
        tr1 = w1.getGlobalTransform(w1Base)
        tr2 = w2.getGlobalTransform(w2Base)
        t1.setTransform(tr1 * tr2)
        w1.setState(w1Base)
        w1.applyGlobalTransform(tr2)
    w1.sigRegionChanged.connect(update)
    w2.sigRegionChanged.connect(update)
    
    