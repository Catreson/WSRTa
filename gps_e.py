import sys
import time
import pandas as pd
filet = sys.argv[1]
print(filet)
filnam = filet.split('.')
time.sleep(3)
file = open(filet, 'r')
nam = f'{filnam[0]}ek.csv'
ilef = open(nam, 'w')
prevline = file.readline()
prevlin = prevline.split(',')
timdfrift = 0
for line in file:
    lin = line.split(',')
    if lin[0] == 'gps' and prevlin[0] != 'gps':
        timdrift = round(float(prevlin[1]) - float(lin[1]))
        print(timdrift)
        break
    prevlin = lin
file.close()
file = open(filet, 'r')
prevline = file.readline()
for line in file:
    lin = line.split(',')
    if lin[0] == 'gps':
        try:  
            pom = lin[2].split(' ') 
            lat = pom[0]
            lon = pom[1]
            ilef.write(f'gps,{float(lin[1]) + timdrift},{lat} {lon} {pom[2]} {pom[3]} {pom[4]} {pom[5]},bike/sensor/gps,string\n')
        except:
            try:
                pom = lin[2].split(' ') 
                lat = pom[0]
                lon = pom[1]
                ilef.write(f'gps,{float(lin[1]) + timdrift},{lat} {lon} {pom[2]} {pom[3]},bike/sensor/gps,string\n')
            
            except:
                print('Err')
    elif lin[0] == 'gyro':
        print('gyro')
    else:
        ilef.write(line)
print('Done')
ilef.close()
df_csv = pd.read_csv(nam, names = ['tag', 'timestamp', 'value', 'topic', 'datatype'] )
df_csv.sort_values("timestamp", axis=0, ascending=True,inplace=True, na_position='first')
df_csv.to_csv(f'{filnam[0]}eksort.csv', index=False)

filet = f'{filnam[0]}eksort.csv'
print(filet)
filnam = filet.split('.')
time.sleep(3)
file = open(filet, 'r')
ilef = open(f'{filnam[0]}er.csv', 'w')
err = 0
for i in range(5):
    dumper = file.readline()
for line in file:
    lin = line.split(',')
    if lin[0] != 'err':
        ilef.write(line)
    else:
        err += 1
print(f'Found {err} errors')
time.sleep(5)
print('Done')

time.sleep(3)