#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""A heart of ugm. This module implements core classes for ugm to work.
It should be ran as a script in MAIN thread or using UgmEngine.run()."""
import sys
from PyQt4 import QtGui, QtCore, Qt
import Queue

from obci.gui.ugm import ugm_config_manager
from obci.gui.ugm import ugm_stimuluses


from obci.utils import context as ctx

class UgmField(ugm_stimuluses.UgmRectStimulus):
    """For now, just to express it..."""
    pass

class UgmGenericCanvas(QtGui.QWidget):
    """This class represents canvas for ugm, an object holding 
    all stimuluses. As it is simple pyqt widget it might be embedded 
    in some other pyqt elements."""

    def __init__(self, p_parent, p_config_manager):
        """Create widget, create all children from p_config_manager,
        store p_config_manager."""
        QtGui.QWidget.__init__(self, p_parent)
        self.setWindowTitle('UGM')

        self._config_manager = p_config_manager
        self._create_children()

    def _create_children(self):
        """Create ugm fields as children."""
        for i_field_config in self._config_manager.get_ugm_fields():
            UgmField(self, i_field_config)

    def _get_width(self):
        """Return self`s width."""
        return self.frameSize().width()
    def _get_height(self):
        """Return self`s height."""
        return self.frameSize().height()

    def resizeEvent(self, event):
        """Redefine the method so that all children are updated."""
        self.update_geometry()
# --------------------------------------------------------------------------
# -------------- PUBLIC INTERFACE ------------------------------------------
    def get_config_manager(self):
        """Return stored config manager."""
        return self._config_manager

    def update_geometry(self):
        """Update all children. The method is fired explicitly very time 
        config manager changed it`s state and widgets need to be redrawn
        (not rebuilt)."""
        for i in self.children():
            i.update_geometry()

    width = property(_get_width)
    height = property(_get_height)

# -------------- PUBLIC INTERFACE ------------------------------------------
# --------------------------------------------------------------------------

class SpellerWindow(QtGui.QFrame):
    """Main frame using UgmGenericCanvas and other usefull widgets."""
    def __init__(self, p_parent, p_config_manager):
        """Init UgmGenericCanvas and other widgets, lay them out."""
        QtGui.QFrame.__init__(self, p_parent)
        l_hbox = QtGui.QVBoxLayout()
        l_hbox.setContentsMargins(0,0,0,0)

        #self.text = QtGui.QLineEdit()
        #l_hbox.addWidget(self.text)

        self.canvas = UgmGenericCanvas(self, p_config_manager)       
        l_hbox.addWidget(self.canvas)

        self.setLayout(l_hbox)

    def update_geometry(self):
        """Update self`s canvas geometry. Fired when config manager has
        updated it`s state."""
        self.canvas.update_geometry()

class UgmMainWindow(QtGui.QMainWindow):
    mousePressSignal = QtCore.pyqtSignal(QtGui.QMouseEvent)
    keyPressSignal = QtCore.pyqtSignal(QtGui.QKeyEvent)
    """Qt main window for ugm."""
    def __init__(self, p_config_manager):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._config_manager = p_config_manager
        self.view = SpellerWindow(self, p_config_manager)
        self.setCentralWidget(self.view)

    def update(self):
        """Update self`s view.Fired when config manager has
        updated it`s state."""
        self.view.update_geometry()
    def rebuild(self):
        """Delete and once again create self`s central widget."""
        self.view.deleteLater()
        self.view = SpellerWindow(self, self._config_manager)
        self.setCentralWidget(self.view)

    def mousePressEvent(self, event):
        super(UgmMainWindow, self).mousePressEvent(event)
        self.mousePressSignal.emit(event)

    def keyPressEvent(self, event):
        super(UgmMainWindow, self).keyPressEvent(event)
        self.keyPressSignal.emit(event)


class UgmEngine(QtCore.QObject):
    """A class representing ugm application. It is supposed to fire ugm,
    receive messages from outside (UGM_UPDATE_MESSAGES) and send`em to
    ugm pyqt structure so that it can refresh."""
    def __init__(self, p_config_manager, p_connection, context=ctx.get_dummy_context('UgmBlinkingEngine')):
        """Store config manager."""
        super(UgmEngine, self).__init__()
        self.context = context
        self.connection = p_connection
        self._config_manager = p_config_manager
        self.ugm_rebuild = QtCore.pyqtSignal()
        self.connect(self, QtCore.SIGNAL("ugm_rebuild"), 
                     self.ugm_rebuild_signal)
        self.ugm_update = QtCore.pyqtSignal()
        self.connect(self, QtCore.SIGNAL("ugm_update"), 
                     self.ugm_update_signal)


        self.queue = Queue.Queue()
        self.mutex = Qt.QMutex()
        self.mgr_mutex = Qt.QMutex()

    def queue_message(self, l_msg):
        """Insert message to queue waiting to be displayed."""
        self.mutex.lock()
        self.queue.put(l_msg)
        self.mutex.unlock()

    def _timer_on_run(self):
        """Fired on run once time."""
        self.update_gui_timer = QtCore.QTimer()
        self.update_gui_timer.connect(self.update_gui_timer,QtCore.SIGNAL("timeout()"),self.timer_update_gui)
        self.update_gui_timer.start(10)

        # Well, as for below ... qtwindow.showFullScreen() is somehow broken (see documentation)
        # It doesn`t set window as active and keyEvent don`t work, needed dirty hack as below...:(
        self.tmp_timer = QtCore.QTimer()
        self.tmp_timer.connect(self.tmp_timer, QtCore.SIGNAL("timeout()"), self._window.activateWindow)
        self.tmp_timer.setSingleShot(True)
        self.tmp_timer.start(2000)


    def timer_update_gui(self):
        """Fired very often - clear self.queue and update gui with those messages."""
        self.mutex.lock()
        if self.queue.qsize() == 0:
            self.mutex.unlock()
            return
        elif (self.queue.qsize() > 5):
            self.context['logger'].warning("Warning! Queue size is: "+str(self.queue.qsize()))

        while True:
            try:
                msg = self.queue.get_nowait()
            except Queue.Empty:
                break
            else:
                self.update_from_message(
                    msg.type, msg.value)
        self.mutex.unlock()


    @QtCore.pyqtSlot(QtGui.QMouseEvent)
    def mousePressEvent(self, event):
        try:
            self.connection.send_mouse_event(event.button())
        except Exception, e:
            self.context['logger'].error("Could send mouse event to connection. Error: "+str(e)) 

    @QtCore.pyqtSlot(QtGui.QKeyEvent)
    def keyPressEvent(self, event):
        try:
            self.connection.send_keyboard_event(event.key())
        except Exception, e:
           self.context['logger'].error("Could send keyboard event to connection. Error: "+str(e)) 


    def run(self):
        """Fire pyqt application with UgmMainWindow. 
        Refire when app is being closed. (This is justified as if 
        ugm_config_manager has changed its state remarkably main window
        needs to be completely rebuilt."""
        self.context['logger'].info("ugm_engine run")
        l_app = QtGui.QApplication(sys.argv)
        self._window = UgmMainWindow(self._config_manager)
        self._window.showFullScreen()
        #self._window.show()
        #self._window.showMaximized()
        self._timer_on_run()
        self._window.keyPressSignal.connect(self.keyPressEvent)
        self._window.mousePressSignal.connect(self.mousePressEvent)
        l_app.exec_()
        self.context['logger'].info('ugm_engine main window has closed')

    def control(self, ctr):
        self.context['logger'].info("Got control message "+str(ctr))
        if ctr.key == 'hide':
            self._window.hide()

    def update_from_message(self, p_msg_type, p_msg_value):
        """Update ugm from config defined by dictionary p_msg_value.
        p_msg_type must be 0 or 1. 0 means that ugm should rebuild fully,
        2 means that config hasn`t changed its structure, only attributes, 
        so that ugm`s widget might remain the same, 
        they should only redraw."""
        self.mgr_mutex.lock()
        if self._config_manager.update_message_is_full(p_msg_type):
            self.context['logger'].info('ugm_engine got full message to update.')
            self._config_manager.set_full_config_from_message(p_msg_value)
            self.update_or_rebuild()
            self.mgr_mutex.unlock()
        elif self._config_manager.update_message_is_simple(p_msg_type):
            self.context['logger'].debug('ugm_engine got simple message to update.')
            self._config_manager.set_config_from_message(p_msg_value)
            self.update()
            self.mgr_mutex.unlock()
        else:
            self.mgr_mutex.unlock()
            self.context['logger'].error("Wrong UgmUpdate message type!")
            raise Exception("Wrong UgmUpdate message type!")

    def update_from(self, p_ugm_configs):
        self.mgr_mutex.lock()
        self._config_manager.set_configs(p_ugm_configs)
        self.update()
        self.mgr_mutex.unlock()

    def update_or_rebuild(self):
        """Update or rebuild ugm depending on config manager`s decison..."""
        if self._config_manager.old_new_fields_differ():
            self.rebuild()
        else:
            self.update()

    def update(self):
        """Fired when self._config_manager has changed its state, but only 
        stimuluses`es attributes, not their number or ids."""
        self.context['logger'].debug("ugm_engine update")
        self.emit(QtCore.SIGNAL("ugm_update"))

    def rebuild(self):
        """Fired when self._config_manager has changed its state 
        considerably - eg number of stimuluses or its ids changed.
        In that situation we need to rebuild gui, not only refresh.
        Send signal, as we need gui to be rebuilt in the main thread."""
        self.context['logger'].info("ugm_engine rebuild")
        self.emit(QtCore.SIGNAL("ugm_rebuild"))

    def ugm_rebuild_signal(self):
        """See __init__ and rebuild."""
        self._window.rebuild()

    def ugm_update_signal(self):
        """See __init__ and update."""
        self._window.update()


def run():
    try:
        CONF = sys.argv[1]
    except IndexError:
        CONF = ''
    finally:
        # Run ugm engin from default config or config from prompt
        if CONF == '':
            UgmEngine(ugm_config_manager.UgmConfigManager(), None).run()
        else:
            UgmEngine(ugm_config_manager.UgmConfigManager(CONF), None).run()
			
if __name__ == '__main__':
	run()




