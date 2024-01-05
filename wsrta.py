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


class LFGener(tk.LabelFrame):
    def __init__(self, master, filetype, filedescription, titel, *args, **kwargs):
        tk.LabelFrame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.path = ''
        self.filename = ''
        self.filetype = filetype
        self.filedescription = filedescription
        self.config(text = titel)
        self.button_explore = tk.Button(self,
                        text="Browse File",
                        command=lambda: self.set_path_n_name(self.browseFiles()))
        self.label_selected = tk.Label(self,
                           text = "None")
        self.label_select = tk.Label(self,
                         text = "Selected file: ")
        self.label_processing = tk.Label(self,
                         text="File not selected")
        self.button = tk.Button(self,
                     text="Preview",
                     command=self.buttonAction)
        
        self.button_explore.grid(sticky="W", column=0, row=1)
        self.label_selected.grid(sticky="W", column=1, row=2)
        self.label_select.grid(sticky="W", column=0, row=2)
        self.button.grid(sticky="W", column=0,row=3)
        self.label_processing.grid(sticky="W",column=1,row=3)
    
    def buttonAction(self):
            pass
    
    def set_path_n_name(self, args):
        self.path = args[0]
        self.filename = args[1]
        self.label_selected.config(text = self.filename)
        self.label_processing.config(text='File selected')

    def browseFiles(self):
        path = filedialog.askopenfilename(initialdir=os.getcwd(),
                                          title="Select a File",
                                          filetypes=((self.filedescription,
                                                      f"*{self.filetype}"),
                                                     ("all files",
                                                      "*.*")))
        selected = path.split("/")[-1]
        return (path, selected)
class LFParse(LFGener):
    def __init__(self, master, *args, **kwargs):
        LFGener.__init__(self, master, filetype = '.csv', filedescription = 'CSV Files', titel = 'Parse', *args, **kwargs)
        self.fileTypes = [
            "WSRT",
            "TEST"
            ]
        self.selectedType = tk.StringVar()
        self.selectedType.set("WSRT")
        self.label_type = tk.Label(self,
                      text="Input file format",)
        self.typeSelector = tk.OptionMenu(self,
                            self.selectedType,
                            *self.fileTypes)
        self.label_type.grid(sticky="W",column=0,row=0)
        self.typeSelector.grid(sticky="E",column=1, row=0)

    def buttonAction(self):
        if self.selectedType.get() == 'WSRT':
            ParseWindowWSRT(self, self.path)
class LFSplit(LFGener):
    def __init__(self, master, *args, **kwargs):
        LFGener.__init__(self, master, filetype = '.wsrt', filedescription = 'WSRT Files', titel = 'Split', *args, **kwargs)
    
    def buttonAction(self):
        SplitWindow(self, self.path)   
class LFView(LFGener):
    def __init__(self, master, *args, **kwargs):
        LFGener.__init__(self, master, filetype = '.wsrtses', filedescription = 'WSRT Session Files', titel = 'Preview', *args, **kwargs)
    
    def buttonAction(self):
        return
class LFControl(tk.LabelFrame):
    def __init__(self, master, *args, **kwargs):
        tk.LabelFrame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.button_exit = tk.Button(self,
                     text="Exit",
                     command=exit)
        
        self.button_exit.pack()
class SmallControls(tk.Frame):
    def __init__(self, master, buttonContinue = lambda: 0, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.continue_buton = tk.Button(self,
                     text="Continue",
                     command=buttonContinue)
        self.cancel_buton = tk.Button(self,
                     text="Cancel",
                     command=self.buttonCancel)
        
        self.continue_buton.pack(side = 'left', expand=True)
        self.cancel_buton.pack(side = 'left', expand=True)

    def buttonCancel(self):
        self.master.destroy()
        self.master.update()
class ParseWindowWSRT(tk.Toplevel):
    def __init__(self, master, path, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
        self.master = master
        self.path = path
        self.title("Parse parameters")
        self.geometry("200x100")
        self.fileSas = tk.BooleanVar()
        self.label_freq = tk.Label(self, text = "Selected frequency (0-300]: ")
        self.inputtxt = tk.Entry(self, 
                   width = 5) 
        self.inputtxt.insert(0, 10)
        self.label_state = tk.Label(self, text = "")
        self.checkbox_sas = tk.Checkbutton(self,
                            text="Generate SAS file?",
                            variable=self.fileSas,
                            onvalue=self.fileSas.set(True),
                            offvalue=self.fileSas.set(False))
        self.checkbox_sas.grid(sticky="W", column=0, row=1)
        self.label_freq.grid(sticky="W", column=0,row=0)
        self.inputtxt.grid(sticky="W", column=1, row = 0)
        self.label_state.grid(sticky="W", column=0, row = 2)
        SmallControls(self, self.buttonContinue).grid(column=0, row=3, columnspan=2)

    def buttonContinue(self):
        self.inputtxt.config(bg='white')
        try:
            inp = float(self.inputtxt.get())
        except:
            self.inputtxt.config(bg='red')
            self.label_state.config(text="Invalid frequency",fg="red")
            return
        if not 300 >= inp > 0:
            self.inputtxt.config(bg='red')
            self.label_state.config(text="Invalid frequency",fg="red")
            return
        if len(self.path) > 0:
            self.label_state.config(text="Processing...",fg="yellow")
            self.update_idletasks()
            try:
                completeParsing(self.path, frequency=inp, save_file = self.fileSas.get())
                self.label_state.config(text="Complete",bg="green")
                self.update_idletasks()
                time.sleep(3)
                try:
                    self.master.label_processing.config(text="Complete",bg="green")
                except:
                    print('No use like this')
                self.update_idletasks()
                time.sleep(3)
                self.destroy()
            except Exception as erro:
                self.label_state.config(text="ERROR",bg="red")
                print(f'Error: {erro}')
                raise
        else:
            self.label_state.config(text="Invalid file",fg="red")
class RiderInfo(tk.Frame):
    def __init__(self, master, path, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.path = path
        self.config(height=600,
                    width=250)
        
        self.label_rider = tk.Label(self, text="Input rider name: ")
        self.input_rider = tk.Entry(self, width=30)
        self.label_track = tk.Label(self, text="Input track name: ")
        self.input_track = tk.Entry(self, width=30)
        self.label_date = tk.Label(self, text="Input date: ")
        self.date_val = tk.StringVar()
        self.cal = Calendar(self, selectmode='day',
                   date_pattern='yyyy-mm-dd',
                   year=int(datetime.today().strftime('%Y')),
                   month=int(datetime.today().strftime('%m')),
                     day=int(datetime.today().strftime('%d')),
                     textvariableStringVar=self.date_val)
        self.label_id = tk.Label(self, text="Input session ID\n(to make identification easier)")
        self.input_id = tk.Entry(self, width=30)

        self.label_rider.grid(sticky="W",column=0,row=0)
        self.input_rider.grid(sticky="W", column=1, row=0)
        self.label_track.grid(sticky="W",column=0,row=1)
        self.input_track.grid(stick="W", column=1, row=1)
        self.label_date.grid(sticky="W",column=0,row=2)
        self.cal.grid(column=1,row=2, rowspan = 2)
        self.label_id.grid(sticky="W", column=0, row=4)
        self.input_id.grid(sticky="W",column=1, row=4)
    
    def buttonContinue(self):
        self.master.session_metadata['session_rider'] = self.input_rider.get()
        self.master.session_metadata['session_track'] = self.input_track.get()
        self.master.session_metadata['session_date'] = str(self.cal.selection_get())
        self.master.session_metadata['session_id'] = self.input_id.get()
        self.master.geometry('700x320')
        print(self.master.session_metadata)
class FnishlineInfo(tk.Frame):
    def __init__(self, master, path, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.path = path
        self.click_count = 0
        self.config(height=600,
                    width=250)
        self.data = pd.read_csv(self.path)

        self.t_lat = self.data['latitude'][50]
        self.t_lon = self.data['longitude'][50]

        self.label_1 = tk.Label(self, text = "1st point (latitude, longitude): ")
        self.label_2 = tk.Label(self, text = "2nd point (latitude, longitude): ")
        self.label_1.config(text=str(self.t_lat))
        self.label_2.config(text=str(self.t_lon))
        self.input_lat_1 = tk.Entry(self, 
               width = 10) 
        self.input_lon_1 = tk.Entry(self, 
               width = 10) 
        self.input_lat_2 = tk.Entry(self, 
               width = 10) 
        self.input_lon_2 = tk.Entry(self, 
               width = 10) 
        self.input_lat_1.insert(0, 51.417095)
        self.input_lon_1.insert(0, 21.149420)
        self.input_lat_2.insert(0, 51.417186)
        self.input_lon_2.insert(0, 21.149489)
        self.label_tolerance = tk.Label(self,
                                text = "Set splitting tolerance: \n(as fraction of finish line length)")
        self.input_tolerance = tk.Entry(self, 
               width = 4) 
        self.input_tolerance.insert(0, 0.1)
        self.label_minimal = tk.Label(self,
                              text = "Set minimal laptime in seconds:")
        self.input_minimal = tk.Entry(self, 
                                width = 4) 
        self.input_minimal.insert(0, 25)
        self.map_widget = tkm.TkinterMapView(self, width=400, height=300, corner_radius=0)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(self.t_lat, self.t_lon)
        self.map_widget.add_right_click_menu_command(label="Add 1st point",
                                            command=self.set1stPoint,
                                            pass_coords=True)
        self.map_widget.add_right_click_menu_command(label="Add 2nd point",
                                            command=self.set2ndPoint,
                                            pass_coords=True)
        self.map_widget.add_left_click_map_command(self.leftClick)

        self.label_1.grid(sticky="W", column=0, row=0)
        self.label_2.grid(sticky="W", column=0, row=1)
        self.input_lat_1.grid(sticky="W", column=1, row = 0)
        self.input_lon_1.grid(sticky="W", column=2, row = 0)
        self.input_lat_2.grid(sticky="W", column=1, row = 1)
        self.input_lon_2.grid(sticky="W", column=2, row = 1)
        self.label_tolerance.grid(sticky="W", column=0, row=2)
        self.input_tolerance.grid(sticky="W", column=1, row=2)
        self.label_minimal.grid(sticky="W", column=0, row=3)
        self.input_minimal.grid(sticky="W", column=1, row=3)
        self.map_widget.grid(sticky="NE", column=3,row=0, rowspan=5)

    def set2ndPoint(self, coords):
        self.input_lat_2.delete(0, tk.END)
        self.input_lon_2.delete(0, tk.END)
        self.input_lat_2.insert(0, coords[0])
        self.input_lon_2.insert(0, coords[1])
        self.path1 = self.map_widget.set_path([(float(self.input_lat_1.get()), float(self.input_lon_1.get())), (coords[0], coords[1])])
    def set1stPoint(self, coords):
        self.input_lat_1.delete(0, tk.END)
        self.input_lon_1.delete(0, tk.END)
        self.input_lat_1.insert(0, coords[0])
        self.input_lon_1.insert(0, coords[1])
        try:
            self.path1.delete()
        except:
            pass
    def leftClick(self, coords):
        self.click_count
        if self.click_count == 0:
            self.set1stPoint(coords)
        elif self.click_count == 1:
            self.set2ndPoint(coords)
        self.click_count = (self.click_count + 1) % 2

    def createSessionFile(self, laps):
        p = Path(self.path)
        laps_path = Path.cwd() / p.stem
        if not os.path.isdir(laps_path):
            os.mkdir(laps_path)
        with open(laps_path / f'{p.stem}.wsrtses', 'wb') as file:
            rut = ET.Element('session')
            details = ET.SubElement(rut, 'details')
            laplist = []
            laptimes = ET.SubElement(rut, 'laptimes')
            rider_name = ET.SubElement(details, 'rider_name')
            rider_name.text = self.master.session_metadata['session_rider']
            track_name = ET.SubElement(details, 'track_name')
            track_name.text = self.master.session_metadata['session_track']
            ride_date = ET.SubElement(details, 'date')
            ride_date.text = self.master.session_metadata['session_date']
            ride_id = ET.SubElement(details, 'identifier')
            ride_id.text = self.master.session_metadata['session_id']

            no_laps = ET.SubElement(laptimes, 'no_laps')
            no_laps.text = str(len(laps))
            for i, lap in enumerate(laps, 1):
                tmp = ET.SubElement(laptimes, f'lap')
                tmp.set('number', f'l{i}')
                tmp.text = str(lap[1] - lap[0])
                laplist.append(tmp)
            tmp = minidom.parseString(ET.tostring(rut)).toprettyxml(indent="   ")
            file.write(tmp.encode('utf-8'))
        return laps_path

    def buttonContinue(self):
        start_line = [(float(self.input_lon_1.get()), float(self.input_lat_1.get())), (float(self.input_lon_2.get()), float(self.input_lat_2.get()))]
        minimal_laptime = float(self.input_minimal.get())
        finish_line_tolerance = float(self.input_tolerance.get())
        self.master.master.label_processing.config(text="Processing...",fg="yellow")
        laps = find_laps(self.data, start_line, minimal_laptime, finish_line_tolerance)
        laps_path = self.createSessionFile(laps)
        laps_data = split_laps(self.data, laps)
        for i, lap in enumerate(laps_data):
            lap.to_csv(f'{laps_path}/l{i+1}.lap', index=False)
        self.master.master.label_processing.config(text="Complete",bg="green")
class SplitWindow(tk.Toplevel):
    def __init__(self, master, path, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
        self.master = master
        self.path = path
        self.session_metadata = {}
        self.frames = []
        self.frames.append(RiderInfo(self, self.path))
        self.frames.append(FnishlineInfo(self, self.path))

        self.frames[0].pack()
        self.cp = SmallControls(self, buttonContinue=self.buttonContinue)
        self.cp.pack()

    def buttonContinue(self):
        if len(self.frames):
            self.cp.pack_forget()
            self.frames[0].buttonContinue()
            self.frames[0].destroy()
            del self.frames[0]
        if len(self.frames):
            self.frames[0].pack()
            self.cp.pack()
        else:
            self.destroy()

class ViewWindow(tk.Toplevel):
    pass

class MainWindow():
    def __init__(self, master, *args, **kwargs):
        self.frame = tk.Frame(master)
        self.master = master
        self.lfParse = LFParse(self.frame)
        self.lfSplit = LFSplit(self.frame)
        self.lfView = LFView(self.frame)
        self.lfControl = LFControl(self.frame)
        self.pack_self()

    def pack_self(self):
        self.lfParse.pack(side="left",anchor=tk.SW)
        self.lfSplit.pack(side="left",anchor=tk.SW)
        self.lfView.pack(side="left",anchor=tk.SW)
        self.lfControl.pack(side="left",anchor=tk.SW)

if __name__ == '__main__':
    rut = ThemedTk(theme="clam")
    rut.title('File basic analysis and parsing')
    rut.config(background="white")
    rut.geometry('600x200')
    MainWindow(rut).frame.pack()
    plt.style.use('dark_background')
    #main lup
    rut.mainloop()