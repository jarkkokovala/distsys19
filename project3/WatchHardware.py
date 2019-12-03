import time
import ThreadUtil

class WatchHardware:
    def __init__(self, eventhandler):
        self.eventhandler = eventhandler
        self.timeTicks = 0
    
    def ThreadTimeTick(self):
        while True:
            time.sleep(1)
            self.timeTicks += 1
            self.eventhandler.event("increaseTimeByOne")

    def start(self):
        ThreadUtil.StartThread(self.ThreadTimeTick, ())
