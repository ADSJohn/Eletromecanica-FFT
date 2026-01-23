import time
import numpy as np
from scipy.fft import fft

FS = 1000            
DURACAO = 5          
RPM_BASE = 300       
VARIACAO_RPM = 25    

def gerar_vibracao_mock():

    rpm_atual = RPM_BASE + np.random.uniform(-VARIACAO_RPM, VARIACAO_RPM)
    freq_1x = rpm_atual / 60  

    t = np.linspace(0, DURACAO, FS * DURACAO, endpoint=False)

    signal = 0.8 * np.sin(2 * np.pi * freq_1x * t)

    signal += 0.3 * np.sin(2 * np.pi * 2 * freq_1x * t)

    signal += 0.2 * np.random.randn(len(t))

    return signal, FS, rpm_atual

def analisar_fft(signal, fs):

    N = len(signal)
    NFFT = 4 * N              
    
    yf = np.abs(fft(signal, NFFT))
    freqs = np.fft.fftfreq(NFFT, 1 / fs)

    idx = np.argmax(yf[:NFFT // 2])
    pico_freq = freqs[idx]

    if pico_freq < 10:
        falha = "DESBALANCEAMENTO"
    elif pico_freq < 60:
        falha = "DESALINHAMENTO"
    else:
        falha = "ROLAMENTO"

    return float(round(pico_freq, 2)), falha

def main():
    print("Pressione CTRL+C para parar\n")

    while True:
        signal, fs, rpm = gerar_vibracao_mock()

        pico, falha = analisar_fft(signal, fs)

        print(
            f"RPM: {rpm:6.1f} | "
            f"Pico FFT: {pico:5.2f} Hz | "
            f"Falha: {falha}"
        )

        time.sleep(2)

if __name__ == "__main__":
    main()
