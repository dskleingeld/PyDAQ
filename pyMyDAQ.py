"""MAIN FILE"""
import multiprocessing as mp
import numpy as np
import sys

import simpleRead
import feedback
import plotThread

"""
See documentation at: http://zone.ni.com/reference/en-XX/help/370471AA-01/

-Constants are imported from PyDAQmx.DAQmxConstants

-Variables that are not pointers can be used directly,
as they will be automatically converted by ctypes

-For pointers, first declare them and then use byref() 
to pass by referenceNULL in C becomes None in Python
"""

def testProcess(cv):
	cv.set()
	return

def testIfName():
	cv = mp.Event()
	tp = mp.Process(target=testProcess, args = (cv,))
	try:
		tp.start()
	except RuntimeError as e:
		print("CRITICAL ERROR: you forgot to nest your code in: \"'if __name__ == '__main__':\"")
		print("this would cause a crash later in this module exiting")
	else:
		tp.join()
	if(not cv.is_set()):
		sys.exit()

class PyDAQ:
	"""description"""
	def __init__(self):
		testIfName()
		
		self.stop = mp.Event()
		self.rdy = mp.Event()
		
		self.input_write_end, self.input_read_end = mp.Pipe()
		self.output_write_end, self.output_read_end = mp.Pipe()
		
		self.plotting_thread = None
		self.aquisition_thread = None
		self.feedback_thread = None
		
		self.activeChannels = []
		
	def plot(self):
		self.plotting_thread = mp.Process(target = plotThread.plot, 
                      args = (self.input_read_end, self.stop, self.rdy,))

	def aquire(self, inputChannel, samplerate=1000, maxMeasure=10, minMeasure=-10):
		if(self.feedback_thread is not None):
			print("WARNING: You can not run both feedback and aquisition at the same time, "
				 +"not starting aquisition")
		else:
			self.checkIfValidArgs(samplerate, maxMeasure, minMeasure, [inputChannel])
			outputshape = np.full(0, samplerate, dtype = np.float64)
			self.aquisition_thread = mp.Process(target = simpleRead.startReadOnly, 
			     args = (self.input_write_end, self.output_read_end, self.stop,
			     inputChannel, samplerate, maxMeasure, minMeasure,)) 

	def gen(self, inputChannel, samplerate=1000, maxMeasure=10, minMeasure=-10):
		if(self.feedback_thread is not None):
			print("WARNING: You can not run both feedback and aquisition at the same time, "
				 +"not starting aquisition")
		else:
			self.checkIfValidArgs(samplerate, maxMeasure, minMeasure)
			outputshape = np.full(0, samplerate, dtype = np.float64)
			self.aquisition_thread = mp.Process(target = simpleRead.startCallBack, 
			     args = (self.input_write_end, self.output_read_end, 
			     self.stop, outputShape,)) 
 
	def aquireAndGen(self, input, output, outputShape, samplerate=1000, maxMeasure=10, minMeasure=-10):
		if(self.feedback_thread is not None):
			print("WARNING: You can not run both feedback and aquisition at the same time, "
				 +"not starting aquisition")
		else:
			self.checkIfValidArgs(samplerate, maxMeasure, minMeasure)
			self.aquisition_thread = mp.Process(target = simpleRead.startCallBack, 
				 args = (self.input_write_end, self.output_read_end, 
				 self.stop, outputShape,))  

	def feedback(self, transferFunct, samplerate=1000, maxMeasure=10, minMeasure=-10):
		if(self.aquisition_thread is not None):
			print("WARNING: You can not run both feedback and aquisition at the same time, "
				 +"not starting feedback")
		else:
			self.checkIfValidArgs(samplerate, maxMeasure, minMeasure)
			self.feedback_thread = mp.Process(target = feedback.feedback, 
			     args = (self.input_write_end, self.stop, transferFunct,))

	def begin(self):
		if(self.aquisition_thread is not None):
			self.aquisition_thread.start()
		if(self.plotting_thread is not None):
			self.plotting_thread.start()
		if(self.feedback_thread is not None):
			self.feedback_thread.start()

	def menu(self):
		self.rdy.wait()
		input('Press Enter to stop\n')

	def end(self):
		self.stop.set()
		if(self.feedback_thread is not None):
			self.feedback_thread.join()
		if(self.aquisition_thread is not None):
			self.aquisition_thread.join()
		if(self.plotting_thread is not None):
			self.plotting_thread.join()
	
	def checkIfValidArgs(self, samplerate, maxMeasure, minMeasure, channels):
		#check if the inputs are valid
		for channel in channels:
			if(type(channel) == str()):
				if(channel in self.activeChannels):
					print("ERROR: channel ("+channel+") is already in use!")
				else:
					self.activeChannels.append(channel)
		
		if(not -10 < maxMeasure <= 10):
			print("WARNING: maxMeasure  must be > -10 and <= 10 (for the myDAQ)")
		if(not 10 > minMeasure >= -10):
			print("WARNING: minMeasure  must be <= -10 and < 10 (for the myDAQ)")
		if(not 0 < samplerate <= 200000):
			print("WARNING: samplerate must be > 0 and <=200000 (for the myDAQ)")
