# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 10:06:35 2012

@author: sobsen
"""


import win32com.client
import numpy
import time

class Oscilloscope():
  def __init__(self):
    self.xlApp = win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")
    self.TimeBase = 0
    self.Samples = 0
    self.SampleRate = 0
    self.NumberOfSequence = 0
  
  def connect(self):
    if self.xlApp.MakeConnection("IP: localhost") != True:
      return False
    # get scope info
    self.xlApp.WriteString('*IDN?', True)
    answer = self.xlApp.ReadString(1000)
    # set high timeout for sequence mode, so the scope waits for the whole measurement to finish
    self.xlApp.SetTimeout(1000)
    self.xlApp.WaitForOPC()
    return answer
  
  def getParameters(self):
    # Read out Timebase, number of samples, samplerate and number of segments
    self.xlApp.WriteString("TIME_DIV?", True)
    temp = self.xlApp.ReadString(1000)
    try:
      self.TimeBase = (float(temp.split("E")[0]) * (10 ** int(temp.split("E")[1])))
    except:
      self.TimeBase = int(temp)
    #print 'Time measured in one trace: %fs (%fs/div)' % (self.TimeBase, self.TimeBase/10)

    self.xlApp.WriteString('VBS? return = app.Acquisition.Horizontal.NumPoints', True)
    temp = self.xlApp.ReadString(1000)
    try:
      self.Samples = int(float(temp.split("E")[0]) * (10 ** int(temp.split("E")[1])))
    except:
      self.Samples = int(float(temp))
    #print 'Samples in one Trace: %d' % self.Samples
    self.SampleRate = int(1.0 / (self.TimeBase * 10) * self.Samples)
    #print 'Sample rate: %d S/s' % self.SampleRate

    self.xlApp.WriteString("SEQ?", True)
    temp = self.xlApp.ReadString(1000)
    if temp.split(',')[0] == 'ON':
      self.NumberOfSequence = int(temp.split(',')[1])
      #print 'Number of segments: %d' % self.NumberOfSequence
    else:
      #print 'Sequence mode deactivated.'
      self.NumberOfSequence = 1
      
    return self.NumberOfSequence, self.SampleRate, self.Samples, self.TimeBase
    
  def trigger(self):
    self.xlApp.WriteString("ARM", True)
    self.xlApp.WaitForOPC()
    self.xlApp.WriteString("WAIT", True)
    
  def getWaveform2(self):
    return numpy.frombuffer(self.xlApp.GetByteWaveform("C2", self.Samples, 0), numpy.uint8)
    
  def getWaveform3(self):
    return numpy.frombuffer(self.xlApp.GetByteWaveform("C3", self.Samples, 0), numpy.uint8)

  def getWaveform4(self):
    return numpy.frombuffer(self.xlApp.GetByteWaveform("C4", self.Samples, 0), numpy.uint8)

  def getWaveform1(self):
    return numpy.frombuffer(self.xlApp.GetByteWaveform("C1", self.Samples, 0), numpy.uint8)
    
  def disconnect(self):
    self.xlApp.Disconnect()
    
  def calibrate(self):
    self.xlApp.WriteString("*CAL?", True)
    self.xlApp.WaitForOPC()
    
  def displayOff(self):
    self.xlApp.WriteString("DISPLAY OFF", True)
    
  def displayOn(self):
    self.xlApp.WriteString("DISPLAY ON", True)
    
  def saveSetup(self, directory):
    #self.xlApp.WriteString("DIR DISK, HDD, '%s'" % directory, True)
    self.xlApp.WriteString("STPN DISK, HDD, FILE, '%s'" % (directory + '\config.lss'), True)
    
  def deactivateSequence(self):
    self.xlApp.WriteString("SEQ OFF", True)
    
  def clearsweeps(self,channel_number):
    if(channel_number == 1):
      self.xlApp.WriteString("VBS 'app.Acquisition.C1.ClearSweeps'", True)
    elif(channel_number == 2):
      self.xlApp.WriteString("VBS 'app.Acquisition.C2.ClearSweeps'", True)
    elif(channel_number == 3):
      self.xlApp.WriteString("VBS 'app.Acquisition.C3.ClearSweeps'", True)
    elif(channel_number == 4):
      self.xlApp.WriteString("VBS 'app.Acquisition.C4.ClearSweeps'", True)
  
  def clearsweeps_all(self):
    self.xlApp.WriteString("VBS 'app.ClearSweeps'", True)