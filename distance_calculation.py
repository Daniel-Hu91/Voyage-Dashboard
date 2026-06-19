import os
import requests
import urllib3
from dotenv import load_dotenv

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_KEY = os.getenv("ATOBVIAC_API_KEY")
URL = "https://api.atobviac.com/v1/Distance"

route_options = {
    "TC17 Sikka → Dar-es-Salaam": ("Sikka", "Dar-es-Salaam"),
    "TC7 Singapore → Kwinana (Refinery)": ("Singapore", "Kwinana (Refinery)"),
    "TC22 Ulsan → Botany Bay": ("Ulsan", "Botany Bay"),
    "TC11 Ulsan → Singapore": ("Ulsan", "Singapore"),
}

def get_route_options():
    return route_options

def get_ports():
    ports = set()

    for load_port, discharge_port in route_options.values():
        ports.add(load_port)
        ports.add(discharge_port)

    return sorted(list(ports))

def get_route_ports(route_name):
    if route_name not in route_options:
        raise ValueError(f"Unknown route: {route_name}")

    return route_options[route_name]

def get_distance(departure, arrival):
    if not API_KEY:
        raise ValueError("ATOBVIAC_API_KEY is not set.")

    params = {
        "port": [departure, arrival],
        "api_key": API_KEY
    }

    response = requests.get(URL, params=params, verify=False, timeout=30)
    response.raise_for_status()

    distance_text = response.text.strip()
    cleaned_distance = distance_text.replace(",", "").replace("nm", "").strip()

    try:
        return float(cleaned_distance)
    except ValueError:
        raise ValueError(f"Unexpected distance response: {distance_text}")

def get_distance_for_route(route_name):
    load_port, discharge_port = get_route_ports(route_name)
    distance_nm = get_distance(load_port, discharge_port)

    return {
        "route_name": route_name,
        "departure": load_port,
        "arrival": discharge_port,
        "distance_nm": distance_nm
    }