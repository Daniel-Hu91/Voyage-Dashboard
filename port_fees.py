PORT_FEES = {
    "Botany Bay": 70000.0,
    "Dar-es-Salaam": 49000.0,
    "Durban": 29000.0,
    "Houston": 47000.0,
    "Kwinana (Refinery)": 48000.0,
    "New York": 42000.0,
    "Rotterdam": 64000.0,
    "Singapore": 15000.0,
    "Sikka": 30000.0,
    "Ulsan": 21000.0,
}

def get_port_fee(port_name):
    return PORT_FEES.get(port_name, 0.0)