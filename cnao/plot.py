import pandas as pd
from datetime import datetime, timedelta
import collections 
import matplotlib.pyplot as plt
import numpy as np
import sys
import tkinter as tk
import curses
import time

runno, mzb = str(sys.argv[1]), int(sys.argv[2])

names_1 = ["Iin 32V", "Iin 8V", "Iin 5V", "Iin 3V3", "Iout 3V3", "Iout 5V", "Vout 3V3", "Vout 5V", "Vout 8V", "CPU I", "Iin SPI", "I U1", "I U4U9", "I USB", "I HV"]
names_2 = ["Iin 32V", "Iin 5V", "Iin 8V", "Vout 8V", "I CPU"]

if mzb==1 or mzb ==0:
   fig1, axs1 = plt.subplots(5, 3, sharex=True)
   pl1 = [0]*15
   for i in range(15):
       pl1[i], = axs1[i//3][i%3].plot([], [])
       pl1[i].set_color("black")
       axs1[i//3][i%3].title.set_text(F"ch{i+1}:" + names_1[i])
       axs1[i//3][i%3].title.set_color("blue")

if mzb==2 or mzb==0:
  fig2, axs2 = plt.subplots(5, sharex=True)
  pl2 = [0]*5
  for i in range(15, 20):
      idx = i-15
      pl2[idx], = axs2[i-15].plot([], [])
      pl2[idx].set_color("black")
      axs2[idx].title.set_text(F"ch{i+1}:" + names_2[idx])
      axs2[idx].title.set_color("blue")

plt.ion()
plt.show()

try:
  data = pd.read_csv(F"data/{runno}/dat00001.csv")
  # data = pd.read_csv(F"{runno}")
except Exception as exc:
    print("---> error: " +  str(exc))
    sys.exit(-1)
  
data.columns = ["sweep"] + ["time"] + [f"ch{100+i}" for i in range(1, 20+1)]
data["time"] = pd.to_datetime(data["time"]) #, format='%Y-%m-%d %H:%M:%S.%f')
data["time_corr"] = data["time"].dt.tz_localize('Europe/Rome').dt.tz_convert('America/Los_Angeles')  
print(data)

hfrom = data["time_corr"][0]
hdeltadef = timedelta(minutes=3, seconds=0)
hdelta = hdeltadef

try:
    while(True):
      try:

        inp = input("tTstart (HH.MM) [tRange (HH.MM.SS)]:   ")
        inp = inp.split(" ")
        hfrom = datetime.strptime(inp[0], "%H.%M")
        if len(inp) == 2:
          hdeltain = datetime.strptime(inp[1], "%H.%M.%S")
          hdelta = timedelta(hours=hdeltain.hour, minutes=hdeltain.minute, seconds=hdeltain.second)
        hto = hfrom + hdelta

        subdf = data[(data["time_corr"].dt.time>=hfrom.time()) & (data["time_corr"].dt.time<=hto.time())]
        tmin = subdf['time_corr'].min()
        titl = F"from [{hfrom.time()}] to [{hto.time()}]"
        print(subdf)

        if mzb==1 or mzb==0:
          for i in range(15):
            pl1[i].set_xdata((subdf['time_corr']-tmin))
            pl1[i].set_ydata(subdf[f"ch{100 + i+1}"])
            axs1[i//3][i%3].relim()
            axs1[i//3][i%3].autoscale_view()
            fig1.suptitle(titl, fontsize=20, color="red")
        if mzb==2 or mzb==0:
          for i in range(15, 20):
            pl2[i-15].set_xdata((subdf['time_corr']-tmin))
            pl2[i-15].set_ydata(subdf[f"ch{100 + i+1}"])
            axs2[i-15].relim()
            axs2[i-15].autoscale_view()
            fig2.suptitle(titl, fontsize=20, color="red")

        plt.draw()

      except Exception as exc:
        print("---> error: " +  str(exc))

except KeyboardInterrupt:
    print('\n---> closing')
    sys.exit()
