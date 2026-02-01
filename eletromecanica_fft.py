import json
import numpy as np
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
from collections import deque

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "eletromecanica/motor/sensores"

FS = 200             
N = 256               
EIXO = "az"        

ALERTA_G = 200
CRITICO_G = 400

buffer = deque(maxlen=N)

def on_message(client, userdata, msg):
    global buffer

    try:
        data = json.loads(msg.payload.decode())
        acc = data[EIXO]
        buffer.append(acc)

        if len(buffer) == N:
            processar_fft(np.array(buffer))
            buffer.clear()

    except Exception as e:
        print("Erro:", e)

def processar_fft(signal):
    signal = signal - np.mean(signal)

    fft_vals = np.fft.fft(signal)
    fft_mag = np.abs(fft_vals)[:N//2]

    freqs = np.fft.fftfreq(N, 1/FS)[:N//2]

    pico = np.max(fft_mag)
    freq_pico = freqs[np.argmax(fft_mag)]

    status = "NORMAL"
    if pico > CRITICO_G:
        status = "CRÍTICO"
    elif pico > ALERTA_G:
        status = "ALERTA"

    print(f"\n📈 Pico: {pico:.1f} | Frequência: {freq_pico:.2f} Hz | Status: {status}")

    plotar(freqs, fft_mag, freq_pico, status)

def plotar(freqs, mag, freq_pico, status):
    plt.clf()
    plt.plot(freqs, mag)
    plt.title(f"Espectro de Vibração ({status})")
    plt.xlabel("Frequência (Hz)")
    plt.ylabel("Magnitude")
    plt.axvline(freq_pico, linestyle="--")
    plt.grid()
    plt.pause(0.01)

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, PORT)
client.subscribe(TOPIC)

print("📡 Aguardando dados MQTT...")
plt.figure(figsize=(10,5))
client.loop_forever()
