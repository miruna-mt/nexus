import json
import random
import math

def generar_punto(base_lat, base_lon, radio_km=50):
    # Genera un punto aleatorio dentro de un radio (km)
    R = 6371
    radio_rad = radio_km / R
    u = random.random()
    v = random.random()
    w = radio_rad * math.sqrt(u)
    t = 2 * math.pi * v
    lat = base_lat + (w * math.cos(t)) * 180 / math.pi
    lon = base_lon + (w * math.sin(t)) * 180 / math.pi
    return lat, lon

# Centro de Murcia
centro_lat = 37.9922
centro_lon = -1.1307

# Generar depósito (ZAL de Murcia)
deposito = {
    "id": 0,
    "nombre": "ZAL de Murcia (Sangonera la Verde)",
    "x": 37.9065,
    "y": -1.2301,
    "ventana_inicio": 0,
    "ventana_fin": 1000
}

# Generar clientes (30 puntos aleatorios con nombres realistas)
pueblos = ["Murcia", "Cartagena", "Lorca", "Caravaca", "Alhama", "Molina", "Cieza", "Yecla", "Jumilla", "Totana"]
calles = ["Polígono Industrial", "Centro Comercial", "Parque Empresarial", "Hospital", "Universidad", "Estación", "Puerto"]

clientes = []
for i in range(30):
    lat, lon = generar_punto(centro_lat, centro_lon, radio_km=70)
    nombre_pueblo = random.choice(pueblos)
    nombre_calle = random.choice(calles)
    clientes.append({
        "id": i+1,
        "nombre": f"{nombre_calle} de {nombre_pueblo}",
        "demanda": random.randint(10, 50),
        "ventana_inicio": 0,
        "ventana_fin": 1000,
        "x": lat,
        "y": lon
    })

data = {
    "vehiculos": [
        {"id": "V1", "capacidad": 300, "costo_km": 1.0},
        {"id": "V2", "capacidad": 300, "costo_km": 1.0},
        {"id": "V3", "capacidad": 300, "costo_km": 1.0},
        {"id": "V4", "capacidad": 300, "costo_km": 1.0}
    ],
    "clientes": clientes,
    "deposito": deposito,
    "distancias": []
}

with open("routing_grande.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Generados {len(clientes)} clientes aleatorios en la Región de Murcia")
print("📁 Archivo guardado como 'routing_grande.json'")