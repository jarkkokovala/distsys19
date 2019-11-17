import datetime
import logging.handlers
import os

path = "'../../../../dfslog/"
try:
    if not os.path.exists(path):
        os.makedirs(path)
except OSError as e:
    print(e)
    pass

instrumentation = logging.getLogger('instrumentation')
if not instrumentation.handlers:  # if logger 'name' already exists
    handler = logging.FileHandler(path + datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S") + '.log')
    handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)06d;%(message)s', '%Y-%m-%d_%H:%M:%S'))
    handler.setLevel(logging.DEBUG)
    instrumentation.addHandler(handler)
    # print(handler)

#instrumentation.warning('This should go in the file.')
