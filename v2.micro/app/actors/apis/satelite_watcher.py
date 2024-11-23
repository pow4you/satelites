from app import EventHandlerQueue, Actor
from app import EventAddress, EventMessageDescriptor


import geopy
import geopy.location

class SateliteWatcher(Actor):
    def __init__(self, stage:EventHandlerQueue):
        super().__init__(EventAddress.SateliteWatcher, stage=stage)
        
        
        self.sat_lookahead_time = () #mins
        self.stage.broadcast()
        
        
        self.add_processor(EventMessageDescriptor.SateliteWatcherProcessors.FindSatsByPosition, self.number_action_processor)
        self.add_processor(EventMessageDescriptor.SateliteWatcherMesseges.FindSatsByLatLon, self.object_action_processor)
        self.add_processor(EventMessageDescriptor.FindSatsByAddress, self.standard_action_processor)
        
        
        
    def find_targets_by_position(self):
        """Gets upcoming sats by device Position
        """
        
        sats:List[Target] = 
        
        self._stage.broadcast()
        
        pass
    
    def find_targets_by_latlon(self, latitude:Number, longitude:Number):
        """Gets upcoming sats by Latitude and Longitude
        """
        pass
    
    