import time
import requests
import random

# URL Endpoint Backend FastAPI
API_URL = "http://localhost:8000/api/telemetry"

# API Key yang sesuai dengan backend
HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": "zenith_secret_key_2026"
}

def simulate_device():
    print("🚀 Memulai simulasi pengiriman data telemetri ESP32...")
    print("Tekan Ctrl+C untuk menghentikan simulator.\n")
    
    device_id = "ESP32_NODE_01"
    
    try:
        while True:
            # Simulasi data sensor industri acak
            pressure = round(random.uniform(4.0, 5.5), 2)
            rpm = random.randint(110, 140)
            status = "NORMAL" if pressure < 5.2 else "WARNING"
            
            payload = {
                "device_id": device_id,
                "pressure_bar": pressure,
                "conveyor_rpm": rpm,
                "status": status
            }
            
            # Kirim POST request ke FastAPI
            response = requests.post(API_URL, json=payload, headers=HEADERS)
            
            if response.status_code == 200:
                print(f"[SUCCESS] Terkirim -> Pressure: {pressure} bar | RPM: {rpm} | Status: {status}")
            else:
                print(f"[FAILED] Gagal mengirim data. Status Code: {response.status_code} | Respon: {response.text}")
            
            # Jeda 3 detik sebelum pengiriman berikutnya
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulasi dihentikan oleh pengguna.")

if __name__ == "__main__":
    simulate_device()
