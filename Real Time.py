# ==========================================================
# LIBRARY
# ==========================================================
import serial
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import firwin
from collections import deque
import threading
import atexit

# ==========================================================
# KONFIGURASI
# ==========================================================
PORT = "COM14"
BAUD = 115200

Fs = 1000          # Sampling Rate
Fc = 20            # Cutoff Frequency
NUMTAPS = 167      # FIR Order

WINDOW_SEC = 5
MAX_DATA = int(Fs * WINDOW_SEC)

# ==========================================================
# KOEFISIEN FIR
# ==========================================================
b = firwin(
    numtaps=NUMTAPS,
    cutoff=Fc,
    fs=Fs,
    pass_zero=False
)

Nb = len(b)

print("="*50)
print("Realtime FIR High-Pass FFT")
print(f"Sampling Rate : {Fs} Hz")
print(f"Cutoff        : {Fc} Hz")
print(f"Taps          : {NUMTAPS}")
print("="*50)

# ==========================================================
# IMPLEMENTASI FIR
# ==========================================================
x_buffer = deque([0.0]*Nb, maxlen=Nb)

def filter_sample(x):
    x_buffer.appendleft(x)

    y = 0.0
    for i in range(Nb):
        y += b[i] * x_buffer[i]

    return y

# ==========================================================
# SERIAL
# ==========================================================
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print("Connected :", PORT)

except Exception as e:
    print(e)
    exit()

# ==========================================================
# BUFFER
# ==========================================================
raw_buffer = deque([0.0]*MAX_DATA, maxlen=MAX_DATA)
filt_buffer = deque([0.0]*MAX_DATA, maxlen=MAX_DATA)

buffer_lock = threading.Lock()
stop_event = threading.Event()

sample_count = 0

# ==========================================================
# THREAD SERIAL
# ==========================================================
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

# ==========================================================
# FFT PLOT (2 SUBPLOTS)
# ==========================================================
freq = np.fft.rfftfreq(MAX_DATA, d=1/Fs)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12,8))

line_raw, = ax1.plot(freq,
                     np.zeros(len(freq)),
                     color='royalblue',
                     linewidth=1.5)

ax1.set_title("FFT Sebelum Filter")
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel("Magnitude")
ax1.set_xlim(0, Fs/2)
ax1.grid(True)

line_filt, = ax2.plot(freq,
                      np.zeros(len(freq)),
                      color='crimson',
                      linewidth=1.5)

ax2.set_title("FFT Sesudah Filter")
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude")
ax2.set_xlim(0, Fs/2)
ax2.grid(True)

plt.tight_layout()

# ==========================================================
# UPDATE FFT
# ==========================================================
def update(frame):

    with buffer_lock:
        raw = np.array(raw_buffer)
        filt = np.array(filt_buffer)

    if len(raw) < MAX_DATA:
        return line_raw, line_filt

    # Hilangkan DC Offset
    raw = raw - np.mean(raw)
    filt = filt - np.mean(filt)

    # FFT
    raw_fft = np.abs(np.fft.rfft(raw))
    filt_fft = np.abs(np.fft.rfft(filt))

    line_raw.set_data(freq, raw_fft)
    line_filt.set_data(freq, filt_fft)

    ax1.set_ylim(0, max(np.max(raw_fft), 1) * 1.1)
    ax2.set_ylim(0, max(np.max(filt_fft), 1) * 1.1)

    return line_raw, line_filt

ani = animation.FuncAnimation(
    fig,
    update,
    interval=100,
    blit=False,
    cache_frame_data=False
)

# ==========================================================
# CLEANUP
# ==========================================================
def cleanup():

    stop_event.set()

    if reader_thread.is_alive():
        reader_thread.join(timeout=2)

    if ser.is_open:
        ser.close()

    print("Total Sample :", sample_count)

atexit.register(cleanup)

fig.canvas.mpl_connect(
    'close_event',
    lambda event: cleanup()
)

print("Realtime FFT Running...")

plt.show()