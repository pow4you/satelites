import os

# Define the project structure as a dictionary
project_structure = {
    'your_project': {
        'app.py': 'APP_PY_CONTENT',
        'messaging': {
            '__init__.py': '',
            'message.py': 'MESSAGE_PY_CONTENT',
            'messaging_proxy.py': 'MESSAGING_PROXY_PY_CONTENT',
        },
        'services': {
            '__init__.py': '',
            'base_service.py': 'BASE_SERVICE_PY_CONTENT',
            'concrete_service_a': {
                '__init__.py': '',
                'service_a.py': 'SERVICE_A_PY_CONTENT',
            },
            'concrete_service_b': {
                '__init__.py': '',
                'service_b.py': 'SERVICE_B_PY_CONTENT',
            },
        },
        'interfaces': {
            '__init__.py': '',
            'iservice.py': 'ISERVICE_PY_CONTENT',
        },
        'processors': {
            '__init__.py': '',
            'sample_processor.py': 'SAMPLE_PROCESSOR_PY_CONTENT',
        },
        'logs': {
            '__init__.py': '',
            'logger.py': 'LOGGER_PY_CONTENT',
        },
        'config': {
            '__init__.py': '',
            'settings.py': 'SETTINGS_PY_CONTENT',
        },
        'README.md': 'README_CONTENT',
        'requirements.txt': 'REQUIREMENTS_CONTENT',
    }
}

# Code content for each file
file_contents = {
    'APP_PY_CONTENT': '''# app.py

import asyncio
from messaging.messaging_proxy import messaging_proxy
from services.concrete_service_a.service_a import ServiceA
from services.concrete_service_b.service_b import ServiceB
from messaging.message import Message
from logs.logger import setup_logging

async def main() -> None:
    # Set up logging
    setup_logging()

    pub_endpoint: str = "tcp://127.0.0.1:5557"
    sub_endpoint: str = "tcp://127.0.0.1:5558"

    # Start the messaging proxy
    proxy_task = asyncio.create_task(messaging_proxy(pub_endpoint, sub_endpoint))

    # Create instances of concrete services
    service_a = ServiceA(pub_endpoint, sub_endpoint)
    service_b = ServiceB(pub_endpoint, sub_endpoint)

    # Start receiving messages
    asyncio.create_task(service_a.receive_messages())
    asyncio.create_task(service_b.receive_messages())

    # Give time for subscriptions to set up
    await asyncio.sleep(1)

    # Service A publishes a message on 'topic2'
    message_from_a = Message(topic='topic2', data=b'Hello from Service A')
    await service_a.publish(message_from_a)

    # Service B publishes a message on 'topic1'
    message_from_b = Message(topic='topic1', data=b'Hello from Service B')
    await service_b.publish(message_from_b)

    # Keep the application running for a while
    await asyncio.sleep(5)

    # Cancel the proxy task and exit
    proxy_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
''',

    'MESSAGE_PY_CONTENT': '''# messaging/message.py

from typing import List

class Message:
    """
    Represents a message transmitted over the network.

    Attributes:
        topic (str): The topic of the message.
        data (bytes): The serialized data payload.
    """

    def __init__(self, topic: str, data: bytes) -> None:
        self.topic: str = topic
        self.data: bytes = data

    def serialize(self) -> List[bytes]:
        """
        Prepares the message for sending over ZeroMQ.

        Returns:
            List[bytes]: The message parts to send.
        """
        return [self.topic.encode('utf-8'), self.data]

    @staticmethod
    def deserialize(parts: List[bytes]) -> 'Message':
        """
        Deserializes parts into a Message object.

        Args:
            parts (List[bytes]): The message parts received.

        Returns:
            Message: The deserialized Message object.
        """
        topic: str = parts[0].decode('utf-8')
        data: bytes = parts[1]
        return Message(topic, data)
''',

    'MESSAGING_PROXY_PY_CONTENT': '''# messaging/messaging_proxy.py

import zmq.asyncio
import asyncio

async def messaging_proxy(pub_endpoint: str, sub_endpoint: str) -> None:
    """
    Sets up a PUB/SUB proxy for services to connect to.

    Args:
        pub_endpoint (str): Endpoint for PUB sockets to bind to.
        sub_endpoint (str): Endpoint for SUB sockets to bind to.
    """
    context: zmq.asyncio.Context = zmq.asyncio.Context()
    frontend: zmq.asyncio.Socket = context.socket(zmq.XSUB)
    frontend.bind(sub_endpoint)
    backend: zmq.asyncio.Socket = context.socket(zmq.XPUB)
    backend.bind(pub_endpoint)

    try:
        await zmq.asyncio.proxy(frontend, backend)
    except Exception as e:
        print(f"Messaging proxy encountered an error: {e}")
    finally:
        frontend.close()
        backend.close()
        context.term()
''',

    'BASE_SERVICE_PY_CONTENT': '''# services/base_service.py

import zmq.asyncio
import asyncio
import uuid
import logging
from typing import Callable, Awaitable, Dict, Optional
from interfaces.iservice import IService
from messaging.message import Message

class Service(IService):
    """
    Abstract base class for services.

    Implements common functionality for services, such as publishing and subscribing to messages.
    Concrete services should inherit from this class and implement their specific logic.
    """

    def __init__(self, pub_endpoint: str, sub_endpoint: str) -> None:
        self.service_id: str = self.generate_service_id()
        self.context: zmq.asyncio.Context = zmq.asyncio.Context()
        self.pub_socket: zmq.asyncio.Socket = self.context.socket(zmq.PUB)
        self.pub_socket.connect(pub_endpoint)
        self.sub_socket: zmq.asyncio.Socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(sub_endpoint)
        self.subscriptions: Dict[str, Callable[[Message], Awaitable[None]]] = {}
        self.logger: logging.Logger = self.setup_logger()

    def generate_service_id(self) -> str:
        """Generates a unique service identifier."""
        return str(uuid.uuid4())

    def setup_logger(self) -> logging.Logger:
        """
        Sets up the logger for the service.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger(f"Service-{self.service_id}")
        logger.setLevel(logging.INFO)
        # Optional: Configure logging handlers if needed
        return logger

    def subscribe(self, topic: str, processor: Callable[[Message], Awaitable[None]]) -> None:
        """
        Subscribes to a topic with a processor function.

        Args:
            topic (str): The topic to subscribe to.
            processor (Callable[[Message], Awaitable[None]]): Async function to process messages.
        """
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.subscriptions[topic] = processor
        self.logger.info(f"Subscribed to topic: {topic}")

    async def publish(self, message: Message) -> None:
        """
        Publishes a message to the PUB socket.

        Args:
            message (Message): The message to publish.
        """
        try:
            await self.pub_socket.send_multipart(message.serialize())
            self.logger.info(f"Published message on topic: {message.topic}")
        except Exception as e:
            self.logger.error(f"Failed to publish message: {e}")

    async def receive_messages(self) -> None:
        """
        Continuously receives messages from the SUB socket.

        This method should be run in an asyncio task.
        """
        while True:
            try:
                parts: list[bytes] = await self.sub_socket.recv_multipart()
                message: Message = Message.deserialize(parts)
                await self.process_message(message)
            except Exception as e:
                self.logger.error(f"Error receiving message: {e}")

    async def process_message(self, message: Message) -> None:
        """
        Processes a received message using the appropriate processor.

        Args:
            message (Message): The received message.
        """
        processor: Optional[Callable[[Message], Awaitable[None]]] = self.subscriptions.get(message.topic)
        if processor:
            try:
                await processor(message)
            except Exception as e:
                self.logger.error(f"Error processing message on topic '{message.topic}': {e}")
        else:
            self.logger.warning(f"No processor found for topic: {message.topic}")
''',

    'SERVICE_A_PY_CONTENT': '''# services/concrete_service_a/service_a.py

from services.base_service import Service
from messaging.message import Message

class ServiceA(Service):
    """
    Concrete implementation of Service A.

    This service subscribes to specific topics and processes messages accordingly.
    """

    def __init__(self, pub_endpoint: str, sub_endpoint: str) -> None:
        super().__init__(pub_endpoint, sub_endpoint)
        self.setup_subscriptions()

    def setup_subscriptions(self) -> None:
        """
        Sets up the subscriptions for Service A.
        """
        self.subscribe('topic1', self.process_topic1)

    async def process_topic1(self, message: Message) -> None:
        """
        Processes messages received on 'topic1'.

        Args:
            message (Message): The received message.
        """
        data: str = message.data.decode('utf-8')
        self.logger.info(f"ServiceA processed message on topic1: {data}")
        # Implement specific logic for Service A
''',

    'SERVICE_B_PY_CONTENT': '''# services/concrete_service_b/service_b.py

from services.base_service import Service
from messaging.message import Message

class ServiceB(Service):
    """
    Concrete implementation of Service B.

    This service subscribes to specific topics and processes messages accordingly.
    """

    def __init__(self, pub_endpoint: str, sub_endpoint: str) -> None:
        super().__init__(pub_endpoint, sub_endpoint)
        self.setup_subscriptions()

    def setup_subscriptions(self) -> None:
        """
        Sets up the subscriptions for Service B.
        """
        self.subscribe('topic2', self.process_topic2)

    async def process_topic2(self, message: Message) -> None:
        """
        Processes messages received on 'topic2'.

        Args:
            message (Message): The received message.
        """
        data: str = message.data.decode('utf-8')
        self.logger.info(f"ServiceB processed message on topic2: {data}")
        # Implement specific logic for Service B
''',

    'ISERVICE_PY_CONTENT': '''# interfaces/iservice.py

from abc import ABC, abstractmethod
from typing import Callable, Awaitable
from messaging.message import Message

class IService(ABC):
    """
    Interface for services in the application.

    Services act as both publishers and subscribers in the messaging system.
    """

    @abstractmethod
    def subscribe(self, topic: str, processor: Callable[[Message], Awaitable[None]]) -> None:
        """
        Subscribes to a topic with a processor function.

        Args:
            topic (str): The topic to subscribe to.
            processor (Callable[[Message], Awaitable[None]]): Async function to process messages.
        """
        pass

    @abstractmethod
    async def publish(self, message: Message) -> None:
        """
        Publishes a message to the messaging system.

        Args:
            message (Message): The message to publish.
        """
        pass

    @abstractmethod
    async def receive_messages(self) -> None:
        """
        Starts the message receiving loop.

        This method should be run in an asyncio task.
        """
        pass
''',

    'SAMPLE_PROCESSOR_PY_CONTENT': '''# processors/sample_processor.py

from messaging.message import Message

async def sample_processor(message: Message) -> None:
    """
    Sample processor function for processing messages.

    Args:
        message (Message): The received message.
    """
    data: str = message.data.decode('utf-8')
    print(f"[{message.topic}] {data}")
''',

    'LOGGER_PY_CONTENT': '''# logs/logger.py

import logging

def setup_logging() -> None:
    """
    Configures the logging settings for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler()
            # Add FileHandler or other handlers if needed
        ]
    )
''',

    'SETTINGS_PY_CONTENT': '''# config/settings.py

PUB_ENDPOINT: str = "tcp://127.0.0.1:5557"
SUB_ENDPOINT: str = "tcp://127.0.0.1:5558"
'''}

    
import sys

def create_project(structure, root=''): 
    for name, content in structure.items(): 
        path = os.path.join(root, name) 
        if isinstance(content, dict): 
            # Create directory 
            os.makedirs(path, exist_ok=True) 
            # Recursively create subdirectories and files 
            create_project(content, path) 
        else: # Create file and write content 
            with open(path, 'w', encoding='utf-8') as f: # Replace placeholder with actual content 
                file_content = file_contents.get(content, content) 
                f.write(file_content)

def main(): 
    create_project(project_structure) 
    print("Project structure created successfully.")

if __name__ == "__main_": 
    
    main()