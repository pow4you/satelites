from model import GenericCamModel

import zwoasi as asi
import os
import numpy as np
import time
from typing import *

from logging import Logger

class ZwoAsiModel(GenericCamModel):
    
    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)

        dirname = os.path.dirname(__file__)
        asi.init(f"{dirname}\\AsiSDK\\ASICamera2.dll")

        if not self.find_camera_or_first():
            self.logger.warning("No camera found! call \"find_camera_or_first()\" to connect a camera!")
        
        if self.is_camera_connected():
            self.setup_cam()
        else: 
            self.logger.warning("Can't setup camera ")
  
  
    
    def list_all_cameras(self) -> List[str]:
        """Looksup connected cameras and returns list of names.

        Returns:
            List[str]: Returns a text list with all connected cameras. Empty if none are found.
        """
        
        num_cameras = asi.get_num_cameras()
        if num_cameras == 0:
            return []

        return asi.list_cameras()
    
    def find_camera_or_first(self, name:str = None) -> bool:
        """ finds the first camera connected or connects to te camera with the asigned name

        Args:
            name (str, optional): Optional camera name. Defaults to None.

        Returns:
            bool: True when succseeded to connect, false when it couldnt connects
        """
        num_cameras = asi.get_num_cameras()
        if num_cameras == 0:
            self.logger.warning("No cameras connected")
            self._camera_connected = False
            return False

        cameras = asi.list_cameras()

        if name:
            try:
                id = cameras.index(name)
                self.camera = asi.Camera(id)
                self._camera_connected = True
                return True
            except ValueError:
                self.logger.info("Couldnt find camera by name, returning first")
                pass
        
        self.camera =  asi.Camera(0)
        self._camera_connected = True
        return True

    def setup_cam(self):
        """Sets up the camerasettings / resets them

        Raises:
            ValueError
        """
        
        if not self.is_camera_connected():
            raise ValueError()
        
        #set image output to 8-bit mono
        self.camera.set_image_type(asi.ASI_IMG_RAW8)
                
        #reset all settings to default
        controls = self.camera.get_controls()
        #for control in controls:
        #    self.camera.set_control_value(controls[control]['ControlType'], controls[control]['DefaultValue'])
        #    self.logger.debug("reset control: %s", control)
        #self.logger.info("Values reset")
        
        
        #set usb bandwidth to minimum
        self.camera.set_control_value(
            asi.ASI_BANDWIDTHOVERLOAD, 
            self.camera.get_controls()['BandWidth']['MinValue']
        )
        self.logger.info("bandwidth limit set")
        
        
        #set autoexposure if exists
        if 'Exposure' in controls and controls['Exposure']['IsAutoSupported']:
            self.logger.info('Enabling auto-exposure mode')
            self.camera.set_control_value(
                asi.ASI_EXPOSURE,
                controls['Exposure']['DefaultValue'],
                auto=True
            )

            if 'Gain' in controls and controls['Gain']['IsAutoSupported']:
                self.logger.info('Enabling automatic gain setting')
                self.camera.set_control_value(
                    asi.ASI_GAIN,
                    controls['Gain']['DefaultValue'],
                    auto=True
                )

            # Keep max gain to the default but allow exposure to be increased to its maximum value if necessary
            self.camera.set_control_value(controls['AutoExpMaxExpMS']['ControlType'], controls['AutoExpMaxExpMS']['MaxValue'])

        #mark camera as having undergone initial setup
        self._camera_setup = True

    def get_camera_info(self) -> dict:
        """Collects and returns camera info of the connected camera

        Raises:
            ValueError
            
        Returns:
            dict: dict filled with information about the camera
        """
        if not self.is_camera_connected():
            raise ValueError()
        
        return self.camera.get_camera_property()

    def close_cam(self):
        """Resets settings, closes streams and disconnects camera

        Raises:
            ValueError
            ValueError
        """
        
        if not self.is_camera_connected():
            raise ValueError()
        
        if not self.is_camera_setup():
            raise ValueError()
        
        self.camera.close()



    def enable_video(self):
        """Enables video mode of camera

        Raises:
            ValueError
            ValueError
        """
        
        
        if not self.is_camera_connected():
            raise ValueError()
        
        if not self.is_camera_setup():
            raise ValueError()
        
        self._video_enabled = True
        self.camera.start_video_capture() 

    def disable_video(self):
        """Disables video mode of camera

        Raises:
            ValueError
            ValueError
        """
        
        if not self.is_camera_connected():
            raise ValueError()
        
        if not self.is_camera_setup():
            raise ValueError()
        
        self._video_enabled = False
        self.camera.stop_video_capture()

    

    def get_image_from_camera(self) -> np.ndarray[np.uint8]:
        if self.is_video_enabled():
            
            #capture_video_frame() will wait indefinitely unless a timeout has been given. The SDK suggests that the timeout value, in milliseconds, should be twice the exposure plus 500 ms.
            timeout = (self.camera.get_control_value(asi.ASI_EXPOSURE)[0] / 1000) * 2 + 500
            self.camera.default_timeout = timeout
            
            return self.camera.capture_video_frame()
        else:
            return self.camera.capture()
        

