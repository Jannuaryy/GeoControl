import os
import requests
from math import radians, sin, cos, sqrt, atan2

if not os.path.exists('location_images'):
    os.makedirs('location_images')

YANDEX_API_KEY = '8013b162-6b42-4997-9691-77b7074026e0'


def calculate_distance(ll: str, location: str) -> float:
    lat1, lon1 = map(float, ll.split())
    lat2, lon2 = map(float, location.split()[:2])

    geocode_url = f"https://geocode-maps.yandex.ru/1.x/?apikey={YANDEX_API_KEY}&geocode={lon1},{lat1}&format=json"

    response = requests.get(geocode_url)
    data = response.json()

    if 'response' in data and 'GeoObjectCollection' in data['response']:
        if data['response']['GeoObjectCollection']['featureMember']:
            point1 = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            point1_lat, point1_lon = map(float, point1.split())
            distance = haversine(lat1, lon1, point1_lat, point1_lon)
            return distance
    else:
        print("Ошибка в ответе от API:", data)
        return None


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Радиус Земли в километрах
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance_km = R * c
    distance_m = distance_km * 1000

    return distance_m


def get_map_image(ll: str, location: str):
    lat1, lon1 = map(float, ll.split())
    lat2, lon2 = map(float, location.split()[:2])

    map_url = f"https://static-maps.yandex.ru/1.x/?ll={lon1},{lat1}&size=600,450&z=12&l=map&pt={lon1},{lat1},pm2rdl~{lon2},{lat2},pm2rdl"

    response = requests.get(map_url)

    if response.status_code == 200:
        image_path = f'location_images/map_{lat1}_{lon1}.png'
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Карта сохранена как {image_path}")
        return image_path
    else:
        print(f"Ошибка при получении карты: {response.status_code}")
        return None


# Пример использования функций
if __name__ == "__main__":
    ll = "55.729712 37.609731"  # Первая точка
    location = "55.729828 37.609729 67"  # Вторая точка (с точностью)

    distance = calculate_distance(ll, location)
    print(f"Расстояние между точками: {distance} метров")

    map_image_path = get_map_image(ll, location)