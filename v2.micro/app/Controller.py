from .actors import View 
from . import EventHandlerQueue

from numbers import Number
import time


from abc import ABC, abstractmethod
from enum import Enum

from typing import Iterable, List, Tuple, Callable


import json

from logging import Logger


import threading

      




class Controller:

    
    """
    this is the master mega ultra thread
    this is where all the classed get started, this is where all the dependencies are injected, 
    deamons started and all the queue actors get assigned
    """


    def __init__(self, logger: Logger, headless: bool = True ) -> None:
        super().__init__()
        self.headless: bool = headless

        #setup dependencies
        self.logger: Logger = logger
        
        
        #setup consumers
        self.stage: EventHandlerQueue = EventHandlerQueue()

        self.stageing()
        
        #setup models
        self.setup_models()
        
        self.debug()
        
        
    def stageing(self):
        
        
        
        if not self.headless:
            self.setup_view()
            
            
    def setup_view(self):
        self.__view:View = View(self.stage)
        
    def setup_telescope(self):
        self.__alpaca:Alpaca = Alpaca(self.stage)
        
    def setup_models(self):
        self.__camera_model: GenericCamModel = ZwoAsiModel(self.logger)
        
    def debug(self):
        print(self.camera_model.list_all_cameras())
    
    
    def connect_camera(self):
        self.camera_model.setup_cam()
    
    def connect_telescope(self):
        self.notify(DataDescriptor.LookupTelescopes)
    
    def start_imageloop(self):
        self.notify(DataDescriptor.StartGuiding)
        
        self.imageloop_active = True
        self.imageloop_thread = threading.Thread(target=self.imageloop, args=(self, ))
        
        self.imageloop_thread.start()
        
    def imageloop(self):
        while(self.imageloop_active):
            self.take_image()
            
    def end_imageloop(self):
        self.imageloop_active = False
        self.imageloop_thread.join()
        
        self.notify(DataDescriptor.StopGuiding)
            
    
    def take_image(self):
        image = self.camera_model.get_image_from_camera()
        image = self.camera_model.auto_freshholding(image)
        self.cog = self.camera_model.calculate_center_of_gravity(image)
        
        self.notify(DataDescriptor.COG)
        

    