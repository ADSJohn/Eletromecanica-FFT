import json, numpy as np
import paho.mqtt.client as mqtt
from collections import deque

BROKER = "broker.hivemq.com"

RAW = "eletromecanica/motor/raw"
VIB = "eletromecanica/motor/fft/vibracao"
DES = "eletromecanica/motor/fft/desbalanceamento"

N = 256
buf_vib = deque(maxlen=N)
buf_des = deque(maxlen=N)

def on_message(client, userdata, msg):
    d = json.loads(msg.payload)
    buf_vib.append(d["az"])
    buf_des.append(d["mx"])

    if len(buf_vib) == N:
        publish_fft(client, buf_vib, VIB)
        publish_fft(client, buf_des, DES)
        buf_vib.clear()
        buf_des.clear()

def publish_fft(client, buf, topic):
    s = np.array(buf) - np.mean(buf)
    fft = np.abs(np.fft.rfft(s)).tolist()
    client.publish(topic, json.dumps({"fft": fft}))

client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883)
client.subscribe(RAW)

print("📡 FFT ativa")
client.loop_forever()
