from app import Actor

from typing import Tuple

from logging import Logger


from alpaca import discovery, management
from alpaca.telescope import *

import json

class Alpaca(Actor):
    """ Alpaca interface handels communications with the telescope.
    
    TODO: I dislike my decision to use a real observer pattern here. it just seems a little bulky. i think it's still useful for the ui, but this part should really just be directly pulling pics from the cam in c++ 

    Args:
        Observer (_type_): _description_
    """
    
    def __init__(self, logger: Logger):
        super().__init__()
        
        self.logger = logger
        
    def list_alpaca_hosts(self):
        return discovery.search_ipv4()
        
    def _telescopes(self):
        self.telescope = Telescope(svrs[0], 0)
        
    def calibrate_telescope(self):
        svrs = discovery.search_ipv4()  # Note there is an IPv6 function as well

        self.telescope = Telescope(svrs[0], 0)
        
        #calculating the pixel scale for the setup
        #lense LA4725-UV: focal length: 75mm
        #pixel scale: 3.8 micons
        pixel_scale = self.calculate_arcseconds_per_pixel(3.8, 75)

        camera_values_for_guider_calibration = {   
            "PixelScale": pixel_scale,
            "Angle": 0,
            "IsInverted": False,
            "CamNr":1
        }

        self.telescope.Action("guidercalivalues", json.dumps(camera_values_for_guider_calibration))

    def start_guiding(self):
        answerNotChecked = self.telescope.CommandString("GuideStartCam1", "true")
        
    def stop_guiding(self):
        answerNotChecked = self.telescope.CommandString("GuideStopCam1", "true")

        
    
    def calculate_arcseconds_per_pixel(self, pixel_scale: float, focal_length: float) -> float:
        """calculates field of view from pixels and focal length

        Args:
            pixel_scale (float): pixel size in microns
            focal_length (float): focal length in mm

        Returns:
            float: field of view per pixel in arcseconds 
        """
        return (pixel_scale* focal_length ) / 206.265



        
    def update(self, subject: Subject, data_description: DataDescriptor) -> None:
        match data_description:
            case DataDescriptor.COG:
                center:Tuple[float, float] = subject.cog
            
                self.update_guideposition(center)
                
            case DataDescriptor.LookupTelescopes:
                self.find_telescope()
            
            case DataDescriptor.StartGuiding:
                self.start_guiding()
                
            case DataDescriptor.StopGuiding:
                self.stop_guiding()
                
            case _:
                self.logger.debug("lmao")

        pass
    
    def update_guideposition(self, cog: Tuple[float, float] ): #TODO: Figure this out
        """_summary_

        Args:
            cog (Tuple[float, float]): _description_
        """
        
        #integers from the camera center
        cam_position = {
            "X": cog[0],
            "Y": cog[1]
        }

        self.telescope.Action("guidenewcentroidcam1", json.dumps(cam_position))
        