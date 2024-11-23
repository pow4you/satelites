from app import EventAddress, EventHandlerQueue, Adressable

class Actor(Addressable):
    def __init__(self, address:EventAddress, stage:EventHandlerQueue) -> None:
        super().__init__(address)
        
        self._stage:EventHandlerQueue = stage
        
        self._stage.enroll(self)