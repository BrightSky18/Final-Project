from tkinter import *
from tkinter import ttk,filedialog,messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.io import wavfile
import scipy.io
import matplotlib.pyplot as plt
import numpy as np
from pydub import AudioSegment
from scipy.signal import butter,filtfilt
# Canvas is intialized here so it's value can later be modified by the functions.
canvas=None
def fetch_audio():
    allowedfiletypes=[('Audio Files','*.mp3;*.wav')]
    ##Still need to convert mp3 files to wav format
    global file_path
    file_path = filedialog.askopenfilename(filetypes=allowedfiletypes)
   ##checks file type. if mp3, convert to wav. if neither, errors

    if file_path.endswith('.wav'):

        _audio.set(file_path)

    elif file_path.endswith('.mp3'):
        # Load the MP3 file
        sound = AudioSegment.from_mp3(file_path)

        # Export as WAV
        sound.export("usable_wav_audio_file.wav", format="wav")
        _audio.set(file_path)
        file_path = "usable_wav_audio_file.wav"

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

#If canvas has a value this function clears it, and it clears the matplotlib plot.
def clear_canvas():
    global canvas
    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None
    plt.clf()

def display_waveform():
    global canvas
    clear_canvas()
    ##above code calls the clear_canvas function in case canvas has any data.
    sample_rate, data = wavfile.read(file_path)
    ##The below if statement checks if the data has a left and right channel, and if does combines them.
    if len(data.shape) == 2:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        data = (left_channel + right_channel) / 2
    else:
        data = data
    t=np.linspace(0,len(data)/sample_rate,len(data), endpoint=False)
    plt.figure()
    plt.plot(t,data,label='Waveform', color='blue')
    plt.title('Waveform')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (dB)')
    plt.grid(True)
    ##matplotlib is used to create the plot
    plt.legend()
    canvas=FigureCanvasTkAgg(plt.gcf(), master=_root)
    canvas.draw()
    canvas.get_tk_widget().grid()
    ##tkinter methods are used to show the graph in the gui.

##Def used for the display RT's functions.
def find_nearest_value(array, value):
    array = np.asarray(array)
    idx=(np.abs(array - value)).argmin()
    return array[idx]

def display_lowRT():
    global canvas
    clear_canvas()
    sample_rate, data=wavfile.read(file_path)
    if len(data.shape)==2:
        left_channel=data[:,0]
        right_channel=data[:,1]
        data=(left_channel+right_channel)/2
    else:
        data=data
    t = np.linspace(0,len(data)/sample_rate,len(data), endpoint=False)
    fft_result=np.fft.fft(data)
    spectrum=np.abs(fft_result)
    ##This code collects the spectrum based on the sound data from the file.
    freqs=np.fft.fftfreq(len(data), d=1/sample_rate)
    freqs=freqs[:len(freqs)//2]
    spectrum=spectrum[:len(spectrum)//2]

    ##Target frequency is set here
    target=250
    nearest_freq=freqs[np.abs(freqs-target).argmin()] ##End of find_Target_Frequency
    target_frequency=nearest_freq
    nyquist=0.5* (sample_rate)
    order=4
    low= (target_frequency-50)/nyquist
    high=(target_frequency+50)/nyquist
    b,a= butter(order, [low,high], btype='band')
    filtered_data=filtfilt(b, a, data)
    data_in_db=10*np.log10(np.abs(filtered_data)+1e-10)
    plt.figure(2)
    plt.plot(t, data_in_db, linewidth=1,alpha=0.7,color='blue')
    plt.title('Low-RT Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (dB)')
    index_of_max=np.argmax(data_in_db)
    value_of_max=data_in_db[index_of_max]
    plt.plot(t[index_of_max],data_in_db[index_of_max], 'go')
    sliced_array=data_in_db[index_of_max:]
    value_of_max_less_5=value_of_max-5
    value_of_max_less_5=find_nearest_value(sliced_array,value_of_max_less_5)
    index_of_max_less_5=np.where(data_in_db == value_of_max_less_5)[0][0]
    plt.plot(t[index_of_max_less_5], data_in_db[index_of_max_less_5], 'yo')
    value_of_max_less_25=value_of_max-25
    value_of_max_less_25=find_nearest_value(sliced_array,value_of_max_less_25)
    index_of_max_less_25=np.where(data_in_db == value_of_max_less_25)[0][0]
    plt.plot(t[index_of_max_less_25], data_in_db[index_of_max_less_25], 'ro')
    rt20=t[index_of_max_less_5]-t[index_of_max_less_25]
    rt60=3*rt20
    ##RT60 is extrapolated from rt20*3
    canvas = FigureCanvasTkAgg(plt.gcf(), master=_root)
    canvas.draw()
    canvas.get_tk_widget().grid()

    ##RT60 information is displayed in the console.
    print(f'The RT60 reverb time at freq {int(target_frequency)}Hz is {round(abs(rt60),2)} seconds')

    ##The absolute value of RT60 subtracted by 0.5 is found, then displayed in the gui.
    RT60Dif=abs(rt60)-0.5
    _diffRT.set(f'{round(abs(RT60Dif),2)} seconds')

    ##The RTReturn functions are modified versions of the display_RT functions that return the frequency,rt60 value, time, and decay curve data for later use in the combined graph function.
def lowRTReturn():
    global canvas
    clear_canvas()
    sample_rate, data = wavfile.read(file_path)
    if len(data.shape) == 2:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        data = (left_channel + right_channel) / 2
    else:
        data = data
    t = np.linspace(0, len(data) / sample_rate, len(data), endpoint=False)
    fft_result = np.fft.fft(data)
    spectrum = np.abs(fft_result)
    freqs = np.fft.fftfreq(len(data), d=1 / sample_rate)
    freqs = freqs[:len(freqs) // 2]
    spectrum = spectrum[:len(spectrum) // 2]

    ##find_Target_frequency
    target = 250
    nearest_freq = freqs[np.abs(freqs - target).argmin()]  ##End of find_Target_Frequency
    target_frequency = nearest_freq
    nyquist = 0.5 * (sample_rate)
    order = 4
    low = (target_frequency - 50) / nyquist
    high = (target_frequency + 50) / nyquist
    b, a = butter(order, [low, high], btype='band')
    filtered_data = filtfilt(b, a, data)
    data_in_db = 10 * np.log10(np.abs(filtered_data) + 1e-10)
    plt.figure(2)
    plt.plot(t, data_in_db, linewidth=1, alpha=0.7, color='blue')
    plt.title('Low-RT Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (dB)')
    index_of_max = np.argmax(data_in_db)
    value_of_max = data_in_db[index_of_max]
    plt.plot(t[index_of_max], data_in_db[index_of_max], 'go')
    sliced_array = data_in_db[index_of_max:]
    value_of_max_less_5 = value_of_max - 5
    value_of_max_less_5 = find_nearest_value(sliced_array, value_of_max_less_5)
    index_of_max_less_5 = np.where(data_in_db == value_of_max_less_5)[0][0]
    plt.plot(t[index_of_max_less_5], data_in_db[index_of_max_less_5], 'yo')
    value_of_max_less_25 = value_of_max - 25
    value_of_max_less_25 = find_nearest_value(sliced_array, value_of_max_less_25)
    index_of_max_less_25 = np.where(data_in_db == value_of_max_less_25)[0][0]
    plt.plot(t[index_of_max_less_25], data_in_db[index_of_max_less_25], 'ro')
    rt20 = t[index_of_max_less_5] - t[index_of_max_less_25]
    rt60 = 3 * rt20
    return {
        "frequency": target_frequency,
        "rt60": abs(rt60),
        "time": t,
        "decay_curve": data_in_db,
    }

def display_midRT():
    '''Implement a function to graph in mid RT60 style. Below is a test command. Delete later'''
    global canvas
    clear_canvas()
    sample_rate, data = wavfile.read(file_path)
    if len(data.shape) == 2:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        data = (left_channel + right_channel) / 2
    else:
        data = data
    t = np.linspace(0, len(data) / sample_rate, len(data), endpoint=False)
    fft_result = np.fft.fft(data)
    spectrum = np.abs(fft_result)
    freqs = np.fft.fftfreq(len(data), d=1 / sample_rate)
    freqs = freqs[:len(freqs) // 2]
    spectrum = spectrum[:len(spectrum) // 2]

    ##find_Target_frequency
    target = 1000
    nearest_freq = freqs[np.abs(freqs - target).argmin()]  ##End of find_Target_Frequency
    target_frequency = nearest_freq
    nyquist = 0.5 * (sample_rate)
    order = 4
    low = (target_frequency - 50) / nyquist
    high = (target_frequency + 50) / nyquist
    b, a = butter(order, [low, high], btype='band')
    filtered_data = filtfilt(b, a, data)
    data_in_db = 10 * np.log10(np.abs(filtered_data) + 1e-10)
    plt.figure(2)
    plt.plot(t, data_in_db, linewidth=1, alpha=0.7, color='blue')
    plt.title('Mid-RT Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (dB)')
    index_of_max = np.argmax(data_in_db)
    value_of_max = data_in_db[index_of_max]
    plt.plot(t[index_of_max], data_in_db[index_of_max], 'go')
    sliced_array = data_in_db[index_of_max:]
    value_of_max_less_5 = value_of_max - 5
    value_of_max_less_5 = find_nearest_value(sliced_array, value_of_max_less_5)
    index_of_max_less_5 = np.where(data_in_db == value_of_max_less_5)[0][0]
    plt.plot(t[index_of_max_less_5], data_in_db[index_of_max_less_5], 'yo')
    value_of_max_less_25 = value_of_max - 25
    value_of_max_less_25 = find_nearest_value(sliced_array, value_of_max_less_25)
    index_of_max_less_25 = np.where(data_in_db == value_of_max_less_25)[0][0]
    plt.plot(t[index_of_max_less_25], data_in_db[index_of_max_less_25], 'ro')
    rt20 = t[index_of_max_less_5] - t[index_of_max_less_25]
    rt60 = 3 * rt20
    canvas = FigureCanvasTkAgg(plt.gcf(), master=_root)
    canvas.draw()
    canvas.get_tk_widget().grid()
    print(f'The RT60 reverb time at freq {int(target_frequency)}Hz is {round(abs(rt60), 2)} seconds')
    RT60Dif = abs(rt60) - 0.5
    _diffRT.set(f'{round(abs(RT60Dif), 2)} seconds')
def midRTReturn():
    global canvas
    clear_canvas()
    sample_rate, data = wavfile.read(file_path)
    if len(data.shape) == 2:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        data = (left_channel + right_channel) / 2
    else:
        data = data
    t = np.linspace(0, len(data) / sample_rate, len(data), endpoint=False)
    fft_result = np.fft.fft(data)
    spectrum = np.abs(fft_result)
    freqs = np.fft.fftfreq(len(data), d=1 / sample_rate)
    freqs = freqs[:len(freqs) // 2]
    spectrum = spectrum[:len(spectrum) // 2]

    ##find_Target_frequency
    target = 1001
    nearest_freq = freqs[np.abs(freqs - target).argmin()]  ##End of find_Target_Frequency
    target_frequency = nearest_freq
    nyquist = 0.5 * (sample_rate)
    order = 4
    low = (target_frequency - 50) / nyquist
    high = (target_frequency + 50) / nyquist
    b, a = butter(order, [low, high], btype='band')
    filtered_data = filtfilt(b, a, data)
    data_in_db = 10 * np.log10(np.abs(filtered_data) + 1e-10)
    plt.figure(2)
    plt.plot(t, data_in_db, linewidth=1, alpha=0.7, color='blue')
    plt.title('Mid-RT Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (dB)')
    index_of_max = np.argmax(data_in_db)
    value_of_max = data_in_db[index_of_max]
    plt.plot(t[index_of_max], data_in_db[index_of_max], 'go')
    sliced_array = data_in_db[index_of_max:]
    value_of_max_less_5 = value_of_max - 5
    value_of_max_less_5 = find_nearest_value(sliced_array, value_of_max_less_5)
    index_of_max_less_5 = np.where(data_in_db == value_of_max_less_5)[0][0]
    plt.plot(t[index_of_max_less_5], data_in_db[index_of_max_less_5], 'yo')
    value_of_max_less_25 = value_of_max - 25
    value_of_max_less_25 = find_nearest_value(sliced_array, value_of_max_less_25)
    index_of_max_less_25 = np.where(data_in_db == value_of_max_less_25)[0][0]
    plt.plot(t[index_of_max_less_25], data_in_db[index_of_max_less_25], 'ro')
    rt20 = t[index_of_max_less_5] - t[index_of_max_less_25]
    rt60 = 3 * rt20

    return {
        "frequency": target_frequency,
        "rt60": abs(rt60),
        "time": t,
        "decay_curve": data_in_db,
    }
def display_highRT():
    global canvas
    clear_canvas()
    sample_rate, data = wavfile.read(file_path)
    if len(data.shape) == 2:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        data = (left_channel + right_channel) / 2
    else:
        data = data
    t = np.linspace(0, len(data) / sample_rate, len(data), endpoint=False)
    fft_result = np.fft.fft(data)
    spectrum = np.abs(fft_result)
    freqs = np.fft.fftfreq(len(data), d=1 / sample_rate)
    freqs = freqs[:len(freqs) // 2]
    spectrum = spectrum[:len(spectrum) // 2]

    ##find_Target_frequency
    target = 10000
    nearest_freq = freqs[np.abs(freqs - target).argmin()]  ##End of find_Target_Frequency
    target_frequency = nearest_freq
    nyquist = 0.5 * (sample_rate)
    order = 4
    low = (target_frequency - 50) / nyquist
    high = (target_frequency + 50) / nyquist
    b, a = butter(order, [low, high], btype='band')
    filtered_data = filtfilt(b, a, data)
    data_in_db = 10 * np.log10(np.abs(filtered_data) + 1e-10)
    plt.figure(2)
    plt.plot(t, data_in_db, linewidth=1, alpha=0.7, color='blue')
    plt.title('High-RT Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (dB)')
    index_of_max = np.argmax(data_in_db)
    value_of_max = data_in_db[index_of_max]
    plt.plot(t[index_of_max], data_in_db[index_of_max], 'go')
    sliced_array = data_in_db[index_of_max:]
    value_of_max_less_5 = value_of_max - 5
    value_of_max_less_5 = find_nearest_value(sliced_array, value_of_max_less_5)
    index_of_max_less_5 = np.where(data_in_db == value_of_max_less_5)[0][0]
    plt.plot(t[index_of_max_less_5], data_in_db[index_of_max_less_5], 'yo')
    value_of_max_less_25 = value_of_max - 25
    value_of_max_less_25 = find_nearest_value(sliced_array, value_of_max_less_25)
    index_of_max_less_25 = np.where(data_in_db == value_of_max_less_25)[0][0]
    plt.plot(t[index_of_max_less_25], data_in_db[index_of_max_less_25], 'ro')
    rt20 = t[index_of_max_less_5] - t[index_of_max_less_25]
    rt60 = 3 * rt20
    canvas = FigureCanvasTkAgg(plt.gcf(), master=_root)
    canvas.draw()
    canvas.get_tk_widget().grid()
    print(f'The RT60 reverb time at freq {int(target_frequency)}Hz is {round(abs(rt60), 2)} seconds')
    RT60Dif = abs(rt60) - 0.5
    _diffRT.set(f'{round(abs(RT60Dif), 2)} seconds')

def highRTReturn():
    global canvas
    clear_canvas()
    sample_rate, data = wavfile.read(file_path)
    if len(data.shape) == 2:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        data = (left_channel + right_channel) / 2
    else:
        data = data
    t = np.linspace(0, len(data) / sample_rate, len(data), endpoint=False)
    fft_result = np.fft.fft(data)
    spectrum = np.abs(fft_result)
    freqs = np.fft.fftfreq(len(data), d=1 / sample_rate)
    freqs = freqs[:len(freqs) // 2]
    spectrum = spectrum[:len(spectrum) // 2]

    ##find_Target_frequency
    target = 10000
    nearest_freq = freqs[np.abs(freqs - target).argmin()]  ##End of find_Target_Frequency
    target_frequency = nearest_freq
    nyquist = 0.5 * (sample_rate)
    order = 4
    low = (target_frequency - 50) / nyquist
    high = (target_frequency + 50) / nyquist
    b, a = butter(order, [low, high], btype='band')
    filtered_data = filtfilt(b, a, data)
    data_in_db = 10 * np.log10(np.abs(filtered_data) + 1e-10)
    plt.figure(2)
    plt.plot(t, data_in_db, linewidth=1, alpha=0.7, color='blue')
    plt.title('High-RT Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (dB)')
    index_of_max = np.argmax(data_in_db)
    value_of_max = data_in_db[index_of_max]
    plt.plot(t[index_of_max], data_in_db[index_of_max], 'go')
    sliced_array = data_in_db[index_of_max:]
    value_of_max_less_5 = value_of_max - 5
    value_of_max_less_5 = find_nearest_value(sliced_array, value_of_max_less_5)
    index_of_max_less_5 = np.where(data_in_db == value_of_max_less_5)[0][0]
    plt.plot(t[index_of_max_less_5], data_in_db[index_of_max_less_5], 'yo')
    value_of_max_less_25 = value_of_max - 25
    value_of_max_less_25 = find_nearest_value(sliced_array, value_of_max_less_25)
    index_of_max_less_25 = np.where(data_in_db == value_of_max_less_25)[0][0]
    plt.plot(t[index_of_max_less_25], data_in_db[index_of_max_less_25], 'ro')
    rt20 = t[index_of_max_less_5] - t[index_of_max_less_25]
    rt60 = 3 * rt20
    return {
        "frequency": target_frequency,
        "rt60": abs(rt60),
        "time": t,
        "decay_curve": data_in_db,
    }

def display_comboRT():

    global canvas
    clear_canvas()
    ##The RT Return functions are called to provide the needed data.
    LowRT=lowRTReturn()
    MidRT=midRTReturn()
    HighRT=highRTReturn()
    #RT60 value is extracted for later use, in finding the difference.
    LowRT60=LowRT['rt60']
    MidRT60=MidRT['rt60']
    HighRT60=HighRT['rt60']
    ##Average RT60 value is obtained
    RT60=(LowRT60+MidRT60+HighRT60)/3

    fig,ax=plt.subplots()
    ##Subplots for each graph is created using the data from the Return Functions.
    ax.plot(LowRT["time"], LowRT["decay_curve"], label=f"Low RT ({LowRT['frequency']} Hz)")
    ax.plot(MidRT["time"], MidRT["decay_curve"], label=f"Mid RT ({MidRT['frequency']} Hz)")
    ax.plot(HighRT["time"], HighRT["decay_curve"], label=f"High RT ({HighRT['frequency']} Hz)")
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Power (dB)')
    ax.set_title('Combined RT60 Decay Curves')
    ax.legend()
    ##Graph is made and then displayed in the gui.
    canvas = FigureCanvasTkAgg(plt.gcf(), master=_root)
    canvas.draw()
    canvas.get_tk_widget().grid()
    print(f"RT60 for Low Frequency: {LowRT['rt60']} s")
    print(f"RT60 for Mid frequency: {MidRT['rt60']} s")
    print(f"RT60 for High Frequency: {HighRT['rt60']} s")
    print(f'Average RT60 is {round(abs(RT60), 2)} seconds')
    ##Information for all graphs is then displayed in the console.
    RT60Dif = (RT60) - 0.5
    _diffRT.set(f'{round(abs(RT60Dif), 2)} seconds')

##Custom display RT60 function that shows the data at a frequency of 150hz.
def display_ultralow():
    global canvas
    clear_canvas()
    sample_rate, data = wavfile.read(file_path)
    if len(data.shape) == 2:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        data = (left_channel + right_channel) / 2
    else:
        data = data
    t = np.linspace(0, len(data) / sample_rate, len(data), endpoint=False)
    fft_result = np.fft.fft(data)
    spectrum = np.abs(fft_result)
    freqs = np.fft.fftfreq(len(data), d=1 / sample_rate)
    freqs = freqs[:len(freqs) // 2]
    spectrum = spectrum[:len(spectrum) // 2]

    ##find_Target_frequency
    target = 150
    nearest_freq = freqs[np.abs(freqs - target).argmin()]  ##End of find_Target_Frequency
    target_frequency = nearest_freq
    nyquist = 0.5 * (sample_rate)
    order = 4
    low = (target_frequency - 50) / nyquist
    high = (target_frequency + 50) / nyquist
    b, a = butter(order, [low, high], btype='band')
    filtered_data = filtfilt(b, a, data)
    data_in_db = 10 * np.log10(np.abs(filtered_data) + 1e-10)
    plt.figure(2)
    plt.plot(t, data_in_db, linewidth=1, alpha=0.7, color='blue')
    plt.title('Ultra-Low RT Signal')
    plt.xlabel('Time (s)')
    plt.ylabel('Power (dB)')
    index_of_max = np.argmax(data_in_db)
    value_of_max = data_in_db[index_of_max]
    plt.plot(t[index_of_max], data_in_db[index_of_max], 'go')
    sliced_array = data_in_db[index_of_max:]
    value_of_max_less_5 = value_of_max - 5
    value_of_max_less_5 = find_nearest_value(sliced_array, value_of_max_less_5)
    index_of_max_less_5 = np.where(data_in_db == value_of_max_less_5)[0][0]
    plt.plot(t[index_of_max_less_5], data_in_db[index_of_max_less_5], 'yo')
    value_of_max_less_25 = value_of_max - 25
    value_of_max_less_25 = find_nearest_value(sliced_array, value_of_max_less_25)
    index_of_max_less_25 = np.where(data_in_db == value_of_max_less_25)[0][0]
    plt.plot(t[index_of_max_less_25], data_in_db[index_of_max_less_25], 'ro')
    rt20 = t[index_of_max_less_5] - t[index_of_max_less_25]
    rt60 = 3 * rt20
    canvas = FigureCanvasTkAgg(plt.gcf(), master=_root)
    canvas.draw()
    canvas.get_tk_widget().grid()
    print(f'The RT60 reverb time at freq {int(target_frequency)}Hz is {round(abs(rt60), 2)} seconds')
    RT60Dif = abs(rt60) - 0.5
    _diffRT.set(f'{round(abs(RT60Dif), 2)} seconds')

##Def that shows the intensity of the data
def display_intensity():
    global canvas
    clear_canvas()
    sample_rate, data = wavfile.read(file_path)
    if len(data.shape) == 2:
        left_channel = data[:, 0]
        right_channel = data[:, 1]
        data = (left_channel + right_channel) / 2
    else:
        data = data
    ##Plot is created using the data from the audio file.
    spectrum, freqs, t, im = plt.specgram(data, Fs=sample_rate, NFFT=1024, cmap=plt.get_cmap('autumn_r'))
    cbar = plt.colorbar(im)
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    cbar.set_label('Intensity (dB)')
    canvas = FigureCanvasTkAgg(plt.gcf(), master=_root)
    canvas.draw()
    canvas.get_tk_widget().grid()
    ##Plot is shown in the gui.


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




#The following are the buttons to display different graphs. Each will require separate implementation functions
# ALL CAPS LINE TO SHOW THE ABOVE IS A HEADING COMMENT. TAKE NOTE.
    _buttons_frame = ttk.LabelFrame(
        _mainframe, text='Select Graph Type', padding='9 0 0 0')
    _buttons_frame.grid(row=1, column=0, sticky=(N, S, E, W))


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

    _ultralow_btn = ttk.Button(
        _buttons_frame, text='ULTRA Low RT60', command=display_ultralow)
    _ultralow_btn.grid(row=6, column=0, sticky=(W), padx=5)

    _intensity_btn = ttk.Button(
        _buttons_frame, text='Intensity', command=display_intensity)
    _intensity_btn.grid(row=7, column=0, sticky=(W), padx=5)

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

