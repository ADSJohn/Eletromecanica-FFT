import json, numpy as np
import paho.mqtt.client as mqtt
from collections import deque

BROKER = "broker.hivemq.com"
RAW = "eletromecanica/motor/raw"
VIB = "eletromecanica/motor/fft/vibracao"
DES = "eletromecanica/motor/fft/desbalanceamento"
ALERT = "eletromecanica/motor/alerta"

N = 256
buf_vib = deque(maxlen=N)
buf_des = deque(maxlen=N)

RMS_VIB_CRIT = 4.5
RMS_DES_CRIT = 3.0

def rms(x):
    return np.sqrt(np.mean(np.square(x)))

def publish_fft(client, buf, topic, tipo):
    s = np.array(buf) - np.mean(buf)
    fft = np.abs(np.fft.rfft(s))
    r = rms(fft)

    client.publish(topic, json.dumps({
        "fft": fft.tolist(),
        "rms": float(r)
    }))

    if (tipo == "vib" and r > RMS_VIB_CRIT) or \
       (tipo == "des" and r > RMS_DES_CRIT):
        client.publish(ALERT, json.dumps({
            "tipo": tipo,
            "rms": float(r),
            "mensagem": "ANOMALIA CRÍTICA DETECTADA"
        }))

def on_message(client, userdata, msg):
    d = json.loads(msg.payload)
    buf_vib.append(d["az"])
    buf_des.append(d["mx"])

    if len(buf_vib) == N:
        publish_fft(client, buf_vib, VIB, "vib")
        publish_fft(client, buf_des, DES, "des")
        buf_vib.clear()
        buf_des.clear()

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883)
client.subscribe(RAW)

print("📡 FFT + Diagnóstico ativo")
client.loop_forever()
