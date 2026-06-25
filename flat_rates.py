ROUTE_FLAT_RATES = {
    ("Houston", "Rotterdam"): 21.47,
    ("Rotterdam", "New York"): 15.93,
    ("Sikka", "Durban"): 13.53,
    ("Ulsan", "Botany Bay"): 21.0,
    ("Singapore", "Kwinana (Refinery)"): 10.33,
    ("Singapore", "Botany Bay"): 16.84,
    ("Ulsan", "Singapore"): 10.03,
    ("Sikka", "Dar-es-Salaam"): 9.87,
    ("Jubail - Commercial Port", "Dar-es-Salaam"): 11.08
}

def get_flat_rate(ballast_port, laden_port):
    return ROUTE_FLAT_RATES.get((ballast_port, laden_port))