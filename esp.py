# Script ini menghubungkan ESP32 ke WiFi, membaca data dari sensor DHT22, dan mengirimkan data ke Ubidots serta API Flask
# Data dikirim ke Ubidots menggunakan REST API untuk divisualisasikan di dashboard
# Data juga dikirim ke API Flask yang akan menyimpannya ke database MongoDB

import network
import urequests as requests
import time
import ujson
import machine
import dht

SSID = "K1"  
PASSWORD = "+ 62811371409"

SERVER_URL = "http://192.168.1.16:5000/sensor" #API Flask Lokal, di github saya beri nama app.py

DEVICE_ID = "esp32"
TOKEN = "BBUS-9FwX1zNTZA9LkNntqbClujEN8QrkhU"

DHT_PIN = 4

dht_sensor = dht.DHT22(machine.Pin(DHT_PIN))

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        print("Menghubungkan ke WiFi...")
        time.sleep(1)
        timeout -= 1
    if wlan.isconnected():
        print("Terhubung ke WiFi:", wlan.ifconfig())
    else:
        print("Gagal terhubung ke WiFi, cek SSID/PASSWORD!")

def read_dht22():
    try:
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        return temperature, humidity
    except Exception as e:
        print("Error membaca DHT22:", e)
        return None, None

def send_data_to_ubidots(temperature, humidity):
    data = {"temp": temperature, "humidity": humidity}
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    try:
        response = requests.post(url, json=data, headers=headers)
        print("Response Ubidots:", response.text)
        response.close()
    except Exception as e:
        print("Gagal mengirim ke Ubidots:", e)

def send_sensor_data():
    while True:
        temperature, humidity = read_dht22()
        if temperature is not None and humidity is not None:
            send_data_to_ubidots(temperature, humidity)
            try:
                response = requests.post(SERVER_URL, json={"humidity": humidity}, timeout=5)
                if response.status_code == 201:
                    print("Data terkirim ke Flask:", response.json())
                else:
                    print("Server Flask error:", response.text)
                response.close()
            except Exception as e:
                print("Gagal mengirim data ke Flask:", e)
        time.sleep(5)

connect_wifi()
send_sensor_data()
