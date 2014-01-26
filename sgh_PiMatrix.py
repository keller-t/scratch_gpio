#!/usr/bin/env python
# sgh_Stepper - control 5 pin stepper motors from ScratchGPIO.
#Copyright (C) 2013 by Simon Walters

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Version =  '0.1.0' # 25Jan14

import time
import threading
import datetime as dt

import subprocess
import math
try:
    import smbus
except:
    pass
    
STATE_PORTA = 0x00
STATE_PORTB = 0x01
SET_PORTA = 0x12
SET_PORTB = 0x13

class sgh_PiMatrix(threading.Thread):

    def __init__(self,address, i2c_bus=1):
        print "PiMatrix init"
        self.i2c_bus = i2c_bus
        print "i2cbus:",self.i2c_bus
        #self.bus = smbus.SMBus(i2c_bus)
        self.bus = smbus.SMBus(i2c_bus)
        self.i2c_addr = address
        print "PiMatrix self.bus:", self.bus
        self.enable_output()
        self.aval = 0x00
        self.bval = 0xFF
        print "PiMatrix intialised"
        self.terminated = False
        self.toTerminate = False
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.mPoint =[[0 for x in xrange(8)] for x in xrange(8)] 
        print self.mPoint
        
    def enable_output(self):
        self.write_i2c(STATE_PORTA, 0x00)
        self.write_i2c(STATE_PORTB, 0x00)

    def update_porta(self, value):
        self.write_i2c(SET_PORTA , value)

    def update_portb(self, value):
        self.write_i2c(SET_PORTB , value)


    def write_i2c(self, reg_addr, value):
        if not isinstance(value, list):
            value = [value];
        try:
            self.bus.write_i2c_block_data(self.i2c_addr, reg_addr, value)
        except IOError:
            subprocess.call(['i2cdetect', '-y', '0'])
            self.bus.write_i2c_block_data(self.i2c_addr, reg_addr, value)

    def start(self):
        self.thread = threading.Thread(None, self.run, None, (), {})
        self.thread.start()

    def stop(self):
        #print "Stop Matrix command given"
        self.toTerminate = True
        while self.terminated == False:
        # Just wait
            time.sleep(0.01)
        print "Matrix stopped"


    def run(self):
        #time.sleep(2) # just wait till board likely to be up and running
        while self.toTerminate == False:
            for y in range(0,8):
                #print "X and Y",x,y
                #if self.mPoint [x][y] == 1:
                #print "X and Y",x,y
                self.aval = 0
                for x in range(0,8):
                    self.aval = self.aval + ((0x80 >> x) * self.mPoint [x][y])
                self.bval = 0xFF - (0x80 >> y)        
                #self.aval = 0x0F
                #print y
                #print self.aval,self.bval
                #print bin(self.aval)#,bin(self.bval)
                #self.aval = 0x0F
                self.update_porta(0)
                self.update_portb(self.bval)
                self.update_porta(self.aval)
                
                time.sleep(0.001)
            #self.update_porta(0)
            #self.update_porta(0)
            #time.sleep(1)
               
                # for x in range(1,4):
                    # #print "X and Y",x,y
                    # if self.mPoint [x][y] == 1:
                        # #print "X and Y",x,y
                        # xbin = (0x80 >> x)
                        # ybin = (0x80 >> y)
                        # #print " xbin,ybin" , xbin,ybin
                        # self.aval =  (0x80 >> x)
                        # self.bval = 0xFF - (0x80 >> y)        
                        # #self.aval = 0x0F
                        # #print self.aval,self.bval
                        # #print bin(self.aval),bin(self.bval)
                        # #self.aval = 0x0F
                        # self.update_porta(self.aval)
                        # self.update_portb(self.bval)
                 

        self.terminated = True
    ####### end of Stepper Class

    def setPixel(self,x,y,onoff=1):
        self.mPoint[x][y] = onoff
        
    def clearPixel(self, x, y):
        "A wrapper function to clear pixels (purely cosmetic)"
        self.setPixel(x, y, 0)        

    def getPixel(self,x,y):
        return self.mPoint[x][y]        
        
    def clear(self):
        print "clear"
        self.update_porta(0)
        self.update_portb(0)
        for y in range(0,8):
            for x in range(0,8):
                self.mPoint[x][y] = 0
                
    def scroll(self, direction = "left"):
        #print direction
        if direction == "left":
            for y in range(0,8):
                for x in range (0,7):
                    #print (x+1+(y*8))
                    self.setPixel(x,y,self.getPixel(x+1,y))

            for y in range(0,8):
                self.setPixel(7,y,0)
            
        if direction == "right":
            print "right"
            for y in range(0,8):
                for x in range (7,0,-1):
                    #print (x+1+(y*8))
                    self.setPixel(x,y,self.getPixel(x-1,y))   
            for y in range(0,8):
                self.setPixel(0,y,0)                      





