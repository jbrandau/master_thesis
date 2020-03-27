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
import sys
import EM_station

# AES Sbox
AES_Sbox = np.array([
            0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
            0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
            0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
            0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
            0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
            0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
            0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
            0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
            0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
            0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
            0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
            0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
            0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
            0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
            0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
            0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
            ])

no_steps_x = 20
no_steps_y = 20
no_steps_z = 0

myEM=EM_station.EM_station('COM31', analysis_steps_x=no_steps_x, analysis_steps_y=no_steps_y, analysis_steps_z=no_steps_z)

if not myEM.is_connected():
    print "EM station not connected"
    sys.exit()

print myEM.get_cur_probe_pos()


myEM.set_pos_A([-123000, 144000, -97000])
myEM.set_pos_B([-75000, 197000, -97000])

fixedData = True
fixedPlaintext = int(random.randint(0,0xFF))
fixedPlaintext2 = int(random.randint(0,0xFF))

myEM.get_cur_probe_pos()
myEM.gen_analysis_map()
print "analysis map completed"

en_oscilloscope = True
if en_oscilloscope == True:
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

#
if __name__ == "__main__":
    num_traces = 100000
    traces_per_file = 50
    samples_per_trace = 500000

    if en_oscilloscope == True:
        le = lecroy.Oscilloscope()
        le.connect()
        le.calibrate()
        le.displayOn()
        le.Samples = samples_per_trace

    if en_oscilloscope == False:
        import Oscilloscope as lecroy
        le = lecroy.Oscilloscope()
        le.connect()
        le.displayOn()

    ser = serial.Serial(
            port='COM37',
            baudrate=9600,
            timeout=None
            )

    if en_oscilloscope == True:
      ts = time.time()
      st = datetime.datetime.fromtimestamp(ts).strftime('SBOX_traces%Y-%m-%d_%H_%M_%S/')
      if not os.path.exists(st):
        os.makedirs(st)
        os.chdir(st)

    ser.reset_input_buffer()

    time.sleep(0.5)
    write(ser,0xDE)
    time.sleep(0.5)
    write(ser,0xAD)
    time.sleep(0.5)
    write(ser,0xBE)
    time.sleep(0.5)
    write(ser,0xEF)
    time.sleep(0.5)

    check_first = 0
    got_dead_beef = 0
    dead_beef_start = 0

    while(got_dead_beef == 0):
        while ser.in_waiting:
          no_bytes_received = ser.in_waiting
          print no_bytes_received
          dead_beef = ser.read(no_bytes_received)
          for oo in range(0,no_bytes_received):
            if(ord(dead_beef[oo]) == 0xDE):
              dead_beef_start = 1
              break

          start_dead_beef_no = oo
        if(ord(dead_beef[oo+0]) == 0xDE and ord(dead_beef[oo+1]) == 0xAD and ord(dead_beef[oo+2]) == 0xBE and ord(dead_beef[oo+3]) == 0xEF):
          got_dead_beef = 1

    print("GOT DEAD BEEF CHECK....")
    collectLocation = []
    posLabel = "label"
    posTraces = "traces"
    posCords = "cords"
    for x_pos in xrange(0,no_steps_x):
        for y_pos in range(0,no_steps_y):
          myEM.perform_analysis_step()
          prob_pos = myEM.get_cur_probe_pos()
          print(prob_pos)
          if(x_pos*no_steps_x+y_pos == 92):
            time.sleep(0.1)
            if en_oscilloscope == True:
                position = "spot_%d_%d" %(x_pos,y_pos)
                if not os.path.exists(position):
                    os.makedirs(position)
                os.chdir(position)

            tracesA = np.empty((traces_per_file, samples_per_trace),np.uint8)
            nonces = np.empty((traces_per_file, 1), np.uint8)
            noncesA = np.empty((traces_per_file, 1), np.uint8)
            msg2 = [0]
            msg3 = [0]
            collectedLabels = []
            tmpPosition = "spot_%d_%d" %(x_pos,y_pos)
            collectLocation.append([prob_pos,tmpPosition])

            myCounter=0

            collectedPlaintext = []
            collectedPlaintextFirst = []

            average = 19

            numPlaintext = num_traces / (average+1)

            switcher = 0
            if fixedData == True:

              tmpKey = []
              for i in range(0,16):
                if i == 0:
                  firstBit = fixedPlaintext
                  tmpKey.append(hex(firstBit))
                else:
                  tmpKey.append(hex(int(random.randint(0,0xFF))))

              tmpKey2 = []
              for i in range(0,16):
                if i == 0:
                  firstBit = fixedPlaintext2
                  tmpKey2.append(hex(firstBit))
                else:
                  tmpKey2.append(hex(int(random.randint(0,0xFF))))

              for i in range(0,num_traces):
                if switcher == 0:
                  collectedPlaintext.append(tmpKey)
                  collectedPlaintextFirst.append(fixedPlaintext)
                  switcher = 1
                else:
                  collectedPlaintext.append(tmpKey2)
                  collectedPlaintextFirst.append(fixedPlaintext2)
                  switcher = 0
              len(collectedPlaintext)
              print(collectedPlaintext[0])
              print(collectedPlaintext[1])
              print(collectedPlaintext[2])
              print(collectedPlaintext[3])

            else:

              for i in range(0,numPlaintext):
                tmpKey = []
                for i in range(0,16):
                  if i == 0:
                    firstBit = int(random.randint(0,0xFF))
                    tmpKey.append(hex(firstBit))
                    collectedPlaintextFirst.append(firstBit)
                  else:
                    tmpKey.append(hex(int(random.randint(0,0xFF))))
                collectedPlaintext.append(tmpKey)

            plaintextPos = 0
            switcher = 0
            for i in xrange(0, num_traces):
                  trace_mod = i%traces_per_file

                  le.trigger()
                  tmpLabel = []
                  firstBit = 0

                  if fixedData == True:
                    msg2[0] = collectedPlaintext[plaintextPos]
                    tmpLabel = collectedPlaintextFirst[plaintextPos]
                    plaintextPos = plaintextPos + 1
                  else:
                    if myCounter == 0:
                      msg2[0] = collectedPlaintext[plaintextPos]
                      tmpLabel = collectedPlaintextFirst[plaintextPos]
                      myCounter = myCounter + 1
                    elif myCounter == average:
                      msg2[0] = collectedPlaintext[plaintextPos]
                      tmpLabel = collectedPlaintextFirst[plaintextPos]
                      plaintextPos = plaintextPos + 1
                      myCounter = 0
                    else:
                      msg2[0] = collectedPlaintext[plaintextPos]
                      tmpLabel = collectedPlaintextFirst[plaintextPos]
                      myCounter = myCounter + 1

                  for k in range(0,16):
                    ser.write(struct.pack("B", int(msg2[0][k],16) ))


                  read_byte = ser.read(1)
                  key = 23

                  #checkSum = AES_Sbox[tmpLabel^key]

                  #if(checkSum != ord(read_byte)):
                    #print('msg2',msg2[0])
                    #print('checksum',checkSum)
                    #print('label',tmpLabel)
                    #print('device',ord(read_byte))
                    #print "Something wrong"

                  collectedLabels.append(tmpLabel)

                  for xxx in range(1):
                      msg3[xxx] = ord(read_byte[xxx])

                  if en_oscilloscope == True:
                      if(i%traces_per_file == traces_per_file-1):
                        time.sleep(0.1)
                        seqtrace = le.getWaveform_8_1()[0:samples_per_trace*traces_per_file]
                        tmp_traces = np.split(seqtrace,seqtrace.shape[0]/samples_per_trace)

                        if not os.path.exists(posTraces):
                          os.makedirs(posTraces)
                        os.chdir(posTraces)
                        spio.savemat("traces_" + str(i+1), {'data': tmp_traces}, do_compression=True, oned_as='row')
                        os.chdir("..")

                        if not os.path.exists(posLabel):
                          os.makedirs(posLabel)
                        os.chdir(posLabel)
                        spio.savemat("labels_"+ str(i+1), {'data': collectedLabels}, do_compression=True, oned_as='row')
                        os.chdir("..")
                        collectedLabels = []
                        print "Saving file " + str(time.time() - ts) + " seconds"
                        print "Collected traces: " + str(i+1)
            os.chdir("..")

            if not os.path.exists(posCords):
              os.makedirs(posCords)
            os.chdir(posCords)
            spio.savemat("cord_"+ str(i+1), {'data': collectLocation}, do_compression=True, oned_as='row')

            os.chdir("..")
    os.chdir("..")
