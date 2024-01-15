# WSRTa
 Desktop data analysis software for WSRT<br>
 Designed to provide free tool for data analysis from different acquisition systems simultaneously.<br>
 Made using TkInter.<br>
 When first acceptable debugged version will be ready, I will post standalone built for Windows and howto instruction.<br>
# Main fetures in currently developed version:<br>
- Parsing our motorcycle .CSV "event" long format to uniform (.WSRT) wide format, with linear interpolation.
- Getting individual laps from .WSRT file, selecting finish line by drawing it on a map.
- MapView, plot and scatter tiles for data analysis.
- Ability to personalize workspace, using tabs and window splitting.
- Calculating accelerations from GPS data.
- MAF to smoothen data.
- Data presented in track distance domain (value bond to position on track, not in time)

# In progress features for currently developed version:
- MAF in pre interpolated data.
- Templates of workspace, to simply load preset instead of building it each time.
- STFT and EPWT both presented using 3d graphs.
- Table tile to sum up averages, extremes etc. in laps.
- Speeding up using numpy and njit.
- Parsing exported files from different acquisition systems.
- Splitting laps into sectors, and displaying split times and delta.
- Ability to display data in time domain (Single lap mode)
 
![image](https://drive.google.com/uc?export=view&id=1w2s9aP4xihyk9KIfzjXe3ejKiZp8BCnL)

![image](https://drive.google.com/uc?export=view&id=1n7396hKhAYFeBRDLrWgS4heRuPzZT0bM)
