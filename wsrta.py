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
        SplitWindowRider(self, self.path)   
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

class SplitWindowRider(tk.Toplevel):
    def __init__(self, master, path, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
        self.path = path
        self.session_metadata = {}
        self.click_count = 0
        self.frame = tk.Frame(self,
                              height = 600,
                              width=250)
        self.frame.pack()
        self.geometry('600x250')
        self.label_rider = tk.Label(self.frame, text="Input rider name: ")
        self.input_rider = tk.Entry(self.frame, width=30)
        self.label_track = tk.Label(self.frame, text="Input track name: ")
        self.input_track = tk.Entry(self.frame, width=30)
        self.label_date = tk.Label(self.frame, text="Input date: ")
        self.label_date_selected = tk.Label(self.frame, text=datetime.today().strftime('%Y-%m-%d'))
        self.date_val = tk.StringVar()
        self.cal = Calendar(self.frame, selectmode='day',
                   date_pattern='yyyy-mm-dd',
                   year=int(datetime.today().strftime('%Y')),
                   month=int(datetime.today().strftime('%m')),
                     day=int(datetime.today().strftime('%d')),
                     textvariableStringVar=self.date_val)
        self.label_id = tk.Label(self.frame, text="Input session ID\n(to make identification easier)")
        self.input_id = tk.Entry(self.frame, width=30)

        self.label_rider.grid(sticky="W",column=0,row=0)
        self.input_rider.grid(sticky="W", column=1, row=0)
        self.cal.grid(column=3,row=0,rowspan=5)
        self.label_track.grid(sticky="W",column=0,row=1)
        self.input_track.grid(stick="W", column=1, row=1)
        self.label_date.grid(sticky="W",column=0,row=2)
        self.label_date_selected.grid(sticky="W",column=1, row=2)
        self.label_id.grid(sticky="W", column=0, row=4)
        self.input_id.grid(sticky="W",column=1, row=4)
        self.cp = SmallControls(self, buttonContinue= self.getLine)
        self.cp.pack(anchor=tk.S)
    
    def getLine(self):
        self.session_metadata['session_rider'] = self.input_rider.get()
        self.session_metadata['session_track'] = self.input_track.get()
        self.session_metadata['session_date'] = self.label_date_selected.cget('text')
        self.session_metadata['session_id'] = self.input_id.get()
        self.frame.destroy()
        self.cp.destroy()
        self.geometry('700x320')
        self.frame = tk.Frame(self,
                              height = 700,
                              width=320)
        self.frame.pack()
        self.cp = SmallControls(self,
                                 buttonContinue= self.splitLaps)
        self.cp.pack(anchor=tk.S)

    def splitLaps(self):
        data = pd.read_csv(self.path)
        t_lat = data['latitude'][50]
        t_lon = data['longitude'][50]

        label_1 = tk.Label(self.frame, text = "1st point (latitude, longitude): ")
        label_2 = tk.Label(self.frame, text = "2nd point (latitude, longitude): ")
        label_1.config(text=str(t_lat))
        label_2.config(text=str(t_lon))
        input_lat_1 = tk.Entry(self.frame, 
               width = 10) 
        input_lon_1 = tk.Entry(self.frame, 
               width = 10) 
        input_lat_2 = tk.Entry(self.frame, 
               width = 10) 
        input_lon_2 = tk.Entry(self.frame, 
               width = 10) 
        input_lat_1.insert(0, 51.417095)
        input_lon_1.insert(0, 21.149420)
        input_lat_2.insert(0, 51.417186)
        input_lon_2.insert(0, 21.149489)
        label_tolerance = tk.Label(self.frame,
                                text = "Set splitting tolerance: \n(as fraction of finish line length)")
        input_tolerance = tk.Entry(self.frame, 
               width = 4) 
        input_tolerance.insert(0, 0.1)
        label_minimal = tk.Label(self.frame,
                              text = "Set minimal laptime in seconds:")
        input_minimal = tk.Entry(self.frame, 
                                width = 4) 
        input_minimal.insert(0, 25)

    def set2ndPoint(self, coords):
        input_lat_2.delete(0, tk.END)
        input_lon_2.delete(0, tk.END)
        input_lat_2.insert(0, coords[0])
        input_lon_2.insert(0, coords[1])
        set2ndPoint.path1 = map_widget.set_path([(float(input_lat_1.get()), float(input_lon_1.get())), (coords[0], coords[1])])
    def set1stPoint(self, coords):
        input_lat_1.delete(0, tk.END)
        input_lon_1.delete(0, tk.END)
        input_lat_1.insert(0, coords[0])
        input_lon_1.insert(0, coords[1])
        try:
            set2ndPoint.path1.delete()
        except:
            pass
    def leftClick(self, coords):
        if click_count == 0:
            set1stPoint(coords)
        elif click_count == 1:
            set2ndPoint(coords)
        click_count = (click_count + 1) % 2

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