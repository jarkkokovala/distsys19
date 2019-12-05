import time
import ThreadUtil

class WatchHardware:
    def __init__(self, eventhandler):
        self.eventhandler = eventhandler
        self.timeUpdating = True
        self.chronoRunning = False
        self.displayMode = "Time"
        self.topRightPressed = False
        self.bottomRightPressed = False
        self.bottomLeftPressed = False
        self.lastEdit = 0

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

    def ThreadChronoTick(self):
        while self.chronoRunning:
            time.sleep(0.01)
            if self.chronoRunning:
                self.eventhandler.event("increaseChronoByOne")

    def initChrono(self):
        if not self.chronoRunning:
            self.chronoRunning = True
            ThreadUtil.StartThread(self.ThreadChronoTick, ())
        else:
            self.chronoRunning = False

    def ThreadTimeEdit(self):
        time.sleep(1.5)

        if self.bottomRightPressed:
            self.displayMode = "Time Edit"
            self.timeUpdating = False
            self.lastEdit = time.time()
            self.eventhandler.event("startTimeEdit")

            while self.displayMode == "Time Edit" and time.time() < self.lastEdit + 5:
                time.sleep(1)
            
            self.stopTimeEdit()

    def initTimeEdit(self):
        self.bottomRightPressed = True
        ThreadUtil.StartThread(self.ThreadTimeEdit, ())

    def stopTimeEdit(self):
        self.displayMode == "Time"
        self.timeUpdating = True
        self.eventhandler.event("stopTimeEdit")

    def ThreadFinishTimeEdit(self):
        time.sleep(2)

        if self.bottomRightPressed:
            self.stopTimeEdit()

    def finishTimeEdit(self):
        self.bottomRightPressed = True
        ThreadUtil.StartThread(self.ThreadFinishTimeEdit, ())
    
    def bottomRightUp(self):
        self.bottomRightPressed = False    

    # Time increase thread for editing mode
    def ThreadTimeIncrease(self):
        while self.bottomLeftPressed:
            self.eventhandler.event("increaseTimeByOne")
            self.lastEdit = time.time()
            time.sleep(0.3)

    # Bottom left pressed in time edit mode, increase time and start thread
    def initTimeIncrease(self):
        self.bottomLeftPressed = True
        self.lastEdit = time.time()

        ThreadUtil.StartThread(self.ThreadTimeIncrease, ())

    def stopTimeIncrease(self):
        self.bottomLeftPressed = False

    # Timer tick thread for time/chrono modes
    def ThreadTimeTick(self):
        while True:
            time.sleep(1)
            if self.timeUpdating:
                self.eventhandler.event("increaseTimeByOne")

    def start(self):
        ThreadUtil.StartThread(self.ThreadTimeTick, ())
