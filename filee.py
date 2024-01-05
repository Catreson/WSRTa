from gpse import *
from lapsplit import Lap
from lapsplit import *
from laprefer import *
from pathlib import Path
import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import filedialog
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
import pandas as pd
from tkcalendar import Calendar
from datetime import datetime
import time
import tkintermapview as tkm
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from bs4 import BeautifulSoup
import math
import re
from geopy import distance

def previewFile(): 
  
    fig = Figure(figsize = (5, 5), 
                 dpi = 100) 

    y = [i**2 for i in range(101)] 
  
    plot1 = fig.add_subplot(111) 
  
    plot1.plot(y) 
  
    canvas = FigureCanvasTkAgg(fig, 
                               master = window)   
    canvas.draw() 

    canvas.get_tk_widget().pack(side="top",anchor=tk.NE)

    toolbar = NavigationToolbar2Tk(canvas, 
                                   window) 
    toolbar.update() 
  
    canvas.get_tk_widget().pack() 

def browseParseFiles():
    global parse_path
    parse_path = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title="Select a File",
                                          filetypes=(("CSV files",
                                                      "*.csv*"),
                                                     ("all files",
                                                      "*.*")))
    label_selected.config(text=parse_path.split("/")[-1])
    label_processing.config(text='File selected')

def browseSplitFiles():
    global split_path
    split_path = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title="Select a File",
                                          filetypes=(("WSRT files",
                                                      "*.wsrt*"),
                                                     ("all files",
                                                      "*.*")))
    label_selected_split.config(text=split_path.split("/")[-1])
    label_processing_split.config(text='File selected')

def browsePreviewFiles():
    global preview_path
    preview_path = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title="Select a File",
                                          filetypes=(("WSRT session files",
                                                      "*.wsrtses*"),
                                                     ("all files",
                                                      "*.*")))
    label_selected_preview.config(text=preview_path.split("/")[-1])
    label_processing_preview.config(text='File selected')


def parseFile(filetype):
    global parse_path
    if filetype == 'WSRT':
        alive = True
        wait_var = tk.IntVar()
        top= tk.Toplevel(window)
        top.geometry("200x80")
        top.title("Parsing parameters")
        label_freq = tk.Label(top, text = "Selected frequency: ")
        inputtxt = tk.Entry(top, 
                   width = 5) 
        inputtxt.insert(0, 10)
        checkbox_sas = tk.Checkbutton(top,
                            text="Generate SAS file?",
                            variable=fileSas,
                            onvalue=fileSas.set(True),
                            offvalue=fileSas.set(False))
        continue_button = tk.Button(top,
                                    text="Continue",
                                    command=lambda: wait_var.set(1))
        def closeWindow():
            global alive
            wait_var.set(1)
            alive = False
            top.destroy()
        cancel_button = tk.Button(top,
                                    text="Cancel",
                                    command=closeWindow)
        checkbox_sas.grid(sticky="W", column=0, row=1)
        label_freq.grid(sticky="W", column=0,row=0)
        inputtxt.grid(sticky="W", column=1, row = 0)
        continue_button.grid(sticky="W", column=0, row = 2)
        cancel_button.grid(sticky="E", column=1, row=2)
        continue_button.wait_variable(wait_var)
        if not alive:
            return
        top.update_idletasks()
        try:
            inp = float(inputtxt.get())
        except:
            label_processing.config(text="Invalid frequency",fg="red")
            return
        if not 300 > inp > 0:
            label_processing.config(text="Invalid frequency",fg="red")
            return
        if len(parse_path) > 0:
            top.destroy()
            label_processing.config(text="Processing...",fg="yellow")
            window.update_idletasks()
            try:
                completeParsing(parse_path, frequency=inp, save_file = fileSas.get())
                label_processing.config(text="Complete",bg="green")
            except Exception as erro:
                label_processing.config(text="ERROR",bg="red")
                print(f'Error: {erro}')
                raise
        else:
            label_processing.config(text="Invalid file",fg="red")
    else:
        label_processing.config(text=f"Invalid file format: {filetype}",fg="red")


def splitIntoLaps():
    global split_path
    if len(split_path) < 4:
        label_processing_split.config(text="Incorrect file",bg = "red")
        return
    alive = True
    wait_var = tk.IntVar()
    top= tk.Toplevel(window)
    top.geometry("600x250")
    label_rider = tk.Label(top, text="Input rider name: ")
    input_rider = tk.Entry(top, width=30)
    label_track = tk.Label(top, text="Input track name: ")
    input_track = tk.Entry(top, width=30)
    label_date = tk.Label(top, text="Input date: ")
    label_date_selected = tk.Label(top, text=datetime.today().strftime('%Y-%m-%d'))
    cal = Calendar(top, selectmode='day',
                   date_pattern='yyyy-mm-dd',
                   year=int(datetime.today().strftime('%Y')),
                   month=int(datetime.today().strftime('%m')),
                     day=int(datetime.today().strftime('%d')))
    def changeDate():
        label_date_selected.config(text=cal.get_date())
    button_date = tk.Button(top, text="Change date",
                            command=changeDate)
    label_id = tk.Label(top, text="Input session ID\n(to make identification easier)")
    input_id = tk.Entry(top, width=30)
    button_continue = tk.Button(top, text="Continue",
                                command=lambda : wait_var.set(1))
    def closeWindow():
            global alive
            wait_var.set(1)
            alive = False
            top.destroy()
    button_cancel = tk.Button(top, text="Cancel",
                                command=closeWindow)
    label_rider.grid(sticky="W",column=0,row=0)
    input_rider.grid(sticky="W", column=1, row=0)
    cal.grid(column=3,row=0,rowspan=5)
    label_track.grid(sticky="W",column=0,row=1)
    input_track.grid(stick="W", column=1, row=1)
    label_date.grid(sticky="W",column=0,row=2)
    label_date_selected.grid(sticky="W",column=1, row=2)
    button_date.grid(sticky="W",column=0, row=3)
    label_id.grid(sticky="W", column=0, row=4)
    input_id.grid(sticky="W",column=1, row=4)
    button_continue.grid(sticky="W", column=0, row=7)
    button_cancel.grid(sticky="E",column=1, row=7)
    button_continue.wait_variable(wait_var)

    if not alive:
        return

    session_rider = input_rider.get()
    session_track = input_track.get()
    session_date = label_date_selected.cget('text')
    session_id = input_id.get()
    top.destroy()
    
    p = Path(split_path)
    laps_path = Path.cwd() / p.stem
    if not os.path.isdir(laps_path):
        os.mkdir(laps_path)
    
    data = pd.read_csv(split_path)

    t_lat = data['latitude'][50]
    t_lon = data['longitude'][50]
    wait_var = tk.IntVar()
    top= tk.Toplevel(window)
    top.geometry("700x320")
    top.title("Splitting parameters")
    label_1 = tk.Label(top, text = "1st point (latitude, longitude): ")
    label_2 = tk.Label(top, text = "2nd point (latitude, longitude): ")

    label_1.config(text=str(t_lat))
    label_2.config(text=str(t_lon))
    input_lat_1 = tk.Entry(top, 
               width = 10) 
    input_lon_1 = tk.Entry(top, 
               width = 10) 
    input_lat_2 = tk.Entry(top, 
               width = 10) 
    input_lon_2 = tk.Entry(top, 
               width = 10) 
    input_lat_1.insert(0, 51.417095)
    input_lon_1.insert(0, 21.149420)
    input_lat_2.insert(0, 51.417186)
    input_lon_2.insert(0, 21.149489)
    label_tolerance = tk.Label(top,
                                text = "Set splitting tolerance: \n(as fraction of finish line length)")
    input_tolerance = tk.Entry(top, 
               width = 4) 
    input_tolerance.insert(0, 0.1)
    label_minimal = tk.Label(top,
                              text = "Set minimal laptime in seconds:")
    input_minimal = tk.Entry(top, 
                                width = 4) 
    input_minimal.insert(0, 25)
    continue_button = tk.Button(top,
                                text="Continue",
                                command=lambda: wait_var.set(1))
    button_cancel = tk.Button(top, text="Cancel",
                                command=closeWindow)
    click_count = 0
    def set2ndPoint(coords):
        input_lat_2.delete(0, tk.END)
        input_lon_2.delete(0, tk.END)
        input_lat_2.insert(0, coords[0])
        input_lon_2.insert(0, coords[1])
        set2ndPoint.path1 = map_widget.set_path([(float(input_lat_1.get()), float(input_lon_1.get())), (coords[0], coords[1])])
    def set1stPoint(coords):
        input_lat_1.delete(0, tk.END)
        input_lon_1.delete(0, tk.END)
        input_lat_1.insert(0, coords[0])
        input_lon_1.insert(0, coords[1])
        try:
            set2ndPoint.path1.delete()
        except:
            pass
    def leftClick(coords):
        nonlocal click_count
        if click_count == 0:
            set1stPoint(coords)
        elif click_count == 1:
            set2ndPoint(coords)
        click_count = (click_count + 1) % 2
    map_widget = tkm.TkinterMapView(top, width=400, height=300, corner_radius=0)
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    map_widget.set_position(t_lat, t_lon)
    map_widget.add_right_click_menu_command(label="Add 1st point",
                                        command=set1stPoint,
                                        pass_coords=True)
    map_widget.add_right_click_menu_command(label="Add 2nd point",
                                        command=set2ndPoint,
                                        pass_coords=True)
    map_widget.add_left_click_map_command(leftClick)
    label_1.grid(sticky="W", column=0, row=0)
    label_2.grid(sticky="W", column=0, row=1)
    input_lat_1.grid(sticky="W", column=1, row = 0)
    input_lon_1.grid(sticky="W", column=2, row = 0)
    input_lat_2.grid(sticky="W", column=1, row = 1)
    input_lon_2.grid(sticky="W", column=2, row = 1)
    label_tolerance.grid(sticky="W", column=0, row=2)
    input_tolerance.grid(sticky="W", column=1, row=2)
    label_minimal.grid(sticky="W", column=0, row=3)
    input_minimal.grid(sticky="W", column=1, row=3)
    continue_button.grid(sticky="W", column=0, row = 4)
    button_cancel.grid(sticky="E",column=1,row=4)
    map_widget.grid(sticky="NE", column=3,row=0, rowspan=5)
    continue_button.wait_variable(wait_var)
    top.update_idletasks() 

    start_line = [(float(input_lon_1.get()), float(input_lat_1.get())), (float(input_lon_2.get()), float(input_lat_2.get()))]
    minimal_laptime = float(input_minimal.get())
    finish_line_tolerance = float(input_tolerance.get())

    top.destroy()
    label_processing_split.config(text="Processing...",fg="yellow")
    window.update_idletasks()

    laps = find_laps(data, start_line, minimal_laptime, finish_line_tolerance)

    with open(laps_path / f'{p.stem}.wsrtses', 'wb') as file:
            rut = ET.Element('session')
            details = ET.SubElement(rut, 'details')
            laplist = []
            laptimes = ET.SubElement(rut, 'laptimes')
            rider_name = ET.SubElement(details, 'rider_name')
            rider_name.text = session_rider
            track_name = ET.SubElement(details, 'track_name')
            track_name.text = session_track
            ride_date = ET.SubElement(details, 'date')
            ride_date.text = session_date
            ride_id = ET.SubElement(details, 'identifier')
            ride_id.text = session_id

            no_laps = ET.SubElement(laptimes, 'no_laps')
            no_laps.text = str(len(laps))
            for i, lap in enumerate(laps, 1):
                tmp = ET.SubElement(laptimes, f'lap')
                tmp.set('number', f'l{i}')
                tmp.text = str(lap[1] - lap[0])
                laplist.append(tmp)
            tmp = minidom.parseString(ET.tostring(rut)).toprettyxml(indent="   ")
            file.write(tmp.encode('utf-8'))

    laps_data = split_laps(data, laps)
    for i, lap in enumerate(laps_data):
        lap.to_csv(f'{laps_path}/l{i+1}.lap', index=False)
    label_processing_split.config(text="Complete",bg="green")


def previewLaps():
    global preview_path
    global reference_lap_index
    global selected_laps_list

    if not os.path.exists(preview_path):
        return
    dir_path = Path(preview_path).parent
    with open(preview_path, 'r') as file:
        times_data = file.read()
    bs_times_data = BeautifulSoup(times_data, 'xml')
    bs_laptimes = bs_times_data.find_all('lap')
    lap_list = [[x.get('number'), '{:.3f}'.format(float(x.get_text()))] for x in bs_laptimes]
    lap_paths = list(dir_path.glob('*.lap'))
    lap_paths.sort(key = lambda x: int(str(x.stem)[1:]))
    lap_dic = {}
    for lap in lap_paths:
        lap_dic[lap.stem] = lap

    selected_laps_names = []
    selected_laps_df = []
    reference_lap_index = 0
    selected_laps_list = []

    def loadLaps():
        nonlocal selected_laps_names
        global selected_laps_list
        colors = ['green', 'red', 'blue', 'orange', 'black', 'yellow', 'pink']
        selected_laps_names = []
        for i, lap in enumerate(laps_selected.curselection()):
            tmp = Lap(lap_ID = laps_selected.get(lap)[0], lap_path = lap_dic[laps_selected.get(lap)[0]], lap_color = colors[i%len(colors)])
            selected_laps_names.append([laps_selected.get(lap)[0], colors[i%len(colors)]])
            tmp.reload_df()
            selected_laps_list.append(tmp)
        reference_list_select.set(selected_laps_names)

    def referLaps():
        global reference_lap_index
        global selected_laps_list
        reference_lap_index = reference_selected.curselection()[0]
        reference_lap_ID = reference_selected.get(reference_lap_index)[0]
        print(reference_lap_ID)
        referLapsToLap(selected_laps_list, reference_lap_ID)
        calculateTrackDistance(selected_laps_list[reference_lap_index].df)
        calculateAcceleration(selected_laps_list[reference_lap_index].df)
        calculateAcceleration2(selected_laps_list[reference_lap_index].df)

    def showMapLaps():
        global selected_laps_list
        global reference_lap_index
        map_widget.pack()
        map_widget.set_position(selected_laps_list[reference_lap_index].df['latitude'][5], selected_laps_list[reference_lap_index].df['longitude'][5])
        for i, lap in enumerate(selected_laps_list):
            map_widget.set_path(list(zip(lap.df['latitude'], lap.df['longitude'])),
                                color=lap.color,
                                width=2)
        
    previewWindow = tk.Toplevel(window)
    previewWindow.title("Laps preview")
    previewWindow.geometry('1000x800')

    lap_list_select = tk.Variable(value=lap_list)
    laps_selected = tk.Listbox(previewWindow,
                             height=5,
                             listvariable=lap_list_select,
                             selectmode=tk.MULTIPLE)
    reference_list_select = tk.Variable()
    reference_selected = tk.Listbox(previewWindow,
                             height=5,
                             listvariable=reference_list_select,
                             selectmode=tk.SINGLE)
    

    button_laps_select = tk.Button(previewWindow,
                                   text="Load selected",
                                   command=loadLaps)
    button_reference_select = tk.Button(previewWindow,
                                   text="Change dziedzina",
                                   command=referLaps)
    button_showmap_select = tk.Button(previewWindow,
                                   text="Show map",
                                   command=showMapLaps)
    button_show_plot = tk.Button(previewWindow,
                                   text="Show plot",
                                   command=showChart)
    map_frame = tk.Frame(previewWindow,
                         width=1000,
                         height=600)
    map_widget = tkm.TkinterMapView(map_frame, width=1000, height=600, corner_radius=0)
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    
    
    laps_selected.grid(column=0,row=0)
    reference_selected.grid(column=1, row=0)
    button_showmap_select.grid(column=2,row=0)
    button_laps_select.grid(column=0,row=1)
    button_reference_select.grid(column=1,row=1)
    button_show_plot.grid(column=3,row=0)
    map_frame.grid(column=0,row=8,columnspan=10)

def showChart():
    global reference_lap_index
    global selected_laps_list

    butt_row = tk.IntVar()

    chartWindow = tk.Toplevel(window)
    chartWindow.title('Statystyki')

    wid = window.winfo_screenmmwidth()
    hei = window.winfo_screenheight()
    depei = chartWindow.winfo_fpixels('1i')
    map_frame = tk.Frame(chartWindow,
                         width=600,
                         height=400)
    widecharts_frame = tk.Frame(chartWindow,
                                width=900,
                                height=800)
    vw = tk.Scrollbar(widecharts_frame, orient='vertical')
    vw.pack(side = tk.RIGHT, fill = tk.Y)
    boxcharts_frame = tk.Frame(chartWindow,
                               width=300,
                               height=400)
    map_frame.grid(column=1,row=0)
    widecharts_frame.grid(column=0,row=0,rowspan=2)
    boxcharts_frame.grid(column=1,row=1)

    map_widget = tkm.TkinterMapView(map_frame, width=600, height=400, corner_radius=0)
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
    map_widget.set_position(selected_laps_list[reference_lap_index].df['latitude'][5],selected_laps_list[reference_lap_index].df['longitude'][5])
    map_widget.pack()

    tag_list = ['gps_speed']
    plot_list = []
    x_lims = ()
    xer = 0

    def showMapPoint(distancer):
        global selected_laps_list
        global reference_lap_index
        straight_lenght = 0.0002
        lap = selected_laps_list[reference_lap_index]
        ind = 0
        coords = []
        for i, row in lap.df.iterrows():
            if row['distance'] > distancer:
                ind = i
                break
        deformation = distance.distance((lap.df['latitude'][ind], lap.df['longitude'][ind]), (lap.df['latitude'][ind] + 0.0002, lap.df['longitude'][ind])).m\
                                        / distance.distance((lap.df['latitude'][ind], lap.df['longitude'][ind]), (lap.df['latitude'][ind], lap.df['longitude'][ind] + 0.0002)).m
        rad_argument = ((2 * math.pi - math.radians(lap.df['course'][ind])) + math.pi/2) % (2 * math.pi)
        argument = -1.0 / math.tan(rad_argument)
        argument = argument / deformation
        print(deformation)
        b =  lap.df['latitude'][ind] - lap.df['longitude'][ind] * argument
        additional_distance = (straight_lenght / 2) / math.sqrt(1 + argument**2)
        tmp = lap.df['longitude'][ind] + additional_distance
        coords.append((argument * tmp + b, tmp))
        tmp = lap.df['longitude'][ind] - additional_distance
        coords.append((argument * tmp + b, tmp))
        print(coords)
        map_widget.set_path(coords,
                             color=lap.color,
                             width=2)        

    def showMapLaps(x_lims):
        global selected_laps_list
        global reference_lap_index
        x_min = x_lims[0] if x_lims[0] > 0 else 0
        x_max = x_lims[1]
        i_min = 0
        i_max = len(selected_laps_list[reference_lap_index].df['longitude']) - 1
        min_set = False
        for i, row in selected_laps_list[reference_lap_index].df.iterrows():    
            if  not min_set and row['distance'] > x_min:
                i_min = i
                min_set = True
            if row['distance'] > x_max:
                i_max = i
                break
        print(f'i_max {i_max}, i_min { i_min}')
        map_widget.set_position(selected_laps_list[reference_lap_index].df['latitude'][5], selected_laps_list[reference_lap_index].df['longitude'][5])
        map_widget.set_path(list(zip(selected_laps_list[reference_lap_index].df['latitude'][i_min:i_max], selected_laps_list[reference_lap_index].df['longitude'][i_min:i_max])),
                             color=selected_laps_list[reference_lap_index].color,
                             width=2)
        for i, lap in enumerate(selected_laps_list):
            if i != reference_lap_index:
                ises = selected_laps_list[reference_lap_index].df[lap.ID][i_min:i_max]
                coords = [(lap.df['latitude'][x], lap.df['longitude'][x]) for x in ises]
                map_widget.set_path(coords,
                                    color=lap.color,
                                    width=2)

    def reloadCharts():
        nonlocal canvas
        nonlocal canvas_wg
        nonlocal toolbar
        nonlocal add_butt
        nonlocal remove_butt
        nonlocal add_list

        canvas_wg.pack_forget()
        add_list.pack_forget()
        add_butt.pack_forget()
        remove_butt.pack_forget()
        toolbar.pack_forget()

        
        add_list.pack(side=tk.TOP)
        add_butt.pack(side=tk.TOP)
        remove_butt.pack(side=tk.TOP)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        canvas_wg.pack(anchor=tk.S)

    def addChart(tag):
        nonlocal tag_list
        if tag not in tag_list:
            tag_list.append(tag)
            addRemoveChart('+')

    def removeChart(tag):
        nonlocal tag_list
        if tag in tag_list:
            tag_list.remove(tag)
            addRemoveChart('-')

    def on_xlims_change(event_ax):
        nonlocal x_lims
        nonlocal xer
        x_lims = event_ax.get_xlim()
        print(x_lims)
        map_widget.delete_all_path()
        showMapPoint(xer)
        showMapLaps(x_lims)

    def on_click(event):
        nonlocal x_lims
        nonlocal xer
        xer = event.xdata
        if event.button == 3:
            map_widget.delete_all_path()
            showMapPoint(xer)
            showMapLaps(x_lims)

    def addRemoveChart(sign):
        nonlocal fig
        nonlocal canvas
        nonlocal canvas_wg
        nonlocal toolbar
        nonlocal tag_list
        nonlocal plot_list
        tmp = fig.get_size_inches()
        canvas_wg.destroy()
        toolbar.destroy()
        additional_height = 250/depei if sign == '+' else -250/depei if sign =='-' else 0

        fig = Figure(figsize = (tmp[0], tmp[1] + additional_height), 
                 dpi = 100) 
        no_plots = len(tag_list) + 1
        plot_list = []
        for i, tagg in enumerate(tag_list):
            if i == 0:
                plot_list.append(fig.add_subplot(no_plots, 1, i + 1))
            else:
                plot_list.append(fig.add_subplot(no_plots, 1, i + 1, sharex=plot_list[0]))
            plot_list[i].plot(selected_laps_list[reference_lap_index].df['distance'], selected_laps_list[reference_lap_index].df[tagg], color = selected_laps_list[reference_lap_index].color)
            for j, lap in enumerate(selected_laps_list):
                if j != reference_lap_index:
                    xses = selected_laps_list[reference_lap_index].df['distance']
                    yreks = [lap.df[tagg][x] for x in selected_laps_list[reference_lap_index].df[lap.ID]]
                    plot_list[i].plot(xses, yreks, color = lap.color)
            plot_list[i].grid(visible=True)
            plot_list[i].set_ylabel(tagg)
            if i == 0:
                plot_list[i].callbacks.connect('xlim_changed', on_xlims_change)
            cid = fig.canvas.mpl_connect('button_press_event', on_click)
        canvas = FigureCanvasTkAgg(fig, 
                           master = widecharts_frame)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, 
                                   widecharts_frame) 
        toolbar.update()  
        canvas_wg = canvas.get_tk_widget()
        canvas_wg.config(yscrollcommand=vw.set)
        canvas_wg.configure(scrollregion=canvas_wg.bbox("all"))
        reloadCharts()

    fig = Figure(figsize = (900/depei, 250/depei), 
                 dpi = 100) 
    plot_list.append(fig.add_subplot(111))
    plot_list[0].plot(selected_laps_list[reference_lap_index].df['distance'], selected_laps_list[reference_lap_index].df['gps_speed'], color = selected_laps_list[reference_lap_index].color)
    canvas = FigureCanvasTkAgg(fig, 
                               master = widecharts_frame)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, 
                                   widecharts_frame) 
    toolbar.update() 
    canvas_wg = canvas.get_tk_widget()
    canvas_wg.config(yscrollcommand=vw.set)
    selected_add = tk.StringVar()
    add_butt = tk.Button(widecharts_frame,
                         text='Add chart',
                         command=lambda: addChart(selected_add.get()))
    remove_butt = tk.Button(widecharts_frame,
                         text='Remove  chart',
                         command=lambda: removeChart(selected_add.get()))
    options = [x for x in selected_laps_list[reference_lap_index].df.columns]
    selected_add.set(options[1])
    add_list = tk.OptionMenu(widecharts_frame,
                             selected_add,
                             *options)
    vw.config(command=canvas_wg.yview)
    canvas_wg.configure(scrollregion=canvas_wg.bbox("all"))
    reloadCharts()
#----------------------------------
#Root window
window = ThemedTk(theme="clam")
window.title('File basic analysis and parsing')
window.geometry("800x600")
window.config(background="white")
plt.style.use('dark_background')
#----------------------------------
#variables
parse_path = ""
split_path = ""
preview_path = ""
fileSas = tk.BooleanVar()
fileTypes = [
    "WSRT",
    "HWDP"
]
selectedType = tk.StringVar()
selectedType.set("WSRT")
#----------------------------------
#Parse file
lfParse = tk.LabelFrame(window, text='Parse file')

label_selected = tk.Label(lfParse,
                           text = "None")
label_select = tk.Label(lfParse,
                         text = "Selected file: ")
button_explore = tk.Button(lfParse,
                        text="Browse File",
                        command=browseParseFiles)
label_type = tk.Label(lfParse,
                      text="Input file format",)
typeSelector = tk.OptionMenu(lfParse,
                            selectedType,
                            *fileTypes)
button_parse = tk.Button(lfParse,
                        text="Parse",
                        command=lambda: parseFile(selectedType.get()))
label_processing = tk.Label(lfParse,
                         text="File not selected")


label_type.grid(sticky="W",column=0,row=0)
typeSelector.grid(sticky="E",column=1, row=0)
button_explore.grid(sticky="W", column=0, row=1)
label_selected.grid(sticky="W", column=1, row=2)
label_select.grid(sticky="W", column=0, row=2)
button_parse.grid(sticky="W", column=0,row=3)
label_processing.grid(sticky="W",column=1,row=3)
#----------------------------------
#Split laps
lfSplit = tk.LabelFrame(window, text="Split laps")

button_explore_split = tk.Button(lfSplit,
                        text="Browse File",
                        command=browseSplitFiles)
label_selected_split = tk.Label(lfSplit,
                           text = "None")
label_select_split = tk.Label(lfSplit,
                         text = "Selected file: ")
label_processing_split = tk.Label(lfSplit,
                         text="File not selected")
button_split = tk.Button(lfSplit,
                     text="Preview",
                     command=splitIntoLaps)


button_explore_split.grid(sticky="W", column=0, row=0)
label_selected_split.grid(sticky="W", column=1, row=1)
label_select_split.grid(sticky="W", column=0, row=1)
label_processing_split.grid(sticky="W",column=1,row=2)
button_split.grid(sticky="W", column=0,row=2)

#----------------------------------
#Preview laps
lfView = tk.LabelFrame(window,text="View laps")

button_explore_preview = tk.Button(lfView,
                        text="Browse File",
                        command=browsePreviewFiles)
label_selected_preview= tk.Label(lfView,
                           text = "None")
label_select_preview = tk.Label(lfView,
                         text = "Selected file: ")
label_processing_preview = tk.Label(lfView,
                         text="File not selected")
button_preview = tk.Button(lfView,
                     text="Preview",
                     command=previewLaps)


button_explore_preview.grid(sticky="W", column=0, row=0)
label_selected_preview.grid(sticky="W", column=1, row=1)
label_select_preview.grid(sticky="W", column=0, row=1)
label_processing_preview.grid(sticky="W",column=1,row=2)
button_preview.grid(sticky="W", column=0,row=2)
#----------------------------------
#Controls
lfControl = tk.LabelFrame(window, text="Controls")


button_exit = tk.Button(lfControl,
                     text="Exit",
                     command=exit)


button_exit.grid(sticky="W", column=0, row=2)

#----------------------------------









lfParse.pack(side="left",anchor=tk.SW)
lfSplit.pack(side="left",anchor=tk.SW)
lfView.pack(side="left",anchor=tk.SW)
lfControl.pack(side="left",anchor=tk.SW)




window.mainloop()