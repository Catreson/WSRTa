from gpse import *
from lap import Lap
from lapsplit import *
from laprefer import *
import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import filedialog
from tkinter import ttk
import customtkinter
import matplotlib.pyplot as plt
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
from matplotlib.widgets import MultiCursor
import pandas as pd
from tkcalendar import Calendar
from datetime import datetime
import time
import tkintermapview as tkm
import os


class LFGener(ttk.LabelFrame):
    def __init__(self, master, filetype, filedescription, titel, *args, **kwargs):
        ttk.LabelFrame.__init__(self, master, *args, **kwargs)
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
        ViewWindow(self, self.path)
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
                time.sleep(0.1)
                try:
                    self.master.label_processing.config(text="Complete",bg="green")
                except:
                    print('No use like this')
                self.update_idletasks()
                time.sleep(0.1)
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
class FinishlineInfo(tk.Frame):
    def __init__(self, master, path, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.path = path
        self.click_count = 0
        self.config(height=600,
                    width=250)
        self.data = pd.read_csv(self.path)
        print(self.data.columns)

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
        self.input_tolerance.insert(0, 2)
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

    def buttonContinue(self):
        start_line = [(float(self.input_lon_1.get()), float(self.input_lat_1.get())), (float(self.input_lon_2.get()), float(self.input_lat_2.get()))]
        minimal_laptime = float(self.input_minimal.get())
        finish_line_tolerance = float(self.input_tolerance.get())
        self.master.master.label_processing.config(text="Processing...",fg="yellow")
        laps = findLaps(self.data, start_line, minimal_laptime, finish_line_tolerance)
        laps_path, tag = createSessionFile(str(self.path), laps, **self.master.session_metadata)
        laps_data = splitLaps(self.data, laps)
        saveLaps(laps_path, laps_data, tag)
        self.master.master.label_processing.config(text="Complete",bg="green")
class SplitWindow(tk.Toplevel):
    def __init__(self, master, path, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
        self.master = master
        self.path = path
        self.session_metadata = {}
        self.frames = []
        self.frames.append(RiderInfo(self, self.path))
        self.frames.append(FinishlineInfo(self, self.path))

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
class LapSelectionWindow(tk.Toplevel):
    def __init__(self, master, king, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
        self.master = master
        self.king = king
        self.iconbitmap('wsrta.ico')
        self.title('Lap selection')
        self.config(width=400,
                    height=200)
        self.lift()
        self.attributes('-topmost',True)
        self.after_idle(self.attributes,'-topmost',False)
        self.lap_list_select = tk.Variable(value=[[x.ID, x.laptime] for x in self.king.laps.values()])
        self.to_filter_select = tk.Variable(value=[x for x in next(iter(self.king.laps.values())).df.columns])
        self.select_frame = tk.LabelFrame(self,
                                          text = 'Select laps')
        self.refer_frame = tk.LabelFrame(self,
                                          text = 'Select reference lap')
        self.filter_frame = tk.LabelFrame(self,
                                          text = 'Apply MAF to channel')
        self.selec_list = tk.Listbox(self.select_frame,
                         height=5,
                         listvariable=self.lap_list_select,
                         selectmode=tk.MULTIPLE)
        self.selec_butt = ttk.Button(self.select_frame,
                                     text = 'Select Laps',
                                     command = self.loadLaps)
        self.laps_selected = tk.Variable()
        self.reference_list = tk.Listbox(self.refer_frame,
                         height=5,
                         listvariable=self.laps_selected,
                         selectmode=tk.SINGLE)
        self.reference_butt = ttk.Button(self.refer_frame,
                                     text = 'Refer to Lap',
                                     command = self.referLaps)
        
        self.save_butt = ttk.Button(self,
                                     text = 'Save current state',
                                     command = self.saveLaps)

        self.to_filter_list = tk.Listbox(self.filter_frame,
                         height=5,
                         listvariable=self.to_filter_select,
                         selectmode=tk.MULTIPLE)
        self.apply_filter_butt = ttk.Button(self.filter_frame,
                                            text = 'Apply',
                                            command = self.applyFilter)
        self.filter_window_l = tk.Label(self.filter_frame,
                                        text = 'Set window')
        self.filter_window = tk.Entry(self.filter_frame)
        self.filter_window.insert(0, 15)
        self.filter_weight_l = tk.Label(self.filter_frame,
                                        text = 'Set weight')
        self.filter_weight = tk.Entry(self.filter_frame)
        self.filter_weight.insert(0, 0.6)
        self.filter_diff_l = tk.Label(self.filter_frame,
                                        text = 'Set max diff')
        self.filter_diff = tk.Entry(self.filter_frame)
        self.filter_diff.insert(0, 100)
        
        self.selec_list.pack()
        self.selec_butt.pack()
        self.reference_list.pack()
        self.reference_butt.pack()

        self.to_filter_list.grid(column=0, row=0, rowspan=5)
        self.apply_filter_butt.grid(column=0,row=5)
        self.filter_window_l.grid(column=1, row=0)
        self.filter_window.grid(column=2, row=0)
        self.filter_weight_l.grid(column=1, row=1)
        self.filter_weight.grid(column=2, row=1)
        self.filter_diff_l.grid(column=1, row=2)
        self.filter_diff.grid(column=2, row=2)

        self.select_frame.grid(column=0, row=0)
        self.refer_frame.grid(column=1, row=0)
        self.filter_frame.grid(column=0, row=1, columnspan=3)
        self.save_butt.grid(column=2,row=0)

    def loadLaps(self):
        lista = []
        for i in self.selec_list.curselection():
            tmp = self.selec_list.get(i)[0]
            lista.append([tmp, self.king.laps[tmp].color])
        self.king.selected_laps_ids = [x[0] for x in lista]
        self.laps_selected.set(lista)

    def referLaps(self):
        self.king.reference_lap_id = self.reference_list.get(self.reference_list.curselection())[0]
        referLapsToLap([self.king.laps[x] for x in self.king.selected_laps_ids], self.king.laps[self.king.reference_lap_id].ID)
        self.king.lapsSelected()

    def applyFilter(self):
        for i in self.to_filter_list.curselection():
            for lap in self.king.laps.values():
                lap.simpleSmoother(tag = self.to_filter_list.get(i),
                                   window = int(self.filter_window.get()),
                                   weight = float(self.filter_weight.get()),
                                   max_diff = float(self.filter_diff.get()))

    def saveLaps(self):
        for lap in self.master.laps.values():
            lap.saveLap()
class ScrollFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
class MapFrame(tk.Frame):
    def __init__(self, master, king,  *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.king = king
        #self.height= 400
        #self.width = 600
        self.height= self.master['height']
        self.width = self.master['width']
        print(f'h: {self.height}, w: {self.width}')
        self.config(height=self.height,
                    width=self.width)
        self.map_widget = tkm.TkinterMapView(self, width=self.width, height=self.height, corner_radius=0)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(self.king.lat_start, self.king.lon_start)

        self.king.subscribeAll(self.plotLaps)
        self.king.subscribeXLims(self.update)
        self.map_widget.pack()

    def showMapPoint(self):
        lap = self.king.laps[self.king.reference_lap_id]
        distancer = self.king.distancer
        ind = 0
        coords = []
        for i, row in lap.df.iterrows():
            if row['distance'] > distancer:
                ind = i
                break
        coords = perpendicularLine(lap.df['latitude'][ind], lap.df['longitude'][ind], lap.df['course'][ind], 10)
        self.map_widget.set_path(coords,
                             color=lap.color,
                             width=2)
        self.map_widget.set_position(lap.df['latitude'][ind], lap.df['longitude'][ind])

    def plotLaps(self):
        self.map_widget.delete_all_path()
        reference_lap = self.king.laps[self.king.reference_lap_id]
        x_min = self.king.x_lims[0] if self.king.x_lims[0] > 0 else 0
        x_max = self.king.x_lims[1]
        i_min = 0
        i_max = len(reference_lap.df['longitude']) - 1
        min_set = False
        for i, row in reference_lap.df.iterrows():    
            if  not min_set and row['distance'] > x_min:
                i_min = i
                min_set = True
            if row['distance'] > x_max:
                i_max = i
                break
        #print(f'i_max {i_max}, i_min { i_min}')
        self.map_widget.set_position(reference_lap.df['latitude'][5], reference_lap.df['longitude'][5])
        self.map_widget.set_path(list(zip(reference_lap.df['latitude'][i_min:i_max], reference_lap.df['longitude'][i_min:i_max])),
                             color=reference_lap.color,
                             width=2)
        for lap_id in self.king.selected_laps_ids:
            if lap_id != reference_lap.ID:
                ises = reference_lap.df[lap_id][i_min:i_max]
                coords = [(self.king.laps[lap_id].df['latitude'][x], self.king.laps[lap_id].df['longitude'][x]) for x in ises]
                self.map_widget.set_path(coords,
                                    color=self.king.laps[lap_id].color,
                                    width=2)
                
    def update(self):
        self.plotLaps()
        self.showMapPoint()
class MapFrame1(tk.Frame):
    def __init__(self, master, king, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.king = king
        self.map_widget = tkm.TkinterMapView(self)
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        self.map_widget.set_position(self.king.lat_start, self.king.lon_start)

        self.king.subscribeAll(self.plotLaps)
        self.king.subscribeXLims(self.update)

    def showMapPoint(self):
        lap = self.king.laps[self.king.reference_lap_id]
        distancer = self.king.distancer
        ind = 0
        coords = []
        for i, row in lap.df.iterrows():
            if row['distance'] > distancer:
                ind = i
                break
        coords = perpendicularLine(lap.df['latitude'][ind], lap.df['longitude'][ind], lap.df['course'][ind], 10)
        self.map_widget.set_path(coords,
                             color=lap.color,
                             width=2)
        self.map_widget.set_position(lap.df['latitude'][ind], lap.df['longitude'][ind])

    def plotLaps(self):
        self.map_widget.delete_all_path()
        reference_lap = self.king.laps[self.king.reference_lap_id]
        x_min = self.king.x_lims[0] if self.king.x_lims[0] > 0 else 0
        x_max = self.king.x_lims[1]
        i_min = 0
        i_max = len(reference_lap.df['longitude']) - 1
        min_set = False
        for i, row in reference_lap.df.iterrows():    
            if  not min_set and row['distance'] > x_min:
                i_min = i
                min_set = True
            if row['distance'] > x_max:
                i_max = i
                break
        #print(f'i_max {i_max}, i_min { i_min}')
        self.map_widget.set_position(reference_lap.df['latitude'][5], reference_lap.df['longitude'][5])
        self.map_widget.set_path(list(zip(reference_lap.df['latitude'][i_min:i_max], reference_lap.df['longitude'][i_min:i_max])),
                             color=reference_lap.color,
                             width=2)
        for lap_id in self.king.selected_laps_ids:
            if lap_id != reference_lap.ID:
                ises = reference_lap.df[lap_id][i_min:i_max]
                coords = [(self.king.laps[lap_id].df['latitude'][x], self.king.laps[lap_id].df['longitude'][x]) for x in ises]
                self.map_widget.set_path(coords,
                                    color=self.king.laps[lap_id].color,
                                    width=2)
                
    def update(self):
        self.plotLaps()
        self.showMapPoint()

class WideChartFrame(ScrollFrame):
    def __init__(self, master, king, *args, **kwargs):
        ScrollFrame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.king = king
        self.height = 1000
        self.width = 1000
        self.tag_list = ['gps_speed']
        self.pack_propagate(False)
        self.config(height=self.height,
                    width=self.width)
        self.scroll_frame.config(height= 3*self.height,
                                 width=self.width)
        self.selected_add = tk.StringVar()
        self.options = [x for x in self.king.laps[self.king.reference_lap_id].df.columns]
        self.selected_add.set(self.options[1])

        self.fig = Figure(figsize = (self.width/self.king.depei, len(self.tag_list) * (self.width/4)/self.king.depei), 
                 dpi = 100)
        self.canvas = FigureCanvasTkAgg(self.fig, 
                               master = self.scroll_frame)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, 
                                   self.scroll_frame) 
        self.toolbar.update() 
        
        self.canvas_wg = self.canvas.get_tk_widget()
        
        self.control_panel = tk.Frame(self.scroll_frame)
        self.add_butt = tk.Button(self.control_panel,
                         text='Add chart',
                         command=self.addChart)
        self.remove_butt = tk.Button(self.control_panel,
                         text='Remove  chart',
                         command=self.removeChart)
        self.add_list = tk.OptionMenu(self.control_panel,
                             self.selected_add,
                             *self.options)
        
        self.bmanage = tk.Button(self.control_panel, text='manage',
                                 command = self.manage
                                 )
        self.bforget = tk.Button(self.control_panel, text='forget',
                                 command = self.forget
                                 )

        self.add_list.pack(side=tk.LEFT)
        self.add_butt.pack(side=tk.LEFT)
        self.remove_butt.pack(side=tk.LEFT)
        self.bmanage.pack(side=tk.LEFT)
        self.bforget.pack(side=tk.LEFT)
        self.control_panel.pack(side=tk.TOP, fill=tk.X)
        
        self.king.subscribeAll(self.addRemoveChart)
        self.addRemoveChart('0')

    def manage(self):
        test=self.king.wm_manage(self.master)
        self.king.frame2.pack()

    def forget(self):
        self.king.frame2.pack_forget()
        self.king.wm_forget(self.master)
        self.king.frame1.pack()

    def reloadCharts(self):
        self.canvas_wg.pack_forget()
        self.toolbar.pack_forget()

        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas_wg.pack(side=tk.TOP)


    def addChart(self):
        tag = self.selected_add.get()
        if tag not in self.tag_list:
            self.tag_list.append(tag)
            self.addRemoveChart('+')   

    def removeChart(self):
        tag = self.selected_add.get()
        if tag in self.tag_list:
            self.tag_list.remove(tag)
            self.addRemoveChart('-')    

    def on_xlims_change(self, event_ax):
        x_lims = event_ax.get_xlim()
        self.king.setXLims(x_lims)

    def on_click(self, event):
        if event.button == 3:
            distancer = event.xdata
            self.king.setDistancer(distancer)
            for plot in self.plot_list:
                try:
                    plot.lines = plot.get_lines()[0]
                except:
                    print('Chuj')
                plot.axvline(x=event.xdata, color="g", linewidth=2)

    def addRemoveChart(self, sign = '0'):
        tmp = self.fig.get_size_inches()
        self.canvas_wg.destroy()
        self.toolbar.destroy()
        additional_height = (self.width/4)/self.king.depei if sign == '+' else -(self.width/4)/self.king.depei if sign =='-' else 0
        reference_lap = self.king.laps[self.king.reference_lap_id]

        self.fig = Figure(figsize = (tmp[0], tmp[1] + additional_height), 
                 dpi = 100) 
        no_plots = len(self.tag_list)
        self.plot_list = []
        for i, tagg in enumerate(self.tag_list):
            if i == 0:
                self.plot_list.append(self.fig.add_subplot(no_plots, 1, i + 1))
            else:
                self.plot_list.append(self.fig.add_subplot(no_plots, 1, i + 1, sharex=self.plot_list[0]))
            self.plot_list[i].plot(reference_lap.df['distance'], reference_lap.df[tagg], color = reference_lap.color)
            for lap_id in self.king.selected_laps_ids:
                if lap_id != self.king.reference_lap_id:
                    lap = self.king.laps[lap_id]
                    xses = reference_lap.df['distance']
                    yreks = [lap.df[tagg][x] for x in reference_lap.df[lap.ID]]
                    self.plot_list[i].plot(xses, yreks, color = lap.color)
            self.plot_list[i].grid(visible=True)
            self.plot_list[i].set_ylabel(tagg)
            if i == 0:
                self.plot_list[i].callbacks.connect('xlim_changed', self.on_xlims_change)
            cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas = FigureCanvasTkAgg(self.fig, 
                           master = self.scroll_frame)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, 
                                   self.scroll_frame) 
        self.toolbar.update()  
        self.canvas_wg = self.canvas.get_tk_widget()
        self.reloadCharts()

class WideChartFrame1(ScrollFrame):
    def __init__(self, master, king, *args, **kwargs):
        ScrollFrame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.king = king
        self.height = self.master.winfo_height()
        self.width = self.master.winfo_width()
        self.tag_list = ['gps_speed']
        #self.pack_propagate(False)
        self.config(height=self.height,
                    width=self.width)
        self.scroll_frame.config(height= 3*self.height,
                                 width=self.width)
        self.selected_add = tk.StringVar()
        self.options = [x for x in self.king.laps[self.king.reference_lap_id].df.columns]
        self.selected_add.set(self.options[1])

        self.fig = Figure(figsize = (self.width/self.king.depei, len(self.tag_list) * (self.width/4)/self.king.depei), 
                 dpi = 100)
        self.canvas = FigureCanvasTkAgg(self.fig, 
                               master = self.scroll_frame)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, 
                                   self.scroll_frame) 
        self.toolbar.update() 
        
        self.canvas_wg = self.canvas.get_tk_widget()
        
        self.control_panel = tk.Frame(self.scroll_frame)
        self.add_butt = tk.Button(self.control_panel,
                         text='Add chart',
                         command=self.addChart)
        self.remove_butt = tk.Button(self.control_panel,
                         text='Remove  chart',
                         command=self.removeChart)
        self.add_list = tk.OptionMenu(self.control_panel,
                             self.selected_add,
                             *self.options)
        
        self.bmanage = tk.Button(self.control_panel, text='manage',
                                 command = self.manage
                                 )
        self.bforget = tk.Button(self.control_panel, text='forget',
                                 command = self.forget
                                 )

        self.add_list.pack(side=tk.LEFT)
        self.add_butt.pack(side=tk.LEFT)
        self.remove_butt.pack(side=tk.LEFT)
        self.bmanage.pack(side=tk.LEFT)
        self.bforget.pack(side=tk.LEFT)
        self.control_panel.pack(side=tk.TOP, fill=tk.X)
        
        self.king.subscribeAll(self.addRemoveChart)
        self.addRemoveChart('0')

    def manage(self):
        test=self.king.wm_manage(self.master)

    def forget(self):
        self.king.wm_forget(self.master)
        self.pack()

    def reloadCharts(self):
        self.canvas_wg.pack_forget()
        self.toolbar.pack_forget()

        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas_wg.pack(side=tk.TOP)


    def addChart(self):
        tag = self.selected_add.get()
        if tag not in self.tag_list:
            self.tag_list.append(tag)
            self.addRemoveChart('+')   

    def removeChart(self):
        tag = self.selected_add.get()
        if tag in self.tag_list:
            self.tag_list.remove(tag)
            self.addRemoveChart('-')    

    def on_xlims_change(self, event_ax):
        x_lims = event_ax.get_xlim()
        self.king.setXLims(x_lims)

    def on_click(self, event):
        if event.button == 3:
            distancer = event.xdata
            self.king.setDistancer(distancer)
            for plot in self.plot_list:
                try:
                    plot.lines = plot.get_lines()[0]
                except:
                    print('Chuj')
                plot.axvline(x=event.xdata, color="g", linewidth=2)

    def addRemoveChart(self, sign = '0'):
        tmp = self.fig.get_size_inches()
        self.canvas_wg.destroy()
        self.toolbar.destroy()
        additional_height = (self.width/4)/self.king.depei if sign == '+' else -(self.width/4)/self.king.depei if sign =='-' else 0
        reference_lap = self.king.laps[self.king.reference_lap_id]

        self.fig = Figure(figsize = (tmp[0], tmp[1] + additional_height), 
                 dpi = 100) 
        no_plots = len(self.tag_list)
        self.plot_list = []
        for i, tagg in enumerate(self.tag_list):
            if i == 0:
                self.plot_list.append(self.fig.add_subplot(no_plots, 1, i + 1))
            else:
                self.plot_list.append(self.fig.add_subplot(no_plots, 1, i + 1, sharex=self.plot_list[0]))
            self.plot_list[i].plot(reference_lap.df['distance'], reference_lap.df[tagg], color = reference_lap.color)
            for lap_id in self.king.selected_laps_ids:
                if lap_id != self.king.reference_lap_id:
                    lap = self.king.laps[lap_id]
                    xses = reference_lap.df['distance']
                    yreks = [lap.df[tagg][x] for x in reference_lap.df[lap.ID]]
                    self.plot_list[i].plot(xses, yreks, color = lap.color)
            self.plot_list[i].grid(visible=True)
            self.plot_list[i].set_ylabel(tagg)
            if i == 0:
                self.plot_list[i].callbacks.connect('xlim_changed', self.on_xlims_change)
            cid = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas = FigureCanvasTkAgg(self.fig, 
                           master = self.scroll_frame)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, 
                                   self.scroll_frame) 
        self.toolbar.update()  
        self.canvas_wg = self.canvas.get_tk_widget()
        self.reloadCharts()

class SquareChartFrame(ScrollFrame):
    def __init__(self, master, king, *args, **kwargs):
        ScrollFrame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.king = king
        self.height = self.master.winfo_height()
        self.width = self.master.winfo_width()
        self.tag_list = [['acc_n_g', 'acc_t_g']]
        self.pack_propagate(False)
        self.config(height=self.height,
                    width=self.width)
        self.scroll_frame.config(height= 3*self.height,
                                 width=self.width)
        self.selected_x_add = tk.StringVar()
        self.options = [x for x in self.king.laps[self.king.reference_lap_id].df.columns]
        self.selected_x_add.set(self.options[0])
        self.selected_y_add = tk.StringVar()
        self.selected_y_add.set(self.options[1])

        self.fig = Figure(figsize = (self.width/self.king.depei, len(self.tag_list) * (self.width/2)/self.king.depei), 
                 dpi = 100)
        self.canvas = FigureCanvasTkAgg(self.fig, 
                               master = self.scroll_frame)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, 
                                   self.scroll_frame) 
        self.toolbar.update() 
        
        self.canvas_wg = self.canvas.get_tk_widget()
        
        self.control_panel = tk.Frame(self.scroll_frame)
        self.add_butt = tk.Button(self.control_panel,
                         text='Add chart',
                         command=self.addChart)
        self.remove_butt = tk.Button(self.control_panel,
                         text='Remove  chart',
                         command=self.removeChart)
        self.add_x_list = tk.OptionMenu(self.control_panel,
                             self.selected_x_add,
                             *self.options)
        self.add_y_list = tk.OptionMenu(self.control_panel,
                             self.selected_y_add,
                             *self.options)

        self.add_x_list.pack(side=tk.LEFT)
        self.add_y_list.pack(side=tk.LEFT)
        self.add_butt.pack(side=tk.LEFT)
        self.remove_butt.pack(side=tk.LEFT)
        self.control_panel.pack(side=tk.TOP, fill=tk.X)
        
        self.king.subscribeAll(self.addRemoveChart)
        self.king.subscribeXLims(self.addRemoveChart)
        self.addRemoveChart('0')

    def reloadCharts(self):
        self.canvas_wg.pack_forget()
        self.toolbar.pack_forget()

        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.canvas_wg.pack(side=tk.TOP)


    def addChart(self):
        tag = [self.selected_x_add.get(), self.selected_y_add.get()]
        if tag not in self.tag_list:
            self.tag_list.append(tag)
            self.addRemoveChart('+')   

    def removeChart(self):
        tag = [self.selected_x_add.get(), self.selected_y_add.get()]
        if tag in self.tag_list:
            self.tag_list.remove(tag)
            self.addRemoveChart('-')    

    def on_xlims_change(self, event_ax):
        x_lims = event_ax.get_xlim()
        self.king.setXLims(x_lims)

    def on_click(self, event):
        if event.button == 3:
            distancer = event.xdata
            self.king.setDistancer(distancer)
            for plot in self.plot_list:
                try:
                    plot.lines = plot.get_lines()[0]
                except:
                    print('Chuj')
                plot.axvline(x=event.xdata, color="g", linewidth=2)

    def addRemoveChart(self, sign = '0'):
        tmp = self.fig.get_size_inches()
        self.canvas_wg.destroy()
        self.toolbar.destroy()
        additional_height = (self.width/2)/self.king.depei if sign == '+' else -(self.width/2)/self.king.depei if sign =='-' else 0
        reference_lap = self.king.laps[self.king.reference_lap_id]
        i_min = -1
        i_max = len(reference_lap.df['distance']) - 1
        x_min = self.king.x_lims[0] if self.king.x_lims[0] > 0 else 0
        x_max = self.king.x_lims[1]
        for i, row in reference_lap.df.iterrows():    
            if  i_min == -1 and row['distance'] > x_min:
                i_min = i
            if row['distance'] > x_max:
                i_max = i
                break
        print(f'i_max {i_max}, i_min { i_min}')
        self.fig = Figure(figsize = (tmp[0], tmp[1] + additional_height), 
                 dpi = 100) 
        no_plots = len(self.tag_list)
        self.plot_list = []
        for i, tagg in enumerate(self.tag_list):
            if i == 0:
                self.plot_list.append(self.fig.add_subplot(no_plots, 1, i + 1))
            else:
                self.plot_list.append(self.fig.add_subplot(no_plots, 1, i + 1))
            self.plot_list[i].scatter(reference_lap.df[tagg[0]][i_min:i_max], reference_lap.df[tagg[1]][i_min:i_max], marker = ".", sizes=[2 for x in reference_lap.df[tagg[0]][i_min:i_max]])
            """for lap_id in self.king.selected_laps_ids:
                if lap_id != self.king.reference_lap_id:
                    lap = self.king.laps[lap_id]
                    xses = reference_lap.df['distance']
                    yreks = [lap.df[tagg][x] for x in reference_lap.df[lap.ID]]
                    self.plot_list[i].plot(xses, yreks, color = lap.color)"""
            self.plot_list[i].grid(visible=True)
            self.plot_list[i].set_ylabel(tagg)
        self.canvas = FigureCanvasTkAgg(self.fig, 
                           master = self.scroll_frame)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, 
                                   self.scroll_frame) 
        self.toolbar.update()  
        self.canvas_wg = self.canvas.get_tk_widget()
        self.reloadCharts()        

class TestFrame(tk.Frame):
    def __init__(self, master, king, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.king = king
        self.master = master
        self.control = tk.Frame(self)
        self.selected_tile = tk.StringVar()
        self.hor_butt = tk.Button(self.control,
                              text= 'Split verticaly',
                              command = self.splitVer)
        self.ver_butt = tk.Button(self.control,
                              text= 'Split horizontaly',
                              command = self.splitHor)
        self.select_tile = ttk.Combobox(self.control,
                                         textvariable=self.selected_tile,
                                         values = list(self.king.tile_dic))
        self.cre_butt = tk.Button(self.control,
                              text= 'Make content',
                              command = self.addTile)
        self.hor_butt.pack(fill=tk.BOTH)
        self.ver_butt.pack(fill=tk.BOTH)
        self.select_tile.pack(fill=tk.BOTH)
        self.cre_butt.pack(fill=tk.BOTH)
        self.control.pack(fill=tk.BOTH, expand=1)
        self.pan = None
        self.content = None
        self.slaves = []
    
    def addTile(self):
        self.control.destroy()
        self.content = self.king.tile_dic[self.selected_tile.get()](self, self.king)
        self.content.pack(fill=tk.BOTH, expand=1)

    def splitVer(self):
        direction_split = tk.VERTICAL
        size = self['height'] / 2
        self.split(direction_split, size)

    def splitHor(self):
        direction_split = tk.HORIZONTAL
        size = self['width'] / 2
        self.split(direction_split, size)
    
    def split(self, direction_split, size):
        self.pan = tk.PanedWindow(self, orient=direction_split, sashrelief="raised")
        self.pan.pack(fill=tk.BOTH, expand=True)
        self.control.pack_forget()
        tmp1 = TestFrame(self, self.king)
        tmp2 = TestFrame(self, self.king)
        self.pan.add(tmp1, minsize = size)
        self.pan.add(tmp2, minsize = size)
        self.slaves.append(tmp1)
        self.slaves.append(tmp2)
        #self.configure(width= 2 * self['width'])
        self.king.update_idletasks()
        print(self.slaves)



class TmpFrame(tk.PanedWindow):
    def __init__(self, master, king, *args, **kwargs):
        tk.PanedWindow.__init__(self, master, *args, **kwargs)
        self.king = king
        self.master = master
        self.pan = tk.PanedWindow(self)
        self.ll = tk.Label(self.pan,
                           text= 'Hello')
        self.ll.pack()
        self.add(self.pan)
        self.map_frame = MapFrame(self, self.king)
        self.chart_frame = None
        self.scatter_frame = None

        self.king.subscribeAll(self.loadElements)
        #self.map_frame.grid(column=1,row=0,
        #                    sticky=tk.E)
        self.add(self.map_frame)
    def loadElements(self):
        self.chart_frame = WideChartFrame(self, self.king)
        self.scatter_frame = SquareChartFrame(self, self.king)
        """self.chart_frame.grid(column=0,row=0,
                              rowspan=3,
                              sticky=tk.W)
        self.scatter_frame.grid(column=1,row=1,
                              sticky=tk.W)"""
        self.pan.add(self.chart_frame)
        self.pan.add(self.scatter_frame)
        
class TmpFrame1(tk.Frame):
    def __init__(self, master, king, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.king = king
        self.master = master
        self.map_frame = MapFrame(self, self.king)
        self.chart_frame = None
        self.scatter_frame = None

        self.king.subscribeAll(self.loadElements)
        self.map_frame.grid(column=1,row=0,
                            sticky=tk.E)
    def loadElements(self):
        self.chart_frame = WideChartFrame(self, self.king)
        self.chart_frame.grid(column=0,row=0,
                              rowspan=3,
                              sticky=tk.W)
            

class ViewWindow(tk.Toplevel):
    def __init__(self, master, path, *args, **kwargs):
        tk.Toplevel.__init__(self, master, *args, **kwargs)
        self.master = master
        self.iconbitmap('wsrta.ico')
        self.subscribed_all = []
        self.subscribed_x_lims = []
        self.title('Laps preview')
        self.laps = None
        self.selected_laps_ids = None
        self.reference_lap_id = None
        self.x_lims = [0, 10000]
        self.distancer = 10
        self.tile_dic = {'mapa':MapFrame1,
                         'wide chart':WideChartFrame1,
                         'square chart':SquareChartFrame}
        #self.tag_list = ['gps_speed']
        self.path = path
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry(f'{self.width}x{self.height}')
        self.depei = self.winfo_fpixels('1i')
        self.loadLaps()
        self.lat_start, self.lon_start = next(iter(self.laps.values())).df[['latitude', 'longitude']].iloc[5]
        self.lap_selection = LapSelectionWindow(self, self)
        self.control_panel = tk.Frame(self)
        self.add_tab = tk.Button(self.control_panel,
                                 text = '+',
                                 command= self.new_tab)
        self.tabs_ids = ['tab1']
        #self.tabs = {self.tabs_ids[0] : TmpFrame(self, self),
        #             self.tabs_ids[1] : TmpFrame1(self, self)}
        self.tabs = {self.tabs_ids[0] : TestFrame(self, self)}
        self.selected_tab_id = tk.StringVar()
        self.control_box = ttk.Combobox(self.control_panel,
                                         textvariable=self.selected_tab_id,
                                         values = self.tabs_ids)
        self.control_box.set(self.tabs_ids[0])
        self.control_box.pack(side=tk.LEFT)
        self.control_box.bind('<<ComboboxSelected>>', self.switch_tab)
        self.add_butt = tk.Button(self.control_panel,
                                  text='Add tab',
                                  command=self.new_tab)
        self.add_butt.pack(side=tk.LEFT)
        #self.tabs = ViewBook(self.frame, self)
        self.frame = self.tabs['tab1']
        self.control_panel.pack()
        self.frame.pack(fill=tk.BOTH, expand=True)
        

    def loadLaps(self):
        self.laps = getLaps(self.path)

    def subscribeAll(self, widget_reload):
        self.subscribed_all.append(widget_reload)

    def subscribeXLims(self, widget_reload):
        self.subscribed_x_lims.append(widget_reload)

    def lapsSelected(self):
        self.triggerAll()

    def triggerAll(self):
        for sub in self.subscribed_all:
            sub()

    def triggerXLims(self):
        for sub in self.subscribed_x_lims:
            sub()

    def setXLims(self, x_lims):
        self.x_lims = x_lims
        self.triggerXLims()

    def setDistancer(self, distancer):
        self.distancer = distancer
        self.triggerXLims()

    def new_tab(self):
        top = tk.Toplevel(self)
        top.title('Set name')
        entr = tk.Entry(top)
        be = tk.Button(top,
                       text='Add',
                       command= lambda: self.create_tab(entr.get(), top))
        entr.pack()
        be.pack()
        #self.control_box['values'] = self.tabs_ids

    def create_tab(self, name, top):
        self.tabs_ids.append(name)
        self.tabs[name] = TestFrame(self, self)
        self.control_box['values'] = self.tabs_ids
        top.destroy()

    def switch_tab(self, event):
        self.frame.pack_forget()
        self.frame = self.tabs[self.selected_tab_id.get()]
        self.frame.pack(fill=tk.BOTH, expand=True)


class MainWindow(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.lfParse = LFParse(self)
        self.lfSplit = LFSplit(self)
        self.lfView = LFView(self)
        self.lfControl = LFControl(self)
        self.pack_self()

    def pack_self(self):
        self.lfParse.pack(side="left",anchor=tk.SW)
        self.lfSplit.pack(side="left",anchor=tk.SW)
        self.lfView.pack(side="left",anchor=tk.SW)
        self.lfControl.pack(side="left",anchor=tk.SW)

if __name__ == '__main__':
    rut = ThemedTk('Arc')
    rut.iconbitmap('wsrta.ico')
    rut.title('File basic analysis and parsing')
    rut.geometry('580x140')
    MainWindow(rut).pack()
    plt.style.use('dark_background')
    #main lup
    rut.mainloop()