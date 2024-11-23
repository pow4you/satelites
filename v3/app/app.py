import threading
import sys
from broker import Broker
from controller import Controller
from PyQt5.QtWidgets import QApplication

def start_broker():
    broker = Broker()
    broker.run()

if __name__ == '__main__':
    # Start the broker in a separate thread
    broker_thread = threading.Thread(target=start_broker, daemon=True)
    broker_thread.start()

    # Start the PyQt5 application
    app = QApplication(sys.argv)
    controller = Controller()
    controller.show()
    sys.exit(app.exec_())
