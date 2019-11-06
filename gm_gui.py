# from matplotlib.backends.backend_tkagg import
from tkinter import Tk, Label, Frame, Button, Checkbutton, Entry
from tkinter import StringVar, IntVar, DoubleVar, BooleanVar
from tkinter import E, BOTTOM, TOP, BOTH
from tkinter import messagebox, filedialog
from sigpropy import TimeSeries, FourierTransform
import obspy
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import json
import os
import logging
logging.basicConfig(level=logging.DEBUG)

rcParams.update({'figure.autolayout': True})


class GroundMotionProcessing():

    def __init__(self, master):
        self.master = master
        self.init_layout()

        self.fig1, self.ax1 = plt.subplots(nrows=1, ncols=1, figsize=(5, 2.5))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, self.frame2)
        self.canvas1.get_tk_widget().grid(row=1, column=0)
        tb1 = NavigationToolbar2Tk(self.canvas1, self.frame2_1)
        tb1.update()
        self.canvas1._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        self.fig2, self.ax2 = plt.subplots(nrows=1, ncols=1, figsize=(5, 2.5))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, self.frame4)
        self.canvas2.get_tk_widget().grid(row=1, column=1)
        tb2 = NavigationToolbar2Tk(self.canvas2, self.frame4_1)
        tb2.update()
        self.canvas2._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        self.load_new_file()

    def update_tseries_plot(self):
        logging.info("begin - update_tseries_plot()")
        self.ax1.clear()
        self.ax1.plot(self.tseries.time, self.tseries.amp)
        self.ax1.set_title("Time Domain")
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Amplitude")
        self.canvas1.draw()

    def update_fseries_plot(self):
        logging.info("begin - update_fseries_plot()")
        if bool(self.fseries):
            self.ax2.clear()
            self.ax2.plot(self.fseries.frq, self.fseries.mag)
        self.ax2.set_title("Frequency Domain")
        self.ax2.set_xlabel("Frequency (Hz)")
        self.ax2.set_ylabel("Amplitude")
        self.ax2.set_xscale("log")
        self.canvas2.draw()

    def init_layout(self):
        logging.info("begin - init_layout()")
        title_font = 'Arial 11 underline'

        frame_bg = '#ffffff'
        label_bg = '#ffffff'
        entry_bg = '#e1e7ea'
        check_bg = entry_bg
        button_bg = frame_bg
        check_bg = frame_bg

        self.master.minsize(6, 6)


        # Frame 1 ----------------------------------------------------
        frame1 = Frame(bg=frame_bg)
        frame1.grid(row=0, column=0)

        title_1 = Label(frame1, text="Time Domain",
                        bg=label_bg, font=title_font)
        title_1.grid(row=0, columnspan=2)

        # Band Pass Filter
        label_1_1_1 = Label(frame1, text="Apply BandPass Filter:",
                            bg=label_bg)
        label_1_1_2 = Label(frame1, text="Lower Frequency Limit (Hz):",
                            bg=label_bg)
        label_1_1_3 = Label(frame1, text="Upper Frequency Limit (Hz):",
                            bg=label_bg)
        label_1_1_4 = Label(frame1, text="Filter Order (#):", bg=label_bg)

        label_1_1_1.grid(row=2, column=0, sticky=E)
        label_1_1_2.grid(row=3, column=0, sticky=E)
        label_1_1_3.grid(row=4, column=0, sticky=E)
        label_1_1_4.grid(row=5, column=0, sticky=E)

        self.apply_filter = BooleanVar()
        self.bp_flow = StringVar()
        self.bp_fhigh = StringVar()
        self.bp_fn = StringVar()
        input_1_1_1 = Checkbutton(frame1, bg=check_bg,
                                  variable=self.apply_filter,
                                  disabledforeground=check_bg)
        input_1_1_2 = Entry(frame1, bg=entry_bg, textvariable=self.bp_flow)
        input_1_1_3 = Entry(frame1, bg=entry_bg, textvariable=self.bp_fhigh)
        input_1_1_4 = Entry(frame1, bg=entry_bg, textvariable=self.bp_fn)

        input_1_1_1.grid(row=2, column=1)
        input_1_1_2.grid(row=3, column=1)
        input_1_1_3.grid(row=4, column=1)
        input_1_1_4.grid(row=5, column=1)

        # Cosine Taper
        self.cos_width = StringVar()
        self.apply_taper = BooleanVar()
        label_1_2_1 = Label(frame1, text="Apply Cosine Taper:", bg=label_bg)
        label_1_2_2 = Label(frame1, text="Width (%):", bg=label_bg)

        label_1_2_1.grid(row=7, column=0, sticky=E)
        label_1_2_2.grid(row=8, column=0, sticky=E)

        input_1_2_1 = Checkbutton(frame1, bg=check_bg,
                                  variable=self.apply_taper,
                                  disabledforeground=check_bg)
        input_1_2_2 = Entry(frame1, bg=entry_bg, textvariable=self.cos_width)

        input_1_2_1.grid(row=7, column=1)
        input_1_2_2.grid(row=8, column=1)

        # Run / Undo / New File
        subframe = Frame(frame1)
        subframe.grid(row=9, columnspan=2)
        input_1_3_1 = Button(subframe, command=self.edit_tseries,
                             text="Apply", bg=button_bg)
        input_1_3_2 = Button(subframe, command=self.reload_file,
                             text="Undo", bg=button_bg)
        input_1_3_3 = Button(subframe, command=self.load_new_file,
                             text="New File", bg=button_bg)
        input_1_3_4 = Button(subframe, command=self.new_fseries,
                             text="FFT", bg=button_bg)

        input_1_3_1.grid(row=0, column=1)
        input_1_3_2.grid(row=0, column=2)
        input_1_3_3.grid(row=0, column=3)
        input_1_3_4.grid(row=0, column=4)


        # Frame 2 ----------------------------------------------------
        self.frame2 = Frame(bg=frame_bg)
        self.frame2.grid(row=0, column=1)
        self.frame2_1 = Frame(self.master, bg=frame_bg)
        self.frame2_1.grid(row=1, column=1)


        # Frame 3 ----------------------------------------------------
        frame3 = Frame(bg=frame_bg, bd=1)
        frame3.grid(row=2, column=0, ipadx=1, ipady=1)

        title_3 = Label(frame3, text="Frequency Domain",
                        bg=label_bg, font=title_font)
        title_3.grid(row=0, columnspan=2)

        # Smoothing
        label_3_1_1 = Label(frame3, text="Apply Cosine Taper:", bg=label_bg)
        label_3_1_2 = Label(frame3, text="Smoothing Constant (#):", bg=label_bg)

        label_3_1_1.grid(row=2, column=0, sticky=E)        
        label_3_1_2.grid(row=3, column=0, sticky=E)

        self.apply_smoothing = BooleanVar()
        self.smooth_width = StringVar()
        input_3_1_1 = Checkbutton(frame3, bg=check_bg,
                                  variable=self.apply_smoothing,
                                  disabledforeground=check_bg)
        input_3_1_2 = Entry(frame3, bg=entry_bg,
                            textvariable=self.smooth_width)

        input_3_1_1.grid(row=2, column=1)
        input_3_1_2.grid(row=3, column=1)

        # Resampling
        label_3_2_1 = Label(frame3, text="Apply Resampling:", bg=label_bg)
        label_3_2_2 = Label(frame3, text="Lower Frequency Limit (Hz):",
                            bg=label_bg)
        label_3_2_3 = Label(frame3, text="Upper Frequency Limit (Hz):",
                            bg=label_bg)
        label_3_2_4 = Label(frame3, text="Number of Samples (#)", bg=label_bg)

        label_3_2_1.grid(row=5, column=0, sticky=E)
        label_3_2_2.grid(row=6, column=0, sticky=E)
        label_3_2_3.grid(row=7, column=0, sticky=E)
        label_3_2_4.grid(row=8, column=0, sticky=E)

        self.apply_resampling = BooleanVar()
        self.res_flow = StringVar()
        self.res_fhigh = StringVar()
        self.res_fn = StringVar()
        input_3_2_1 = Checkbutton(frame3, variable=self.apply_resampling,
                                  bg=check_bg, disabledforeground=check_bg)
        input_3_2_2 = Entry(frame3, bg=entry_bg, textvariable=self.res_flow)
        input_3_2_3 = Entry(frame3, bg=entry_bg, textvariable=self.res_fhigh)
        input_3_2_4 = Entry(frame3, bg=entry_bg, textvariable=self.res_fn)

        input_3_2_1.grid(row=5, column=1)
        input_3_2_2.grid(row=6, column=1)
        input_3_2_3.grid(row=7, column=1)
        input_3_2_4.grid(row=8, column=1)

        # Run / Undo / New File
        input_3_3_1 = Button(frame3, command=self.edit_fseries,
                             text="Apply", bg=button_bg)
        input_3_3_1.grid(row=10, columnspan=2)


        # Frame 4 ----------------------------------------------------
        self.frame4 = Frame(bg=frame_bg)
        self.frame4.grid(row=2, column=1)
        self.frame4_1 = Frame(self.master, bg=frame_bg)
        self.frame4_1.grid(row=3, column=1)

        # Destructor
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def new_fseries(self):
        self.applied_smoothing = False
        self.applied_resampling = False
        self.fseries = FourierTransform.from_timeseries(self.tseries)
        self.update_fseries_plot()

    def edit_tseries(self):
        logging.info("begin - edit_tseries()")

        # Apply Bandpass Filter
        if self.apply_filter.get() and not self.applied_filter:
            try:
                self.tseries.bandpassfilter(float(self.bp_flow.get()),
                                            float(self.bp_fhigh.get()),
                                            int(self.bp_fn.get()))
                self.applied_filter = True
            except:
                pass
        # Apply Cosine Taper
        if self.apply_taper.get() and not self.applied_taper:
            try:
                self.tseries.cosine_taper(
                    width=float(self.cos_width.get())/100)
                self.applied_taper = True
            except:
                pass

        # Update plot to reflect changes made to timeseries
        self.update_tseries_plot()

    def edit_fseries(self):
        logging.info("begin - edit_fseries()")

        # Apply K and O Smoothing
        if self.apply_smoothing.get() and not self.applied_smoothing:
            logging.info("  applying_smooting")
            try:
                self.fseries.smooth_konno_ohmachi(
                    float(self.smooth_width.get()))
                self.applied_smoothing = True
            except:
                pass

        # Apply Resampling
        if self.apply_resampling.get() and not self.applied_resampling:
            logging.info("  applying_resampling")
            try:
                self.fseries.resample(float(self.res_flow.get()),
                                      float(self.res_fhigh.get()),
                                      int(self.res_fn.get()),
                                      res_type='log',
                                      inplace=True)
                self.applied_resampling = True
            except:
                pass

        # Update plot to reflect changes made to timeseries
        self.update_fseries_plot()

    def load_new_file(self):
        logging.info("begin - load_new_file()")
        # initialdir = r"D:\CurrentResearch\signalprocessing\gm_gui\data"
        settings_fname = "gm_gui_settings.json"
        if os.path.exists(settings_fname):
            with open(settings_fname, "r") as f:
                settings = json.load(f)
            initialdir = settings["initialdir"]
        else:
            initialdir = r"C:\\"
        resp = filedialog.askopenfilename(initialdir=initialdir)
        # resp = r"D:\CurrentResearch\signalprocessing\gm_gui\data\UT.STN11.A2_C50.miniseed"

        settings = {}
        settings["initialdir"] = os.path.dirname(resp)
        with open(settings_fname, "w") as f:
            json.dump(settings, f)
            
        self.fname = False

        logging.debug(f"    resp = {resp}")
        logging.debug(f"    self.fname = {self.fname}")

        if resp != '':
            self.fname = resp
            self.reload_file()
        else:
            return

    def reload_file(self):
        logging.info("begin - reload_file()")
        # Reset state
        self.applied_filter = False
        self.applied_taper = False
        self.fseries = False

        # Load File and Update Plot to Reflect This
        if self.fname.endswith(".miniseed"):
            traces = obspy.read(self.fname)
            self.tseries = TimeSeries.from_trace(traces[0])
        else:
            df = pd.read_csv(self.fname, names=["time", "amp"])
            self.tseries = TimeSeries(df.amp.to_numpy(), df.time[1]-df.time[0])

        self.update_tseries_plot()
        self.update_fseries_plot()

    def on_closing(self):
        logging.info("begin - on_closing()")
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.master.quit()


root = Tk()
root.title("Ground Motion Processing")
root.configure(bg='#ffffff')
root.update_idletasks()
print("Program Started")
my_gui = GroundMotionProcessing(root)
root.mainloop()
print("Program Finished")
