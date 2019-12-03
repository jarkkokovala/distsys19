import time
import ThreadUtil

class WatchHardware:
    def __init__(self, eventhandler, gui):
        self.eventhandler = eventhandler
        self.gui = gui
        self.timeTicks = 0
    
    def ThreadTimeTick(self):
        while True:
            time.sleep(1)
            self.timeTicks += 1

    def start(self):
        ThreadUtil.StartThread(self.ThreadTimeTick, ())
