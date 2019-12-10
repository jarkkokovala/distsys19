
### Group

Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo

# Project 3

## State chart

State chart for the digital watch is divided in three parts. 
* The first part describes the back light on/off operation. The back light can be toggled on/off from any watch state. Toggling the back light on/off is independent of other watch functionality.
* The second part describes the alarm on/off operation. Similar to back light alarm can fire from any watch state and it's independent of other watch functionality.
* The third part describes the main watch operations: time, chrono and alarm display modes and time and alarm edit modes.

The topLeftPressed event is not displayed in the chart since the task description does not describe any event that would require it. Pushing the top left button alternates between chrono and time display mode. This functionality is attached to the topLeftReleased event.

![Digital watch](./digital_watch.png)

The original state chart for the digital watch is displayed above. The chart reflects the task description for project 3 and is not one-to-one with the implementation. The chart does not reflect all implementation-time modifications on watch functionality.  This is due to time-constraints on the project and other student work. 

The following watch functionality is not reflected on the chart: 
* Alarm activated sign: 
    * Alarm activated sign is displayed on watch screen when an alarm is set and has been activated. Alarm can be activated by pushing briefly the bottom right button. Alarm will not fire if it hasn't been activated.
* Move edit position on edit mode: 
    * When in time or alarm edit mode the edit position (hour, minute, second) can be changed by pressing the top left button. 


## Implementation

The watch implementation has three parts: the state machine (DigitalWatch.des), watch functionality (WatchHardware.py) and the GUI (LowLevelGUI and DWatchGUI as supplied with the task).

The state machine only has callouts to the other components to separate the functionality from the model.

Delayed events, such as timed shutting of the backlight, entering & exiting of chrono and edit states, etc are implemented as threads that are started when the time counter begins and launch an event after a delay. For example, to enter time edit, a thread is started when bottom right button is pressed. The thread sleeps for 1.5 seconds, and if the button is still pressed, an event is launched to switch the state to time edit. The same thread continues to periodically check if five seconds is passed since the last edit, to automatically switch back to time display mode.

Time ticks are implemented by a thread that runs continuously to launch events every second that increment the time. There is an internal boolean that disables updating of time for this thread to stop updates while in time edit.

The application can be launched with Python SVM with the command (run the command in the same working directory with the application source files) 

> python /path/to/svm.py DigitalWatch.des
