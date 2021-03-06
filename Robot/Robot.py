#!/usr/bin/python3
""" Everything needed to control the robot.  """
from threading import Thread
import yaml
import spidev
import os
from BrickPiM import BrickPi

global BLACK
global WHITE

BLACK = 1
WHITE = 0

class Robot(object):
    """ All methods needed to control the robot """
    def __init__(self):
        # Load configuration file
        with open("config.yml", 'r') as ymlfile: # Load Configuration into Dict
                cfg = yaml.load(ymlfile)
        for section in cfg['robot']:
            setattr(self, section, cfg['robot'][section])

        # Init vars for values
        self.colors = [0]*8 # Contains color Values
        self.colorsCalibrate = [150]*8 # Contains treshold, modified by Robot.Calibrate

        # Setup
        #-------------------------------
        # Open SPI bus
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)

        # BrickPi
        self.brick = BrickPi()


    def sensorbar(self, channel=0):
        """ Update self.colors and return value of one specified sensor (not neccessary)."""
        data = self._readChannel()
        #If data is bigger than the threshold (==Black) put True (aka. 1) in the list
        self.colors = [ int(v > t) for (v,t) in zip(data, self.colorsCalibrate) ]
        return self.colors[channel]


    def motor(self, direct, speed):
        if direct == 'l':
            m = self.motorl
        elif direct == 'r':
            m = self.motorr
        else:
            m = self.motorr
            self.motor('l', speed)

        if speed < 0:
            self.brick.updateDirection(m, 0)
        else:
            self.brick.updateDirection(m, 1)

        self.brick.updateSpeed(m, abs(int(speed)))

    def _readChannel(self):
        """ Function to read SPI data from MCP3008 chip """
        data = [0]*8
        for i in range(8):
            adc = self.spi.xfer2([1, (8+i)<<4, 0])
            data[i] = ((adc[1]&3) << 8) + adc[2]
        return data 
