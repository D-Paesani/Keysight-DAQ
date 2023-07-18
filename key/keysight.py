
#import visa
import pyvisa as visa

import pandas as pd

from datetime import datetime

import collections 

import matplotlib.pyplot as plt

import numpy as np

import sys

import keyboard

import tkinter as tk

import curses

import time

'''
Initialize the 34970A/72A and dirvers
load visa lib and open connection
Visa address used 'GPIB0::12::INSTR' can be found in Keysight Connection Expert
'''

rm = visa.ResourceManager()
instr = rm.open_resource('TCPIP::K-DAQ970A-18576.local::5025::SOCKET')    

instr.timeout=5000      #set a delay

instr.read_termination = '\n'
instr.write_termination = '\n'

print("starting com")
instr.write("ROUTE:SCAN:SIZE?") 
numberChannels = int(instr.read())


names_1 = ["101_I_in_32V", "102_I_in_8V", "103_I_in_5V", "104_I_in_3V3", "105_I_out_3V3", "106_I_out_5V", "107_V_out_3V3", "108_V_out_5V", "109_V_out_8V", "110_CPU_I", "111_SPI_I", "112_U1_I", "113_U4U9_I", "114_USB_I", "115_HV_I"]
names_2 = ["116_I_in_32V", "117_I_in_5V", "118_I_in_8V", "119_V_out_8V", "120_CPU_I"]


mzb = int(sys.argv[1])

if mzb==1 or mzb ==0:
   fig1, axs1 = plt.subplots(5, 3, sharex=True)
   pl1 = [0]*15
   for i in range(15):
       pl1[i], = axs1[i//3][i%3].plot([], [])
       axs1[i//3][i%3].title.set_text(names_1[i])

if mzb==2 or mzb ==0:
  fig2, axs2 = plt.subplots(5, sharex=True)
  pl2 = [0]*5
  for i in range(15, 20):
      pl2[i-15], = axs2[i-15].plot([], [])
      axs2[i-15].title.set_text(names_2[i-15])


plt.ion()
plt.show()


nominal_mean = {
  'ch101': 0.3190711, 'ch102': 0.1714851, 'ch103': 0.0853016, 'ch104': 0.0577973, 'ch105': 0.0737106,
  'ch106': 0.0097351, 'ch107': 3.318729, 'ch108': 4.9387359, 'ch109': 8.0009518, 'ch110': 0.0687609,
  'ch111': 0.0003103, 'ch112': 5.7e-06, 'ch113': 0.0012845, 'ch114': 0.0019869, 'ch115': 0.0016936,
  'ch116': 0.1853199, 'ch117': 0.0190895, 'ch118': 0.0035553, 'ch119': 8.0470995, 'ch120': 0.0715978
}

#nominal_std = {'ch101': 0.000835, 'ch102': 0.000787, 'ch103': 2.6e-05, 'ch104': 3.4e-05, 'ch105': 0.003906, 'ch106': 0.001672, 'ch107': 0.000395, 'ch108': 0.000681, 'ch109': 0.000995, 
#'ch110': 0.003457, 'ch111': 8e-05, 'ch112': 3.1e-05, 'ch113': 0.00617, 'ch114': 0.000232, 'ch115': 5e-06, 'ch116': 0.000667, 'ch117': 0.000413, 'ch118': 0.001793, 'ch119': 0.001103, 
#'ch120': 0.004436}

nominal_max = {
  'ch101': 0.360, 'ch102': 0.190, 'ch103': 0.095, 'ch104': 0.070, 'ch105': 0.080,
  'ch106': 0.050, 'ch107': 3.4, 'ch108': 5.2, 'ch109': 8.2, 'ch110': 0.085,
  'ch111': 0.030, 'ch112': 0.010, 'ch113': 0.020, 'ch114': 0.005, 'ch115': 0.002,
  'ch116': 0.215, 'ch117': 0.030, 'ch118': 0.025, 'ch119': 8.1, 'ch120': 0.09
}

nominal_min = {
  'ch101': 0.290, 'ch102': 0.150, 'ch103': 0.075, 'ch104': 0.050, 'ch105': 0.060,
  'ch106': 0.006, 'ch107': 3.2, 'ch108': 4.8, 'ch109': 7.8, 'ch110': 0.055,
  'ch111': 0, 'ch112': 0, 'ch113': 0, 'ch114': 0, 'ch115': 0.001,
  'ch116': 0.155, 'ch117': 0.005, 'ch118': 0.001, 'ch119': 7.9, 'ch120': 0.05
}


#sigma_tol = 1


# f = open("keysigth_data/out.csv", "w")

rows_list = []
buffer = collections.deque(maxlen=1000) # ~3min penso

count = 0

def main(stdscr):
  stdscr.nodelay(True)  # do not wait for input when calling getch
  return stdscr.getch()
  
t_start = datetime.utcnow().strftime('%H:%M:%S')

print(F"-------- starting log {t_start}")
time.sleep(3)

enable_reset = 0
n_en_cycles = 100
n_en_cnt = 0

print("starting loop")

try:
    while(True):

      time.sleep(0.05)

      akey = curses.wrapper(main)

      if(enable_reset):
        n_en_cnt +=1
        if(akey==49):  
          n_en_cnt = 0
          print("---- resetting MB1 !!! \n")
          instr.write("ROUTE:CLOSE (@201)")
          time.sleep(3)
          instr.write("ROUTE:OPEN (@201)")
        if(akey==50): 
          n_en_cnt = 0
          print("---- resetting MB2 !!! \n")
          instr.write("ROUTE:CLOSE (@202)")
          time.sleep(3)
          instr.write("ROUTE:OPEN (@202)")
        if(akey==51):  
          n_en_cnt = 0
          print("---- resetting ALB !!! \n")
          instr.write("ROUTE:CLOSE (@203)")
          time.sleep(2)
          instr.write("ROUTE:OPEN (@203)")
        if(akey==112):  
          n_en_cnt = 0
          print("---- panic button: off ALB supply !!! \n")
          instr.write("ROUTE:CLOSE (@203)")
        if(akey==115):  
          n_en_cnt = 0
          print("---- restarting ALB !!! \n")
          instr.write("ROUTE:OPEN (@203)")

      if(n_en_cnt > n_en_cycles):
        n_en_cnt = 0
        enable_reset = 0
        print("---- reset timeout: disabled \n")

      if(akey==101):  
        print("---- reset enabled \n")
        enable_reset = 1

      '''wait until there is a data available'''
      points = 0
      while (points==0):
          instr.write("DATA:POINTS?")
          points=int(instr.read())

      '''
      The data points are printed 
      data, time, channel
      '''
      data = {}

      doprint = 1

      for chan in range(1, numberChannels+1):
          # instr.write("DATA:REMOVE? 1")
          instr.write(F"DATA:LAST? (@{100+chan})")
          str = instr.read()
          if doprint: print(str)
          reading = float(str.split(' ')[0]) #float(f"{float(str.split(' ')[0]):.3e}")
          n_ch = str.split(",")[2]

          data[f"ch{n_ch}"] = reading
          data["timestamp"] = datetime.utcnow().strftime('%Y/%m/%d;%H:%M:%S.%f')
          #f.write(f"{float(r.split(' ')[0]):.2e}")
          #if chan != numberChannels: f.write(",")

          # points = 0
          # #wait for data
          # while (points==0):
          #     instr.write("DATA:POINTS?")
          #     points=int(instr.read())

      #f.write("\n")
      if doprint: print("\n\n")
      rows_list.append(data)
      buffer.append(data)
      if len(rows_list) > 10:
          df = pd.DataFrame(rows_list)
          df = df.reindex(sorted(df.columns), axis=1)
          df.to_csv(f"keysight_data/out_{t_start}.csv", index=False, mode="a", header=None)
          rows_list = []

      count += 1
      if count == 10:
          count = 0

          df = pd.DataFrame(list(buffer))
          df = df.reindex(sorted(df.columns), axis=1)

          df.columns = [f"ch{100+i}" for i in range(1, 20+1)] + ["timestamp"]

          for key in nominal_mean:
            idx_ch = int(key[2:]) - 101
            tocheckdf = df.iloc[-100:]
            status = 1 * int((tocheckdf[key] < nominal_min[key]).sum() > 0) + 2 * int((tocheckdf[key] > nominal_max[key]).sum() > 0) + 0
            colors = ["blue", "orange", "red"]
            status = status if status < 3 else 2
            colo = colors[status]

            if idx_ch < 15 and (mzb==1 or mzb==0):
              pl1[idx_ch].set_color(colo)
            else:
              if idx_ch >= 15 and mzb==2 or mzb==0:
                pl2[idx_ch-15].set_color(colo)



          df['timestamp'] =  pd.to_datetime(df['timestamp'], format='%Y/%m/%d;%H:%M:%S.%f')

          tmax = df['timestamp'].max()

          df['timestamp'] = (df['timestamp'] - tmax) / np.timedelta64(1, "s")

          if mzb==1 or mzb==0:
            for i in range(15):
              pl1[i].set_xdata(df['timestamp'])
              pl1[i].set_ydata(df[f"ch{100 + i+1}"])
              axs1[i//3][i%3].relim()
              axs1[i//3][i%3].autoscale_view()
          if mzb==2 or mzb==0:
            for i in range(15, 20):
              pl2[i-15].set_xdata(df['timestamp'])
              pl2[i-15].set_ydata(df[f"ch{100 + i+1}"])
              axs2[i-15].relim()
              axs2[i-15].autoscale_view()

          plt.draw()
          plt.pause(0.001)

except KeyboardInterrupt:
    print('close instrument connection')
    instr.close()
    #f.close()
    df = pd.DataFrame(rows_list)
    df = df.reindex(sorted(df.columns), axis=1)
    df.to_csv(f"keysight_data/out_{t_start}.csv", index=False, mode="a", header=None)

    print(dict(df.mean()))
