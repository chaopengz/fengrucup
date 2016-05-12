# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO

import time


# BOARD编号方式，基于插座引脚编号



# 输出模式

def opendoor():
    PORT = 12
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PORT, GPIO.OUT)
    GPIO.output(PORT, False)
    print 'false'
    time.sleep(1)
    GPIO.output(PORT, True)
    print 'true'
    GPIO.cleanup()


# opendoor()
