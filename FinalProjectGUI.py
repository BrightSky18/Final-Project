from tkinter import *
from tkinter import ttk,filedialog,messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.io import wavfile
import scipy.io
import matplotlib.pyplot as plt
import numpy as np


def fetch_audio():
    allowedfiletypes=[('Audio Files','*.mp3;*.wav')]
    ##Still need to convert mp3 files to wav format
    global file_path
    file_path = filedialog.askopenfilename(filetypes=allowedfiletypes)
    if file_path:
        _audio.set(file_path)

    else:
        print("Error, please try again")
        _audio.set("Error, please select an audio file")

    ##displays Audio File/Analysis data 

    #gets variable t, which is a 2 decimal float of the length of the audio file in seconds
    #sample rates is the Hz
    sample_rate, data = wavfile.read(file_path) 
    len_data = len(data)  # holds length of the numpy array 
    t = round(len_data / sample_rate, 2)  # returns duration but in floats and with 2 decimal places

    #converts sample_rates to kHz and rounds the value to 2 decimal places
    kHz = round(sample_rate/1000, 2)

    #text with value and unit
    length = str(t) + ' seconds'
    Frequency = str(kHz) + " kHz"

    #outputs length
    _time.set(length)
    #outputs kHz
    _res.set(Frequency)

def display_waveform():

    sample_rate, data=wavfile.read(file_path)
    t=np.linspace(0,len(data)/sample_rate,len(data), endpoint=False)
    plt.figure()
    plt.plot(t,data,label='Waveform', color='blue')
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (dB)')
    plt.grid(True)
    plt.legend()
    plt.show() ##test to show if plot works
    ##Still need to ensure it works with mp3, can handle multichannel audio, and optionally implement it into the gui.

    #Code below is meant to implement the plot into the gui but is nonfunctional currently.
    ##canvas=FigureCanvasTkAgg(plt.gcf(), master=_root)
    ##canvas.draw()
    ##canvas.get_tk_widget().pack()




def display_lowRT():
    '''Implement a function to graph in low RT60 style. Below is a test command. Delete later'''
    print('Low CLICK')

def display_midRT():
    '''Implement a function to graph in mid RT60 style. Below is a test command. Delete later'''
    print('Mid CLICK')

def display_highRT():
    '''Implement a function to graph in high RT60 style. Below is a test command. Delete later'''
    print('High CLICK')

def display_comboRT():
    '''Implement a function to graph in combined RT60 style. Below is a test command. Delete later'''
    print('Combo CLICK')

def display_tbd():
    '''Implement a function to graph in a style we choose. Below is a test command. Delete later'''
    print('TBD CLICK')


if __name__ == "__main__": # execute logic if run directly

    x = (5, 10, 15) #This is to not cause error. Will remove when line 44 is resolved

#The below is all setting up the main window and the area to choose a file
#ALL CAPS LINE TO SHOW THE ABOVE IS A HEADING COMMENT. TAKE NOTE.
    global _root
    _root = Tk() # instantiate instance of Tk class
    _root.title('WAV Analysis')
    _mainframe = ttk.Frame(_root, padding='5 5 5 5 ') # root is parent of frame
    _mainframe.grid(row=0, column=0, sticky=("E", "W", "N", "S")) # placed on first row,col of parent
    # frame can extend itself in all cardinal directions
    _file_frame = ttk.LabelFrame(
        _mainframe, text='Sound File', padding='5 5 5 5') # label frame
    _file_frame.grid(row=0, column=0, sticky=("E","W")) # only expands E W
    _file_frame.columnconfigure(0, weight=1)
    _file_frame.rowconfigure(0, weight=1) # behaves when resizing

    _audio = StringVar()
    _audio.set('Please import audio file') # displays a message until file is uploaded
    _audio_entry = ttk.Entry(
        _file_frame, width=40, textvariable=_audio) # text box
    _audio_entry.grid(row=0, column=0, sticky=(E, W, S, N), padx=5)
    # place the textbox
    _audioFile_btn = ttk.Button(
        _file_frame, text='Upload file', command=fetch_audio) # create button
    # fetch_audio() is called on button press. Please implement
    _audioFile_btn.grid(row=0, column=1, sticky=W, padx=5)


#The below frame will hold the graph. THIS WILL HAVE TO CHANGE THE LISTBOX TO SOMETHING ELSE. I DO NOT KNOW WHAT
#ALL CAPS LINE TO SHOW THE ABOVE IS A HEADING COMMENT. TAKE NOTE.
    _graphs_frame = ttk.LabelFrame(
        _mainframe, text='Graphing', padding='9 0 0 0')
    _graphs_frame.grid(row=1, column=0, sticky=(N, S, E, W))

    _graph_display = Listbox( #REPLACE THIS LISTBOX. KEEP HEIGHT AND WIDTH THE SAME(12,55)
        _graphs_frame, listvariable=x, height=12, width=55)
    _graph_display.grid(row=0, column=0, sticky=(E, W), pady=5)

#The following are the buttons to display different graphs. Each will require separate implementation functions
# ALL CAPS LINE TO SHOW THE ABOVE IS A HEADING COMMENT. TAKE NOTE.
    _buttons_frame = ttk.LabelFrame(
        _mainframe, text='Select Graph Type', padding='9 0 0 0')
    _buttons_frame.grid(row=1, column=1, sticky=(N, S, E, W))


    _waveform_btn = ttk.Button(
        _buttons_frame, text='Waveform', command=display_waveform)
    _waveform_btn.grid(row=1, column=0, sticky=(W), padx=5)

    _low_btn = ttk.Button(
        _buttons_frame, text='Low RT60', command=display_lowRT)
    _low_btn.grid(row=2, column=0, sticky=(W), padx=5)

    _mid_btn = ttk.Button(
        _buttons_frame, text='Mid RT60', command=display_midRT)
    _mid_btn.grid(row=3, column=0, sticky=(W), padx=5)

    _high_btn = ttk.Button(
        _buttons_frame, text='High RT60', command=display_highRT)
    _high_btn.grid(row=4, column=0, sticky=(W), padx=5)

    _combo_btn = ttk.Button(
        _buttons_frame, text='Combined RT60', command=display_comboRT)
    _combo_btn.grid(row=5, column=0, sticky=(W), padx=5)

    _tbd_btn = ttk.Button(
        _buttons_frame, text='[TBD. Graph of choice]', command=display_tbd)
    _tbd_btn.grid(row=6, column=0, sticky=(W), padx=5)

#A display frame to display required data. When a file is uploaded, it should update these fields with new data
# ALL CAPS LINE TO SHOW THE ABOVE IS A HEADING COMMENT. TAKE NOTE.
    _info_frame = ttk.LabelFrame(
        _mainframe, text='Audio Info/Analysis', padding='9 0 0 0')
    _info_frame.grid(row=0, column=1, sticky=(N, S, E, W))
    _time = StringVar()
    _time.set('File Length(secs): -') # displays a message until audio analyzed
    _time_entry = ttk.Entry(
        _info_frame, width=40, textvariable=_time) # text box
    _time_entry.grid(row=0, column=0, sticky=(E, W, S, N), padx=5)

    _res = StringVar()
    _res.set('Resonant Frequency(Khz): -') # displays a message until audio analyzed
    _res_entry = ttk.Entry(
        _info_frame, width=40, textvariable=_res) # text box
    _res_entry.grid(row=1, column=0, sticky=(E, W, S, N), padx=5)

    _diffRT = StringVar()
    _diffRT.set('RT60 Difference vs .5 seconds(secs): -') # displays a message until audio analyzed
    _diffRT_entry = ttk.Entry(
        _info_frame, width=40, textvariable=_diffRT) # text box
    _diffRT_entry.grid(row=2, column=0, sticky=(E, W, S, N), padx=5)


    _root.mainloop() # listens for events, blocks any code that comes after it

