# LIBRARY
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import firwin
from collections import deque
import threading
import atexit

# KONFIGURASI
PORT = "COM14"
BAUD = 115200

Fs = 1000
Fc = 20
NUMTAPS = 167

WINDOW_SEC = 5
MAX_DATA = int(Fs * WINDOW_SEC)

 
# KOEFISIEN FIR
b = firwin(
    numtaps=NUMTAPS,
    cutoff=Fc,
    fs=Fs,
    pass_zero=False
)

Nb = len(b)

print("="*50)
print("Realtime FIR High-Pass")
print(f"Fs      : {Fs} Hz")
print(f"Fc      : {Fc} Hz")
print(f"Taps    : {NUMTAPS}")
print("="*50)

 
# IMPLEMENTASI FIR
x_buffer = deque([0.0]*Nb, maxlen=Nb)

def filter_sample(x):

    x_buffer.appendleft(x)

    y = 0.0

    for i in range(Nb):
        y += b[i] * x_buffer[i]

    return y

 
# SERIAL
try:

    ser = serial.Serial(PORT, BAUD, timeout=1)

    print("Connected :", PORT)

except Exception as e:

    print(e)
    exit()

 
# BUFFER DISPLAY
raw_buffer = deque([0.0]*MAX_DATA, maxlen=MAX_DATA)
filt_buffer = deque([0.0]*MAX_DATA, maxlen=MAX_DATA)

buffer_lock = threading.Lock()

stop_event = threading.Event()

sample_count = 0

 
# THREAD SERIAL
def reader_loop():

    global sample_count

    while not stop_event.is_set():

        try:

            line = ser.readline().decode(errors='ignore').strip()

            if line == "":
                continue

            x = float(line)

            y = filter_sample(x)

            with buffer_lock:

                raw_buffer.append(x)
                filt_buffer.append(y)

            sample_count += 1

        except:
            pass

reader_thread = threading.Thread(
    target=reader_loop,
    daemon=True
)

reader_thread.start()

 
# PLOT
 

fig,(ax1,ax2)=plt.subplots(
    2,
    1,
    figsize=(12,7),
    sharex=True
)

line_raw, = ax1.plot(
    list(raw_buffer),
    color='royalblue'
)

line_filt, = ax2.plot(
    list(filt_buffer),
    color='crimson'
)

ax1.set_title("Raw EMG")
ax1.set_ylabel("ADC")
ax1.set_ylim(0,1023)
ax1.grid(True)

ax2.set_title("Realtime FIR High-Pass (167 Taps, 20 Hz)")
ax2.set_xlabel("Sample")
ax2.set_ylabel("Amplitude")
ax2.grid(True)

ax1.set_xlim(0,MAX_DATA)

fig.tight_layout()

 
# UPDATE PLOT
 

def update(frame):

    with buffer_lock:

        raw = list(raw_buffer)
        filt = list(filt_buffer)

    line_raw.set_ydata(raw)
    line_filt.set_ydata(filt)

    line_raw.set_xdata(np.arange(len(raw)))
    line_filt.set_xdata(np.arange(len(filt)))

    ymax = max(20,np.max(np.abs(filt)))

    ax2.set_ylim(-1.2*ymax,1.2*ymax)

    return line_raw,line_filt

ani = animation.FuncAnimation(
    fig,
    update,
    interval=30,
    blit=False,
    cache_frame_data=False
)

 
# CLOSE
 

def cleanup():

    stop_event.set()

    if reader_thread.is_alive():
        reader_thread.join(timeout=2)

    if ser.is_open:
        ser.close()

    print("Total Sample :",sample_count)

atexit.register(cleanup)

fig.canvas.mpl_connect(
    'close_event',
    lambda event: cleanup()
)

print("Realtime FIR Running...")

plt.show()
