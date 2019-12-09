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

    # Press top right button
    def topRightDown(self):
        self.topRightPressed = True

    # Thread for timed backlight shutdown
    def ThreadShutLight(self):
        time.sleep(2)
        if not self.topRightPressed:
            self.eventhandler.event("shutLight")

    # Release top right button, initiates timed backlight shutdown
    def topRightUp(self):
        self.topRightPressed = False
        ThreadUtil.StartThread(self.ThreadShutLight, ())

    # Switch between time and chrono modes by pressing top left button in either one
    def changeMode(self):
        if self.displayMode == "Time":
            self.displayMode = "Chrono"
        else:
            self.displayMode = "Time"
    
    def checkTime(self, alarm, gui):
        if alarm != None:
            if gui.checkTime():
                print "ALARM"
            else:
                print "No alarm"
        else:
            print "Alarm not set"

    def selectNext(self):
        self.lastEdit = time.time()

    # Thread for running chrono
    def ThreadChronoTick(self):
        while self.chronoRunning:
            time.sleep(0.01)
            if self.chronoRunning:
                self.eventhandler.event("increaseChronoByOne")

    # Switch chrono running by bottom right button in chrono mode
    def initChrono(self):
        if not self.chronoRunning:
            self.chronoRunning = True
            ThreadUtil.StartThread(self.ThreadChronoTick, ())
        else:
            self.chronoRunning = False

    # Thread for timed entering of time edit mode
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
    
    def ThreadAlarmEdit(self):
        time.sleep(1.5)
        if self.bottomLeftPressed:
            self.displayMode = "Alarm Edit"
            self.lastEdit = time.time()
            self.eventhandler.event("startAlarmEdit")
            
            while self.displayMode == "Alarm Edit" and time.time() < self.lastEdit + 5:
                time.sleep(1)
            
            self.stopAlarmEdit()

    # Press bottom right button in time mode to start enterint time edit mode
    def initTimeEdit(self):
        self.bottomRightPressed = True
        ThreadUtil.StartThread(self.ThreadTimeEdit, ())
    
    def initAlarmEdit(self):
        self.bottomLeftPressed = True
        print("Alarm edit")
        ThreadUtil.StartThread(self.ThreadAlarmEdit, ())

    # Really exit time edit mode (called from timed exiting or timeout in time edit thread)
    def stopTimeEdit(self):
        self.displayMode == "Time"
        self.timeUpdating = True
        self.eventhandler.event("stopTimeEdit")
    
    def stopAlarmEdit(self):
        self.displayMode == "Time"
        self.timeUpdating = True
        self.eventhandler.event("stopAlarmEdit")

    # Timed exiting time edit
    def ThreadFinishTimeEdit(self):
        time.sleep(2)

        if self.bottomRightPressed:
            self.stopTimeEdit()

    # Press bottom right button in time edit mode to start exiting time edit
    def finishTimeEdit(self):
        self.bottomRightPressed = True
        ThreadUtil.StartThread(self.ThreadFinishTimeEdit, ())
    
    # Release bottom right button
    def bottomRightUp(self):
        self.bottomRightPressed = False    

    # Time increase thread for editing mode
    def ThreadTimeIncrease(self):
        while self.bottomLeftPressed:
            if self.displayMode == "Time Edit":
                self.eventhandler.event("increaseTimeByOne")
            else:
                # Alarm Edit
                self.eventhandler.event("increaseAlarmByOne")
            self.lastEdit = time.time()
            time.sleep(0.3)

    # Bottom left pressed in time edit mode, increase time and start thread
    def initTimeIncrease(self):
        self.bottomLeftPressed = True
        self.lastEdit = time.time()

        ThreadUtil.StartThread(self.ThreadTimeIncrease, ())

    # Release left button in time edit mode
    def stopTimeIncrease(self):
        self.bottomLeftPressed = False

    # Timed exiting alarm edit
    def ThreadFinishAlarmEdit(self):
        time.sleep(2)

        if self.bottomRightPressed:
            self.stopAlarmEdit()

    # Press bottom right button in time edit mode to start exiting alarm edit
    def finishAlarmEdit(self):
        self.bottomRightPressed = True
        ThreadUtil.StartThread(self.ThreadFinishAlarmEdit, ())

    # Timer tick thread for time/chrono modes
    def ThreadTimeTick(self):
        while True:
            time.sleep(1)
            if self.timeUpdating:
                self.eventhandler.event("increaseTimeByOne")

    # Start the watch
    def start(self):
        ThreadUtil.StartThread(self.ThreadTimeTick, ())
