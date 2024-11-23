#from model import ValueError

from abc import ABC, abstractmethod
from typing import *
import numpy as np
from logging import Logger
import threading
import time
import io
import cv2 


class GenericCamModel(ABC):

    def __init__(self, logger: Logger) -> None:
        super().__init__()
        
        self.logger: Logger = logger
        
        #protected
        self._camera_connected: bool = False
        self._camera_setup: bool = False
        self._video_enabled: bool = False
        
        #private
        self.__video_stream:cv2.VideoWriter = None
        self.__video_capture_thread:threading.Thread = None
        self.__video_capturing: bool = False

    @abstractmethod
    def list_all_cameras(self) -> List[str]:
        """Looksup connected cameras and returns list of names.

        Raises:
            NotImplementedError:
        
        Returns:
            List[str]: Returns a text list with all connected cameras. Empty if none are found.
        """
        raise NotImplementedError()
        

    @abstractmethod
    def find_camera_or_first(self, name: str = None) -> bool:
        """Finds the first camera connected or connects to te camera with the asigned name
        
        Args:
            name (str, optional): Optional camera name. Defaults to None.

        Raises:
            NotImplementedError:
        
        Returns:
            bool: True when succseeded to connect, false when it couldnt connects
        """
        raise NotImplementedError()
    
    def is_camera_connected(self) -> bool:
        """Returns the internal variable to check if a camera is connected

        Raises:
            NotImplementedError:
        
        Returns:
            bool: True if a camera is connected
        """
        return self._camera_connected

    @abstractmethod
    def setup_cam(self):
        """Sets up the camerasettings / resets them

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()
    
    def is_camera_setup(self) -> bool:
        """Returns the internal variable to check if a camera is setup to run

        Returns:
            bool: True if a camera has undergone setup
        """
        return self._camera_setup

    @abstractmethod
    def get_camera_info(self) -> dict:
        """Collects and returns camera info of the connected camera

        Raises:
            NotImplementedError

        Returns:
            dict: dict filled with information about the camera
        """
        raise NotImplementedError()
    
    @abstractmethod
    def close_cam(self):
        """Resets settings, closes streams and disconnects camera

        Raises:
            NotImplementedError: 
        """
        raise NotImplementedError()

    @abstractmethod
    def enable_video(self):
        """Enables video mode of camera

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    @abstractmethod
    def disable_video(self):
        """Disables video mode of camera

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def is_video_enabled(self) -> bool:
        return self._video_enabled

    @abstractmethod
    def get_image_from_camera(self) -> np.ndarray[np.uint8]:
        """Captures an 8-bit mono image from camera, independent of current camera mode

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()
    
    def start_video_capture(self, file_path:str, fps:int = 30 ):
        """Starts capturing a video to a given filepath.

        Args:
            file_path (str): Filepath the video will be saved to. The extension type automatically determins the encoding scheme.
            fps (int, optional): Goal FPS of the video. If the expsure time is too long it will recycle the last image for multible frames. Defaults to 30.

        Raises:
            ValueError: If a video is already being captured this function will raise an error.
        """
        if self.video_capture_thread.is_alive() or self.video_capturing:
            raise ValueError("Video already capturing")
            
        
        fourcc = self.__get_fourcc(file_path)
        self.video_stream = cv2.VideoWriter(file_path, fourcc, fps, isColor=False)
        
        self.video_capturing = True
        self.video_capture_thread = threading.Thread(target=self.__video_capture_thread_function, args=(self, fps, ))
        
        self.video_capture_thread.start()
        
        pass
    
    def stop_video_capture(self):
        """Stops capturing the Video.

        Raises:
            ValueError: If no video is being captured this error will be triggered.
        """
        if not (self.video_capture_thread.is_alive() and self.video_capturing):
            raise ValueError("No video capturing")
        
        self.video_capture_thread.join()
        
        self.video_stream.release()
        
        self.video_capturing = False
        
        
    def __get_fourcc(self, filename):
        """automatically determens encoding sceme based on filetype

        Args:
            filename (string): filename

        Raises:
            ValueError: type not recognised

        Returns:
            _type_: video encoder type
        """
        ext = filename.split('.')[-1].lower()
        match ext:
            case 'avi':
                return cv2.VideoWriter_fourcc(*'XVID')
            case 'mp4':
                return cv2.VideoWriter_fourcc(*'mp4v')
            case 'mov':
                return cv2.VideoWriter_fourcc(*'avc1')
            case _:
                raise ValueError(f"Unsupported file extension: {ext}")
        
    def __video_capture_thread_function(self, fps:int = 30):
        """Captures a video

        Args:
            fps (int, optional): how many fps the video should have. Defaults to 30.
        """
        while self.video_capturing:
            img = self.get_image_from_camera()
            
            self.video_stream.write(img)
            
            
            time.sleep(1 / fps)

    
    def auto_freshholding(self, image:np.ndarray[np.uint8]) -> np.ndarray[np.uint8]:
        """automatically calulate a freshold value and apply it across all pixels

        Args:
            image (np.ndarray[np.uint8])

        Returns:
            np.ndarray[np.uint8]: thresholded image
        """ 
        brightest = int(np.max(image))
        darkest = int(np.min(image))
        
        threshold = int((2* (brightest + darkest)) / 3)
        image[image < threshold] = 0

        return image.astype(np.uint8)

    def calculate_center_of_gravity(self, image:np.ndarray[np.uint8]) -> Tuple[float, float]:
        """calculates the center of gravity of an image using their intensity values as weights 

        Args:
            image (np.ndarray[np.uint8]): 

        Raises:
            ValueError: _description_

        Returns:
            Tuple[float, float]: _description_
        """
        height, width = image.shape
        y_indices = np.arange(height)
        x_indices = np.arange(width)

        total_intensity = np.sum(image)
        if total_intensity == 0:
            raise ValueError("Image has no intensity")
        
        cols = np.sum(image, axis=0)
        rows = np.sum(image, axis=1)

        x_center = float( np.sum(x_indices * cols) / total_intensity ) - (width / 2)
        y_center = float( np.sum(y_indices * rows) / total_intensity ) - (height / 2)
        
        return (x_center, y_center)

    
