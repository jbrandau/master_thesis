#!/usr/bin/python

import copy
import gc
import time
import serial
import random
import struct
import numpy as np
import scipy.io as spio
import datetime
import os
import gmpy2
import copy

en_oscilloscope = False
if en_oscilloscope == True :
    import Oscilloscope as lecroy

def write(ser, data):
   ser.write(chr(data))

def write64(ser, addr, data):
   ser.write(chr(addr  ) + chr(byte(data, 0)) +
             chr(addr+1) + chr(byte(data, 1)) +
             chr(addr+2) + chr(byte(data, 2)) +
             chr(addr+3) + chr(byte(data, 3)) +
             chr(addr+4) + chr(byte(data, 4)) +
             chr(addr+5) + chr(byte(data, 5)) +
             chr(addr+6) + chr(byte(data, 6)) +
             chr(addr+7) + chr(byte(data, 7)))

def read(ser, addr):
   ser.write(chr( addr | 0x80))
   return ord(ser.read())

def byte(val, index):
    return ((int(val)>>(8*index)) & 0xff)

if __name__ == "__main__":

    # num_traces = 4000
    num_traces = 1
    traces_per_file = 1000
    samples_per_trace = 2500
    num_traces_to_average = 1000
    traces_saved_per_file = 100

    if en_oscilloscope == True:
        le = lecroy.Oscilloscope()
        le.connect()
        le.calibrate()
        le.displayOn()
        le.Samples = samples_per_trace
        le.clearsweeps_all()

    if en_oscilloscope == False:
        import Oscilloscope as lecroy
        le = lecroy.Oscilloscope()
        le.displayOn()
        le.connect()
        le.clearsweeps_all()