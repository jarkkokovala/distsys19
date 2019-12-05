import time
import ThreadUtil

class WatchHardware:
    def __init__(self, eventhandler):
        self.eventhandler = eventhandler
        self.timeTicks = 0
        self.timeUpdating = True
        self.displayMode = "Time"
        self.topRightPressed = False

    def topRightDown(self):
        self.topRightPressed = True

    def ThreadShutLight(self):
        time.sleep(2)
        if not self.topRightPressed:
            self.eventhandler.event("shutLight")

    def topRightUp(self):
        self.topRightPressed = False
        ThreadUtil.StartThread(self.ThreadShutLight, ())

    def changeMode(self):
        if self.displayMode == "Time":
            self.displayMode = "Chrono"
        else:
            self.displayMode = "Time"

    def ThreadTimeTick(self):
        while True:
            time.sleep(1)
            if self.timeUpdating:
                self.timeTicks += 1
                self.eventhandler.event("increaseTimeByOne")

    def start(self):
        ThreadUtil.StartThread(self.ThreadTimeTick, ())
