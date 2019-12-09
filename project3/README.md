
### Group

Eeva-Maria Laiho, Jarkko Kovala, Paavo Hemmo

# Project 3

## State chart

State chart for the digital watch is divided in three parts. 
* The first part describes the back light on/off operation. The back light can be toggled on/off from any watch state. Toggling the back light on/off is independent of other watch functionality.
* The second part describes the alarm on/off operation. Similar to back light alarm can fire from any watch state and it's independent of other watch functionality.
* The third part describes the main watch operations: time, chrono and alarm display modes and time and alarm edit modes.

The topLeftPressed event is not displayed in the chart since it has no functionality attached to it. Pushing the top left button  alternates between chrono and time display mode. This functionality attached to the topLeftReleased event.

![Digital watch](./digital_watch.png)

The original state chart for the digital watch is displayed above. The state chart may not be one-to-one with the implementation. Due to time-constraints for the project and other student work updating implementation-time modifications on the chart was not feasible. 

## Implementation

The watch implementation has three parts: the state machine (DigitalWatch.des), watch functionality (WatchHardware.py) and the GUI (LowLevelGUI and DWatchGUI as supplied with the task).

The state machine only has callouts to the other components to separate the functionality from the model.

Delayed events, such as timed shutting of the backlight, entering & exiting of chrono and edit states, etc are implemented as threads that are started when the time counter begins and launch an event after a delay. For example, to enter time edit, a thread is started when bottom right button is pressed. The thread sleeps for 1.5 seconds, and if the button is still pressed, an event is launched to switch the state to time edit. The same thread continues to periodically check if five seconds is passed since the last edit, to automatically switch back to time display mode.

Time ticks are implemented by a thread that runs continuously to launch events every second that increment the time. There is an internal boolean that disables updating of time for this thread to stop updates while in time edit.

The application can be launched with Python SVM with the command (run the command in the same working directory with the application source files) 

> python /path/to/svm.py DigitalWatch.des
