from . import EventMessageDescriptor, EventAddress

from numbers import Number
import time
from queue import Empty, Queue
from threading import Thread, Lock

#from statemachine import StateMachine, State

from abc import ABC#, abstractmethod

from typing import Iterable, List, Tuple, Callable

class EventMessage():
    def __init__(self, messege, title:str = "", origin:EventAddress = EventAddress.Undefined, destination:List[EventAddress] = [EventAddress.All], data_descriptor: EventMessageDescriptor = EventMessageDescriptor.Undefined ) -> None:
        self.__messege = messege
        self.title:str = title
        self.__data_descriptor: EventMessageDescriptor = data_descriptor
        
        self.__origin: EventAddress = origin
        
        if len(destination) < 1:
            destination.append(EventAddress.Void)    
        self.__destination: List[EventAddress] = destination
    
    def get_messege(self):
        return self.__messege
    
    def is_in_destination(self, local_destiantion: EventAddress) -> bool:
        return bool(
        	( local_destiantion in self.__destination or EventAddress.All in self.__destination )
            and not len(self.__destination) < 1
        )
        
    def get_origin(self) -> EventAddress:
        return self.__origin
    
    def get_descriptor(self) -> EventMessageDescriptor:
        return self.__data_descriptor


class EventProcessorContainer():
    def __init__(self, trigger: EventMessageDescriptor, function: Callable) -> None:
        self.trigger: EventMessageDescriptor = trigger
        self.function: Callable = function
        
    def run(self, event: EventMessage):
        
        data = event.get_messege()
        
        self.function(data)
        


    
# this class is the new base class for allpublishers and subscribers
class Addressable(ABC):
    def __init__(self, address:EventAddress) -> None:
        self.address: EventAddress = address
        
        self.processors: List[EventProcessorContainer] = []
        
    def add_processor(self, trigger: EventMessageDescriptor, function: Callable) -> None:
        self.processors.append(EventProcessorContainer(trigger, function))
        
    
    def process_event(self, event:EventMessage):
        """
            Selects a function that handles the event by it associated descriptor.
        """
        messege_action_trigger_descriptor: EventMessageDescriptor = event.get_descriptor()
        
        # TODO: add some sideeffect checs here
        
        try:
            for processor in self.processors:
                if processor.trigger == messege_action_trigger_descriptor:
                    processor.run(event)
        except Exception as e:
            print(f"Error processing event {event.title} -> {e}")

   
        
class EventHandlerQueue():
    def __init__(self) -> None:
        self.event_queue: Queue = Queue()
        
        self.sub_lock: Lock = Lock()
        self.subscribers: List[Addressable] = []         
        
        Thread(
            target=self.messege_runner,
            args=(),
            daemon=True
        ).start()
    
    def enroll(self, subscriber: Addressable):
        with self.sub_lock:
            self.subscribers.append(subscriber)
                
    def broadcast(self, message: EventMessage):
        self.event_queue.put(message)
        
    def join(self):
        self.event_queue.join()
        
    def messege_runner(self):
        while True:
            time.sleep(0.005) 
            
            try:
                event: EventMessage = self.event_queue.get()
                
            except Empty:
                continue
            else:
                subscribers_snap = []
                with self.sub_lock:
                    subscribers_snap = self.subscribers.copy()
                
                for subscriber in subscribers_snap:
                    if event.is_in_destination(subscriber.address):
                        subscriber.process_event(event)
                        
                        
                #done                
                self.event_queue.task_done()
  
  
