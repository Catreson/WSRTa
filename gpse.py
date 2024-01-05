import sys
import csv 

def findTimeDrift(filename):
    timdrift = 1
    with open(filename, 'r') as file:
        prevline = file.readline()
        prevlin = prevline.split(',')
        for line in file:
            lin = line.split(',')
            if lin[0] == 'gps' and prevlin[0] != 'gps':
                timdrift = round(float(prevlin[1]) - float(lin[1]))
                print(f'timdriftf : {timdrift}')
                break
            prevlin = lin
    return timdrift

def prepareForSas(filename, timdrift = 0, save_file = False):
    outp = []
    with open(filename, 'r') as file:
        err = 0
        for i in range(5):
            dumper = file.readline()
        for line in file:
            lin = line.split(',')
            if lin[0] == 'gps':
                try:  
                    pom = lin[2].split(' ') 
                    lat = pom[0]
                    lon = pom[1]
                    tmp = ['gps', float(lin[1]) + timdrift, f'{lat} {lon} {pom[2]} {pom[3]} {pom[4]} {pom[5]}', 'bike/sensor/gps','string']
                except:
                    try:
                        pom = lin[2].split(' ') 
                        lat = pom[0]
                        lon = pom[1]
                        tmp = ['gps', float(lin[1]) + timdrift, f'{lat} {lon} {pom[2]} {pom[3]}', 'bike/sensor/gps','string']
            
                    except:
                        print('Err')
            elif lin[0] == 'gyro':
                print('gyro')
            elif lin[0] == 'err' or lin[0] == "":
                err += 1
                continue
            else:
                try:
                    tmp = [lin[0], float(lin[1]), lin[2], lin[3], lin[4].strip()]
                except:
                    err += 1
            outp.append(tmp)
    outp.sort(key=lambda x: x[1])
    print(f'Found {err} errors')
    if save_file:
        filename = filename[:-4]+'_sas.csv'
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(outp)
    return outp

def prepareForWeb(f, fromFile = False):
    datal = []
    if fromFile:
        f = open(f, 'r')
    for line in f:
        lin = line.split(',') if fromFile else line
        if lin[0] == 'gps':
            tmp = lin[2].split(' ')
            datal.append(['longitude',lin[1],tmp[0]])
            datal.append(['latitude',lin[1],tmp[1]])
            datal.append(['gps_speed',lin[1],tmp[2]])
            datal.append(['course',lin[1],tmp[3]])
        elif lin[0] == 'susp':
            tmp = line[2].split(' ')
            datal.append(['front_susp',lin[1],tmp[0]])
            datal.append(['rear_susp',lin[1],tmp[1]])
            datal.append(['steering_angle',lin[1],tmp[2]])
            datal.append(['p_brake',lin[1],tmp[3]])
        else:
            datal.append(lin)
    return datal

def interpolateToWide(datalist, filename = '.csv', frequency = 10.0):
    print('Interpolating')
    step = 1.0/frequency
    pars = []
    dic = dict()
    outp = dict()
    for line in datalist:
        if line[0] not in pars:
            pars.append(line[0])
    for tag in pars:
        dic[tag] = {'prevt':0, 'prevv':0, 'futt':0, 'futv':0, 'tmstp':0}
        outp[tag] = []
    cnt_lat = 0
    cnt_lon = 0
    started_list = []
    for lin in datalist:
        if lin[0] not in started_list:
            dic[lin[0]]['futv'] = float(lin[2])
        if len(started_list) >= len(pars):
            break
            

    for lin in datalist:
        dic[lin[0]]['prevt'] = dic[lin[0]]['futt']
        dic[lin[0]]['prevv'] = dic[lin[0]]['futv']
        dic[lin[0]]['futt'] = float(lin[1])
        dic[lin[0]]['futv'] = float(lin[2])
        if lin[0] != 'course':
            while dic[lin[0]]['tmstp'] < dic[lin[0]]['futt']:
                outp[lin[0]].append([dic[lin[0]]['tmstp'],
                                      dic[lin[0]]['prevv'] + (dic[lin[0]]['futv'] - dic[lin[0]]['prevv']) * (dic[lin[0]]['tmstp'] - dic[lin[0]]['prevt'])\
                                        /(dic[lin[0]]['futt'] - dic[lin[0]]['prevt'])]) #linear interpolation
                dic[lin[0]]['tmstp'] += step
        else: #linear interpolation of course (to handle 359 + 1 = 0 and 0-1 = 359 transition)
            while dic[lin[0]]['tmstp'] < dic[lin[0]]['futt']:
                if abs(dic[lin[0]]['futv'] - dic[lin[0]]['prevv']) < 100:
                    outp[lin[0]].append([dic[lin[0]]['tmstp'],\
                                          dic[lin[0]]['prevv'] + (dic[lin[0]]['futv'] - dic[lin[0]]['prevv']) * (dic[lin[0]]['tmstp'] - dic[lin[0]]['prevt'])\
                                            /(dic[lin[0]]['futt'] - dic[lin[0]]['prevt'])]) #no transition 
                else:
                    if dic[lin[0]]['prevv'] > dic[lin[0]]['futv']:
                        outp[lin[0]].append([dic[lin[0]]['tmstp'],
                                            (dic[lin[0]]['prevv'] + (360 + dic[lin[0]]['futv'] - dic[lin[0]]['prevv']) * (dic[lin[0]]['tmstp'] - dic[lin[0]]['prevt'])\
                                            / (dic[lin[0]]['futt'] - dic[lin[0]]['prevt'])) % 360]) #from 359 to 0
                    else: 
                        outp[lin[0]].append([dic[lin[0]]['tmstp'],
                                            (dic[lin[0]]['prevv'] + (dic[lin[0]]['futv'] - dic[lin[0]]['prevv'] - 360) * (dic[lin[0]]['tmstp'] - dic[lin[0]]['prevt'])\
                                            / (dic[lin[0]]['futt'] - dic[lin[0]]['prevt'])) % 360]) #from 0 to 359
                dic[lin[0]]['tmstp'] += step
    with open(f'{filename[:-4]}.wsrt', 'w') as ilef:
        stri ='timestamp,'
        for tag in pars:
            stri += f'{tag},'
        stri = stri[:-1]
        ilef.write(f'{stri}\n')
        maxi = 0
        mtag = ""
        for tag in pars:
            if len(outp[tag]) > maxi:
                maxi = len(outp[tag])
                mtag = tag
        for i in range(maxi):
            stri = str(outp[mtag][i][0]) + ','
            for tag in pars:
                stri += (str(outp[tag][i][1]) + ',') if i < len(outp[tag])  else "0,"
            stri = stri[:-1]
            ilef.write(f'{stri}\n')
    print('Successful interpolation')
    return 0

def completeParsing(filename, frequency = 10.0, save_file = False):
    timdrift = findTimeDrift(filename)
    outp = prepareForSas(filename, timdrift, save_file)
    datal = prepareForWeb(outp)
    interpolateToWide(datal, filename, frequency)

if __name__=='__main__':

    filet = sys.argv[1]
    print(completeParsing(filet, 10, True))
    """
    timdrift = findTimeDrift(filet)
    outp = prepareForSas(filet, timdrift, save_file = True)
    datal = prepareForWeb(outp)
    interpolateToWide(datal, filename=filet, frequency=200)"""
    
