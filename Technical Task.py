import numpy as py
import pandas as pd
import tkinter as tk


## setting pitch boundaries
upper_x_boundary=52.5
lower_x_boundary=-52.5

upper_y_boundary=34
lower_y_boundary=-34

### Select and read a specified CSV File, can be automated if need be


from tkinter.filedialog import askopenfilename
from tkinter import Tk
name1=Tk()
name1.withdraw()

name1.call('wm','attributes','.','-topmost', True)
filename = askopenfilename()
print(filename)


## save CSV into a dataframe

data = pd.read_csv(filename)
index_names=[]
ids = []

for i in range(len(data)):
    tmp = data.at[i,data.columns[0]]  # Temporary datafile to save participant name
    index_names.append(tmp)
    if tmp not in ids:
        ids.append(tmp)

## defining moving average algorithm
def movingaverage(interval, window_size):
    window= py.ones(int(window_size))/float(window_size)
    return py.convolve(interval, window, 'same')

data.index=index_names
trials=data.filter(like=ids[1],axis=0)

speeds=[]
tmp=[]
x_list=[]
y_list=[]
time_list=[]
for i in range(len(ids)):
    speeds.append(list(data.at[ids[i],'Speed (m/s)']))
    x_list.append(list(data.at[ids[i],'Pitch_x']))
    y_list.append(list(data.at[ids[i],'Pitch_y']))
    time_list.append(list(data.at[ids[i],'Time (s)']))
        
speeds_df=pd.DataFrame(speeds,ids)
position_x=pd.DataFrame(x_list,ids)
position_y=pd.DataFrame(y_list,ids)
time=pd.DataFrame(time_list,ids)

## Fast Fourier Transform - smoothing speed data

speeds_smoothed=[]
for i in range(len(speeds)):
    rft=py.fft.rfft(speeds[i])
    rft[1000:]=0
    y_smooth=py.fft.irfft(rft)
    speeds_smoothed.append(list(y_smooth))

## moving point average(Taking 5 values)

speeds_moving_avg=[]
position_x_mov_avg=[]
position_y_mov_avg=[]
time_mov_avg=[]


for i in range(len(speeds_df)):
    speeds_moving_avg.append(list(3.6*movingaverage(speeds_smoothed[i],5))) ## changing to kmph
    position_x_mov_avg.append(list(movingaverage(position_x.loc[ids[i]],5)))
    position_y_mov_avg.append(list(movingaverage(position_y.loc[ids[i]],5)))
    time_mov_avg.append(list(movingaverage(time.loc[ids[i]],5)))
  
speeds_moving_avg_df=pd.DataFrame(speeds_moving_avg,ids)
position_x_mov_avg_df = pd.DataFrame(position_x_mov_avg,ids)
position_y_mov_avgdf = pd.DataFrame(position_y_mov_avg,ids)
time_mov_avgdf = pd.DataFrame(time_mov_avg,ids)
    
speeds_moving_avg_df=pd.DataFrame(speeds_moving_avg,ids)

# Time spend at Speed Zone 5

dist_zone_5y=[]
dist_zone_5x=[]
dist_z5_save_x=[]
dist_z5_save_y=[]

## x and y points spent at zone 5

for i in range(len(speeds_moving_avg)):
    for j in range(len(speeds_moving_avg[i])):
        if speeds_moving_avg[i][j] > 19.8 and speeds_moving_avg[i][j] < 25.1 and (lower_x_boundary<x_list[i][j]<upper_x_boundary and lower_y_boundary<y_list[i][j]<upper_y_boundary):
            dist_zone_5x.append(x_list[i][j])
            dist_zone_5y.append(y_list[i][j])
        else:
            dist_zone_5x.append(0)
            dist_zone_5y.append(0)
    dist_z5_save_x.append(dist_zone_5x)
    dist_z5_save_y.append(dist_zone_5y)

    dist_zone_5x=[]
    dist_zone_5y=[]

## converting x and y into directional information

dist_zone_5z=[]
dist_zone_5z_save=[]
for i in range(len(dist_z5_save_x)):
    for j in range(len(dist_z5_save_x[i])):
        if dist_z5_save_x[i][j]!=0 and dist_z5_save_x[i][j+1]!=0 and (lower_x_boundary<x_list[i][j]<upper_x_boundary and lower_y_boundary<y_list[i][j]<upper_y_boundary):
            temp_x=abs(dist_z5_save_x[i][j+1])-abs(dist_z5_save_x[i][j])
            temp_y=abs(dist_z5_save_y[i][j+1])-abs(dist_z5_save_y[i][j])
            if (temp_x!=0 or temp_y!=0):
                dist_zone_5z.append((temp_x**2+temp_y**2)**0.5)
    
    dist_zone_5z_save.append(dist_zone_5z)
    dist_zone_5z=[]

sum_dist_zone_5=[]
for i in range(len(dist_zone_5z_save)):
    sum_dist_zone_5.append(sum(dist_zone_5z_save[i]))    
    
sum_dist_zone_5_df= pd.DataFrame(sum_dist_zone_5,ids)
sum_dist_zone_5_df=sum_dist_zone_5_df.sort_values(by=[sum_dist_zone_5_df.columns[0]],ascending=False) 
sum_dist_zone_5_df.columns=['Total Distance at Zone 5 on pitch  (m) ']

### length of time played in game

### total distance covered
z=[]
z_store=[]
for i in range(len(ids)):
    for j in range(len(x_list[i])-1):
        if lower_x_boundary<x_list[i][j]<upper_x_boundary and lower_y_boundary<y_list[i][j]<upper_y_boundary:
            temp_x=abs(x_list[i][j+1])-abs(x_list[i][j])
            temp_y=abs(y_list[i][j+1])-abs(y_list[i][j])
            if (temp_x!=0 or temp_y!=0):
                z.append((temp_x**2+temp_y**2)**0.5)
    z_store.append(list(z))
    z=[]           
    
dist_travelled=[]
for i in range(len(z_store)):
    dist_travelled.append(sum(z_store[i]))
    
    
## Sorted distance travelled

dist_travelled_df=pd.DataFrame(dist_travelled,ids)
dist_travelled_df=dist_travelled_df.sort_values(by=[dist_travelled_df.columns[0]],ascending=False) 
dist_travelled_df.columns=['Total Distance Covered on pitch (m)']

## top speed for > 0.5 s

max_moving_avg=[]
for i in range(len(speeds_moving_avg)):
    max_moving_avg.append(0.99*max(speeds_moving_avg[i])) ##0.99 chosen through trial and error with 0.99*max speeds shows to yield good results 
        
max_moving_avg_df=pd.DataFrame(max_moving_avg,ids)
max_moving_avg_df=max_moving_avg_df.sort_values(by=[max_moving_avg_df.columns[0]],ascending=False) 
max_moving_avg_df.columns=['Max Speeds on pitch (km/h)']

# time spend on pitch
time_outside_pitch=[]
time_outside_pitch_save=[]
for i in range(len(time_list)):
    time_outside_pitch=[]
    for j in range(len(time_list[i])):
        if lower_x_boundary<x_list[i][j]<upper_x_boundary and lower_y_boundary<y_list[i][j]<upper_y_boundary:
            time_outside_pitch.append(time_list[i][j])
    time_outside_pitch_save.append(time_outside_pitch)

length_time_on_pitch=[]
for i in range(len(time_outside_pitch_save)):
    length_time_on_pitch.append(round(0.1*len(time_outside_pitch_save[i]),2))
length_time_on_pitch_df=pd.DataFrame(length_time_on_pitch,ids)
length_time_on_pitch_df=length_time_on_pitch_df.sort_values(by=[length_time_on_pitch_df.columns[0]],ascending=False)
length_time_on_pitch_df.columns=['Length of Time on Pitch (s)']

## Distance travelled per second on pitch
distance_per_second=[]
for i in range(len(length_time_on_pitch)):
    distance_per_second.append((dist_travelled[i]/length_time_on_pitch[i]))

distance_per_second_df=pd.DataFrame(distance_per_second,ids)
distance_per_second_df=distance_per_second_df.sort_values(by=[distance_per_second_df.columns[0]],ascending=False) 
distance_per_second_df.columns=['Average Speed on pitch (m/s)']


## Sending Leaderboards to Excel

## Selecting folder for Excel to be saved into
name1=Tk()
name1.withdraw()

name1.call('wm','attributes','.','-topmost', True)
foldername=tk.filedialog.askdirectory()

excel_location_name=foldername+'/Technical Task Output.xlsx'

with pd.ExcelWriter(excel_location_name) as writer:
    dist_travelled_df.to_excel(writer,sheet_name='Total Distance')
    sum_dist_zone_5_df.to_excel(writer,sheet_name='Total Distance at Zone 5')
    max_moving_avg_df.to_excel(writer,sheet_name='Max Speeds')
    length_time_on_pitch_df.to_excel(writer,sheet_name='Total Time on Pitch')
    distance_per_second_df.to_excel(writer,'Average Speed on pitch')
