import pyMyDAQ as pd
import numpy as np

def transferFunct(buffer,lastvalue):
	if buffer[-1]<4: return np.array([6])
	if buffer[-1]>6: return np.array([4])
	return np.array([3])
	




if __name__ == '__main__':
	pd = pd.PyDAQ()

	#configure
	pd.setFileOptions(name="testData", format="csv")
	pd.onlyFeedback("myDAQ1/ai0","myDAQ1/ao0", transferFunct,samplerate=100, maxMeasure=6)
     pd.onlyAquire()
	
	pd.begin()
	pd.menu()
	pd.end()	