from enum import Enum

class EventAddress(Enum):
    """
        Represents different addresses or destinations within the application for events. 
        
        The values are categorized as follows:
            - Negative values: Represent edge cases, such as specific destinations used primarily for logging, errors, or special cases.
            - Zero: Represents an undefined address, used when the destination is not specified or is irrelevant.
            - Positive values: Represent valid destinations for actors within the application, such as different consumers or producers.
    """
    
    Logger = -4
    Error = -3
    Void = -2
    All = -1
    
    Undefined = 0
    
    #UI 1-32
    ViewMain = 1
    
    
    #TLE 161 -164
    T
    
    
class EventMessageDescriptor(Enum):
    """
        Describes the action that should be triggered in a consumer based on the event message. 
        
        The values are categorized as follows:
            - Zero: No specific action is defined.
            - Positive values: Represent various arbitrary actions that can be assigned to "Action Processors" within the application.
    """
    
    Undefined = 0
    
    PrintString = 1
    MultiplyNumberByTwo = 2
    PrettyprintObject = 3
    CalculateTheSquare = 4
    CalculateTheRoot = 5
    
    class SateliteWatcherProcessors(Enum):
        FindSatsByPosition = 0
        