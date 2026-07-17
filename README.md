# FIR High-Pass Hamming

Repository ini berisi implementasi dan analisis FIR high-pass filter untuk sinyal EMG, khususnya sinyal otot Tibialis Anterior. Proyek ini mencakup perancangan filter dengan metode window Hamming, evaluasi di domain waktu dan frekuensi, validasi terhadap `scipy`, serta skrip realtime untuk pembacaan data dari serial.

## Isi Repository

- `code_FIR.ipynb` - notebook utama untuk perancangan filter, visualisasi, dan validasi.
- `code_live_fir.py` - skrip Python untuk filtering realtime dari port serial.
- `Data_EMG/` - kumpulan data EMG dalam format CSV.
- `inoriltime/inoriltime.ino` - sketch Arduino/ESP untuk sumber data serial.

## Ringkasan Metode

Filter yang digunakan adalah FIR high-pass dengan parameter utama:

- Sampling rate `Fs = 1000 Hz`
- Cutoff frequency `Fc = 20 Hz`
- Jumlah koefisien `numtaps = 167`
- Window `Hamming`

Notebook membahas:

1. Visualisasi sinyal EMG mentah.
2. Analisis spektrum frekuensi dengan FFT.
3. Desain koefisien FIR secara manual dengan window method.
4. Perbandingan hasil manual dengan `scipy.signal.firwin`.
5. Validasi hasil filtering dengan `scipy.signal.lfilter`.

## Kebutuhan

Pastikan Python sudah terpasang dan instal paket berikut:

- `numpy`
- `pandas`
- `matplotlib`
- `scipy`
- `pyserial` untuk skrip realtime

Jika ingin menjalankan notebook, gunakan juga Jupyter atau VS Code Notebook.

Contoh instalasi:

```bash
pip install numpy pandas matplotlib scipy pyserial jupyter
```

## Cara Menjalankan Notebook

1. Buka `code_FIR.ipynb`.
2. Jalankan sel secara berurutan dari atas ke bawah.
3. Jika diperlukan, sesuaikan path CSV pada bagian pembacaan data EMG. Notebook ini memakai file dari folder `Data_EMG/`.

Catatan: pada notebook terdapat path absolut untuk salah satu contoh file CSV. Jika repo dipindah ke lokasi lain, ubah path tersebut agar sesuai dengan lokasi workspace saat ini.

## Cara Menjalankan Realtime

1. Pastikan perangkat pengirim data sudah aktif dan mengirimkan nilai EMG lewat serial.
2. Sesuaikan parameter berikut di `code_live_fir.py` jika perlu:
   - `PORT` untuk port serial, misalnya `COM14`
   - `BAUD` sesuai baud rate perangkat
3. Jalankan skrip:

```bash
python code_live_fir.py
```

Skrip ini membaca data serial, menerapkan FIR high-pass secara streaming, lalu menampilkan sinyal raw dan hasil filter secara realtime.

## Output yang Diharapkan

- Plot sinyal EMG mentah dan hasil filtering.
- Plot respon frekuensi filter FIR.
- Perbandingan spektrum sebelum dan sesudah filtering.
- Visualisasi realtime sinyal masuk dan hasil filtering.

## Catatan Teknis

- Koefisien filter di notebook dihitung secara manual agar proses desain lebih transparan.
- Skrip realtime menggunakan buffer melingkar dan thread pembaca serial agar visualisasi tetap responsif.
- Jika data serial berhenti masuk, pastikan format data yang dikirim adalah angka per baris.

## Struktur Data

Folder `Data_EMG/` berisi beberapa contoh file CSV hasil akuisisi. Notebook menggunakan salah satu file sebagai contoh input untuk analisis dan validasi filter.

## Lisensi

Belum ada informasi lisensi pada repository ini.
