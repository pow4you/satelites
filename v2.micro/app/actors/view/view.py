from app import EventHandlerQueue, EventAddress
from .. import Actor

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from . import UI_MainWindow
from .. import Actor

from enum import Enum

from threading import Thread, Event
import time



class CameraStatus(Enum):
    Error = -1
    
    Empty = 0
    
    Loading = 1
    Unset = 3
    Connected = 4

class View(Actor):
    def __init__(self, stage:EventHandlerQueue ):
        super().__init__(address = EventAddress.ViewMain, stage = stage)
        
        self.app = QApplication(sys.argv)
        
        self.main_window = QMainWindow()
        
        # Load the UI
        self.ui = UI_MainWindow()
        self.ui.setupUi(self.main_window)

        # Connect widgets
        self.connect_widgets()
        
        self.set_default_values()
        
        Thread(target=self.view_deamon, daemon=True).start()
        
        
        self.main_window.show()
        self.app.exec_()
        
        
        
        
        
        

    def connect_widgets(self):
        self.ui.ConnectCameraStatus.clicked.connect(self.connect_camera_status_clicked)
        
        pass
        

    def set_default_values(self):
        self.ui.ConnectCameraStatus.setText("Looking dor cameras :)")
        self.ui.CameraSelector.clear()
        
    
    
    def view_deamon(self):
        
        
        self.camstate = CameraStatus.Loading
        
        Thread(target=self.camera_selector_loading_loop, daemon=True).start()
        
        
        
        
        
        
        
    
    def camera_selector_loading_loop(self):
        print("asdadasdasdasd")
        
        sleep_ms = 1000
        counter = 0
        
        while(counter < 15 and self.camstate == CameraStatus.Loading):
            dots = counter % 3 + 1
            loadstr = "Loading"+"".join(["."]*dots)
            print(loadstr)
            
            self.ui.CameraSelector.clear()
            self.ui.CameraSelector.addItem(loadstr)
            
            time.sleep(sleep_ms/1000)
            counter += 1
            
        if self.camstate == CameraStatus.Loading:
            self.camstate = CameraStatus.Empty
            self.ui.CameraSelector.clear()
            
        
            
            
        
        

    def connect_camera_status_clicked(self):
        #self.controller.connect_camera()
        pass


        
        
    def update(self, subject) -> None:
        pass
        

