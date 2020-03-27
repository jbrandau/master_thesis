#!/usr/bin/python

import time
import serial
import random
import struct
import pickle
from picoscope import ps5000
import numpy as np
import datetime
import os


def initscope():
    ps = ps5000.PS5000(connect=False)
    ps.open()


    # do stuff
    ps.flashLed(10)
    time.sleep(5.0)  # the above flash takes roughly 4 seconds

    ps.setChannel("A", coupling="DC", VRange=25.0, probeAttenuation=10)
    ps.setChannel("B", coupling="DC", VRange=25.0, probeAttenuation=10)
    
    ps.setSamplingFrequency(500E6, 3770)
        
    return ps

if __name__ == "__main__":

    #ps = initscope()

    ser = serial.Serial(
        port='/dev/cu.usbmodem1421',
        baudrate=9600,
        timeout=None
    )
        
    time.sleep(0.5):

    traces = 500000
        
    random.seed()    

    # generate random nonce
    key = [589472988, 
           1980599320, 
           506370484,
           3770618530, 
           2494332794, 
           1040266887,
           1817683584, 
           3399450456]
           
    bytesWritten = 0

    for i in xrange(0,8):
        bytesWritten += ser.write(struct.pack("<I", key[i]))

    print bytesWritten        

    key_replay = [0]*8
    key_replay_bytes = ser.read(32)
    for i in xrange(0,8):
        key_replay[i] = struct.unpack("<I", key_replay_bytes[i*4:i*4+4])
        print "original key: " + hex(key[i])
        print "replayed key: " + hex(int(str(key_replay[i][0])))
      
      
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H_%M_%S')  
        
    if not os.path.exists("traces" + st):
        os.makedirs("traces" + st)
    os.chdir("traces" + st)


    ps.setSimpleTrigger(trigSrc="A", threshold_V=3.1, timeout_ms=100000, direction="Rising")
    time.sleep(0.5)

    ts1 = time.time()

    for i in xrange(0,traces) :
        if(i%100 == 0):
            print "Elapsed time: " + str(time.time() - ts1) + " seconds"
            print "Collected traces: " + str(i)
        
        # arm trigger of picoscope?
        ps.runBlock()
    
        # generate random nonce
        n = [0]*4
        n[0] = random.randint(0,0xFFFFFFFF)
        n[1] = random.randint(0,0xFFFFFFFF)
        n[2] = random.randint(0,0xFFFFFFFF)
        n[3] = random.randint(0,0xFFFFFFFF)    
        
        # send random nonce
        
        ser.write(struct.pack("<I", n[0]))
        ser.write(struct.pack("<I", n[1]))
        ser.write(struct.pack("<I", n[2]))
        ser.write(struct.pack("<I", n[3]))
        
        while(ser.in_waiting == 0):
            pass
        
        #replay_bytes = ser.read(16)
        #replay0 = struct.unpack("<I", replay_bytes[0:4])
        #replay1 = struct.unpack("<I", replay_bytes[4:8])
        #replay2 = struct.unpack("<I", replay_bytes[8:12])
        #replay3 = struct.unpack("<I", replay_bytes[12:16])
        
        #a = (0x61707865 + 589472988) & 0xFFFFFFFF; 
        #d = n[0]^a; 
        #d = ((d<<16) | (d>>16)) & 0xFFFFFFFF;
        #c = (2494332794+d) & 0xFFFFFFFF; 
        #b = 589472988^c;
        #b = ((b<<12) | (b>>24)) & 0xFFFFFFFF;
        
        #a = 0x61707865
        #b = 589472988
        #c = 2494332794
        #d = n[0]
        
        #print "expected: " + hex(a)
        #print "received: " + hex(replay0[0])
        #print "received: " + hex(ord(replay_bytes[0]))
        #print "received: " + hex(ord(replay_bytes[1]))
        #print "received: " + hex(ord(replay_bytes[2]))
        #print "received: " + hex(ord(replay_bytes[3]))
     
        #print "expected: " + hex(d)
        #print "received: " + hex(replay3[0])   
        
        # wait for oscilloscope
        ps.waitReady()    
        ps.stop()
        
        ser.read(1)
        
        time.sleep(0.01)
        
        # collect trace data
        dataA = ps.getDataV("A", 3770)
        time.sleep(0.01)
        dataB = ps.getDataV("B", 3770)
        
        trace = open("traceA" + str(i) + ".pckl", "w")
        pickle.dump(np.array(dataA), trace)
        trace.close()
        
        trace = open("traceB" + str(i) + ".pckl", "w")
        pickle.dump(np.array(dataB), trace)
        trace.close()
        
        nonce = open("nonce" + str(i) + ".pckl", "w")
        pickle.dump(n, nonce)
        nonce.close()

        
                
        
    