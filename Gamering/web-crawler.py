from flask import Flask, render_template, send_from_directory, send_file, redirect, url_for
import requests
from bs4 import BeautifulSoup
import webbrowser
import random

# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
import time
import os

app = Flask(__name__, static_folder='static')

# epic = https://store.epicgames.com/es-ES/browse?sortBy=releaseDate&sortDir=DESC&priceTier=tierDiscouted&category=Game&count=40&start=0
# Función para obtener el enlace directo a la oferta del juego
def obtener_enlace_oferta(url_detalles):
    response = requests.get(url_detalles)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        juego_container = soup.find('a', class_='search_result_row')
        if juego_container:
            oferta_link = juego_container['href']
            return oferta_link
    return None



# Función para obtener los datos de los juegos desde la página web
def obtener_datos_juegos():
    start_time = time.time()  # Registra el tiempo inicial
    URL = "https://store.steampowered.com/search/?specials=1"
    response = requests.get(URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0
        for container in game_containers:
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                # Realizar una solicitud a la página de oferta para obtener la imagen
                oferta_response = requests.get(oferta_link)
                if oferta_response.status_code == 200:
                    oferta_soup = BeautifulSoup(oferta_response.content, 'html.parser')
                    # Encuentra el contenedor principal que contiene la información del juego en la página de oferta
                    glance_ctn = oferta_soup.find('div', class_='glance_ctn')
                    if glance_ctn:
                        # Encuentra la etiqueta de la imagen del juego dentro del contenedor principal
                        image_tag = glance_ctn.find('img', class_='game_header_image_full')
                        if image_tag:
                            image = image_tag['src']
                            print("Imagen encontrada en la página de oferta:", image)
                        else:
                            # Si no se encuentra la imagen en la página de oferta, utiliza la miniatura de búsqueda
                            image = container.find('div', class_='search_capsule').find('img')['src']
                            print("No se encontró la imagen en la página de oferta. Se usará la miniatura de búsqueda.")
                    else:
                        # Si no se encuentra el contenedor principal en la página de oferta, utiliza la miniatura de búsqueda
                        image = container.find('div', class_='search_capsule').find('img')['src']
                        print("No se encontró el contenedor principal en la página de oferta. Se usará la miniatura de búsqueda.")
                else:
                    print("Error al obtener los datos de la página de oferta:", oferta_response.status_code)
                    continue  # Saltar al siguiente contenedor si no se puede obtener la página de oferta
            else:
                # Si no hay un enlace de oferta, usa la miniatura de búsqueda
                image = container.find('div', class_='search_capsule').find('img')['src']
                print("No se encontró un enlace de oferta. Se usará la miniatura de búsqueda.")
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            
            category_element = container.find('div', class_='glance_ctn_responsive_right')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            juegos_precios.append({
                "nombre": title, 
                "precio": price, 
                "imagen": image, 
                "url_oferta": oferta_link or detalles_link,  # Usamos el enlace de oferta si está disponible, de lo contrario, el enlace de detalles
                "categorias": category, 
                "plataforma": ['steam']
            })
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        end_time = time.time()  # Registra el tiempo final
        print("Tiempo de carga:", end_time - start_time, "segundos")  # Calcula y muestra el tiempo de carga
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
    # url_aventura = 'https://store.steampowered.com/category/adventure/?tab=2'

def obtener_datos_gog():
    gog = 'https://www.gog.com/en/games?priceRange=0,19'
    response = requests.get(gog)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Aventura"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []

# Llamada a la función y muestra de los datos obtenidos
ofertas_gog = obtener_datos_gog()
# Función para obtener los datos de los juegos de la categoría "Mundo abierto"
def obtener_datos_Aventura():
    url_aventura = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=21&specials=1&ndl=1'
    response = requests.get(url_aventura)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0
        for container in game_containers:
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                # Realizar una solicitud a la página de oferta para obtener la imagen
                oferta_response = requests.get(oferta_link)
                if oferta_response.status_code == 200:
                    oferta_soup = BeautifulSoup(oferta_response.content, 'html.parser')
                    # Encuentra la etiqueta de la imagen del juego en la página de oferta
                    image_tag = oferta_soup.find('img', class_='game_header_image_full')
                    if image_tag:
                        image = image_tag['src']
                    else:
                        # Si no se encuentra la imagen en la página de oferta, utiliza la miniatura de búsqueda
                        image = container.find('div', class_='search_capsule').find('img')['src']
                else:
                    print("Error al obtener los datos de la página de oferta:", oferta_response.status_code)
                    continue  # Saltar al siguiente contenedor si no se puede obtener la página de oferta
            else:
                # Si no hay un enlace de oferta, usa la miniatura de búsqueda
                image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            
            category_element = container.find('div', class_='glance_ctn_responsive_right')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            juegos_precios.append({
                "nombre": title, 
                "precio": price, 
                "imagen": image, 
                "url_oferta": oferta_link or detalles_link,  # Usamos el enlace de oferta si está disponible, de lo contrario, el enlace de detalles
                "categorias": category, 
                "plataforma": ['steam']
            })
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []

def obtener_datos_Aventura_gog():
    gog_aventura = 'https://www.gog.com/en/games/adventure'
    response = requests.get(gog_aventura)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Aventura"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_aventura_gog = obtener_datos_Aventura_gog()
# for oferta in ofertas_aventura_gog:

#     print(f"Nombre: {oferta['nombre']}")
#     print(f"Enlace de oferta: {oferta['url_oferta']}")
#     print(f"URL de la imagen: {oferta['imagen']}")
#     print()
# for oferta in ofertas_aventura_gog:
#     # print("Precio:", oferta["precio"])
#     print("Imagen:", oferta["imagen"])
    # print("URL de la oferta:", oferta["url_oferta"])
    # print("Categorías:", oferta["categorias"])
    # print("\n")
def obtener_datos_Accion():
    start_time = time.time()  # Registra el tiempo inicial
    url_aventura = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=19&specials=1&ndl=1'
    response = requests.get(url_aventura)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0
        for container in game_containers:
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                # Realizar una solicitud a la página de oferta para obtener la imagen
                oferta_response = requests.get(oferta_link)
                if oferta_response.status_code == 200:
                    oferta_soup = BeautifulSoup(oferta_response.content, 'html.parser')
                    # Encuentra la etiqueta de la imagen del juego en la página de oferta
                    image_tag = oferta_soup.find('img', class_='game_header_image_full')
                    if image_tag:
                        image = image_tag['src']
                    else:
                        # Si no se encuentra la imagen en la página de oferta, utiliza la miniatura de búsqueda
                        image = container.find('div', class_='search_capsule').find('img')['src']
                else:
                    print("Error al obtener los datos de la página de oferta:", oferta_response.status_code)
                    continue  # Saltar al siguiente contenedor si no se puede obtener la página de oferta
            else:
                # Si no hay un enlace de oferta, usa la miniatura de búsqueda
                image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            
            category_element = container.find('div', class_='glance_ctn_responsive_right')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            juegos_precios.append({
                "nombre": title, 
                "precio": price, 
                "imagen": image, 
                "url_oferta": oferta_link or detalles_link,  # Usamos el enlace de oferta si está disponible, de lo contrario, el enlace de detalles
                "categorias": category, 
                "plataforma": ['steam']
            })
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        end_time = time.time()  # Registra el tiempo final
        print("Tiempo de carga:", end_time - start_time, "segundos")  # Calcula y muestra el tiempo de carga
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Accion_gog():
    gog_accion = 'https://www.gog.com/en/games?tags=action&priceRange=0,19'
    response = requests.get(gog_accion)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Action"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_accion_gog = obtener_datos_Accion_gog()
    
def obtener_datos_Indie():
    start_time = time.time()
    url_indie = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=492&specials=1&ndl=1'
    response = requests.get(url_indie)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0
        for container in game_containers:
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                # Realizar una solicitud a la página de oferta para obtener la imagen
                oferta_response = requests.get(oferta_link)
                if oferta_response.status_code == 200:
                    oferta_soup = BeautifulSoup(oferta_response.content, 'html.parser')
                    # Encuentra la etiqueta de la imagen del juego en la página de oferta
                    image_tag = oferta_soup.find('img', class_='game_header_image_full')
                    if image_tag:
                        image = image_tag['src']
                    else:
                        # Si no se encuentra la imagen en la página de oferta, utiliza la miniatura de búsqueda
                        image = container.find('div', class_='search_capsule').find('img')['src']
                else:
                    print("Error al obtener los datos de la página de oferta:", oferta_response.status_code)
                    continue  # Saltar al siguiente contenedor si no se puede obtener la página de oferta
            else:
                # Si no hay un enlace de oferta, usa la miniatura de búsqueda
                image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            
            category_element = container.find('div', class_='glance_ctn_responsive_right')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            juegos_precios.append({
                "nombre": title, 
                "precio": price, 
                "imagen": image, 
                "url_oferta": oferta_link or detalles_link,  # Usamos el enlace de oferta si está disponible, de lo contrario, el enlace de detalles
                "categorias": category, 
                "plataforma": ['steam']
            })
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Indie_gog():
    gog_indie = 'https://www.gog.com/en/games?tags=indie&languages=es&discounted=true'
    response = requests.get(gog_indie)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Indie"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_indie_gog = obtener_datos_Indie_gog()

def obtener_datos_Strategy():
    url_strategy = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=9&specials=1&ndl=1'
    response = requests.get(url_strategy)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0
        for container in game_containers:
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                # Realizar una solicitud a la página de oferta para obtener la imagen
                oferta_response = requests.get(oferta_link)
                if oferta_response.status_code == 200:
                    oferta_soup = BeautifulSoup(oferta_response.content, 'html.parser')
                    # Encuentra la etiqueta de la imagen del juego en la página de oferta
                    image_tag = oferta_soup.find('img', class_='game_header_image_full')
                    if image_tag:
                        image = image_tag['src']
                    else:
                        # Si no se encuentra la imagen en la página de oferta, utiliza la miniatura de búsqueda
                        image = container.find('div', class_='search_capsule').find('img')['src']
                else:
                    print("Error al obtener los datos de la página de oferta:", oferta_response.status_code)
                    continue  # Saltar al siguiente contenedor si no se puede obtener la página de oferta
            else:
                # Si no hay un enlace de oferta, usa la miniatura de búsqueda
                image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            
            category_element = container.find('div', class_='glance_ctn_responsive_right')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            juegos_precios.append({
                "nombre": title, 
                "precio": price, 
                "imagen": image, 
                "url_oferta": oferta_link or detalles_link,  # Usamos el enlace de oferta si está disponible, de lo contrario, el enlace de detalles
                "categorias": category, 
                "plataforma": ['steam']
            })
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []

def obtener_datos_Strategy_gog():
    gog_estrategia = 'https://www.gog.com/en/games/Strategy'
    response = requests.get(gog_estrategia)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Strategy"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_Strategy_gog = obtener_datos_Strategy_gog()

def obtener_datos_plataformer():
    url_plataformer = 'https://store.steampowered.com/search/?tags=1625&specials=1&ndl=1'
    response = requests.get(url_plataformer)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0
        for container in game_containers:
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                # Realizar una solicitud a la página de oferta para obtener la imagen
                oferta_response = requests.get(oferta_link)
                if oferta_response.status_code == 200:
                    oferta_soup = BeautifulSoup(oferta_response.content, 'html.parser')
                    # Encuentra la etiqueta de la imagen del juego en la página de oferta
                    image_tag = oferta_soup.find('img', class_='game_header_image_full')
                    if image_tag:
                        image = image_tag['src']
                    else:
                        # Si no se encuentra la imagen en la página de oferta, utiliza la miniatura de búsqueda
                        image = container.find('div', class_='search_capsule').find('img')['src']
                else:
                    print("Error al obtener los datos de la página de oferta:", oferta_response.status_code)
                    continue  # Saltar al siguiente contenedor si no se puede obtener la página de oferta
            else:
                # Si no hay un enlace de oferta, usa la miniatura de búsqueda
                image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            
            category_element = container.find('div', class_='glance_ctn_responsive_right')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            juegos_precios.append({
                "nombre": title, 
                "precio": price, 
                "imagen": image, 
                "url_oferta": oferta_link or detalles_link,  # Usamos el enlace de oferta si está disponible, de lo contrario, el enlace de detalles
                "categorias": category, 
                "plataforma": ['steam']
            })
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []

def obtener_datos_Plataformer_gog():
    gog_plataforma = 'https://www.gog.com/en/games?tags=platformer'
    response = requests.get(gog_plataforma)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Plataformer"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_plataforma_gog = obtener_datos_Plataformer_gog()

def obtener_datos_Shooter():
    url_shooter = 'https://store.steampowered.com/search/?tags=1625&specials=1&ndl=1'
    response = requests.get(url_shooter)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0
        for container in game_containers:
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                # Realizar una solicitud a la página de oferta para obtener la imagen
                oferta_response = requests.get(oferta_link)
                if oferta_response.status_code == 200:
                    oferta_soup = BeautifulSoup(oferta_response.content, 'html.parser')
                    # Encuentra la etiqueta de la imagen del juego en la página de oferta
                    image_tag = oferta_soup.find('img', class_='game_header_image_full')
                    if image_tag:
                        image = image_tag['src']
                    else:
                        # Si no se encuentra la imagen en la página de oferta, utiliza la miniatura de búsqueda
                        image = container.find('div', class_='search_capsule').find('img')['src']
                else:
                    print("Error al obtener los datos de la página de oferta:", oferta_response.status_code)
                    continue  # Saltar al siguiente contenedor si no se puede obtener la página de oferta
            else:
                # Si no hay un enlace de oferta, usa la miniatura de búsqueda
                image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            
            category_element = container.find('div', class_='glance_ctn_responsive_right')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            juegos_precios.append({
                "nombre": title, 
                "precio": price, 
                "imagen": image, 
                "url_oferta": oferta_link or detalles_link,  # Usamos el enlace de oferta si está disponible, de lo contrario, el enlace de detalles
                "categorias": category, 
                "plataforma": ['steam']
            })
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Shooter_gog():
    gog_shooter = 'https://www.gog.com/en/games?genres=shooter&tags=platformer'
    response = requests.get(gog_shooter)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Shooter"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_shooter_gog = obtener_datos_Shooter_gog()   

def obtener_datos_Simulation():
    url_simulacion = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=599&specials=1&ndl=1'
    response = requests.get(url_simulacion)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0
        for container in game_containers:
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                # Realizar una solicitud a la página de oferta para obtener la imagen
                oferta_response = requests.get(oferta_link)
                if oferta_response.status_code == 200:
                    oferta_soup = BeautifulSoup(oferta_response.content, 'html.parser')
                    # Encuentra la etiqueta de la imagen del juego en la página de oferta
                    image_tag = oferta_soup.find('img', class_='game_header_image_full')
                    if image_tag:
                        image = image_tag['src']
                    else:
                        # Si no se encuentra la imagen en la página de oferta, utiliza la miniatura de búsqueda
                        image = container.find('div', class_='search_capsule').find('img')['src']
                else:
                    print("Error al obtener los datos de la página de oferta:", oferta_response.status_code)
                    continue  # Saltar al siguiente contenedor si no se puede obtener la página de oferta
            else:
                # Si no hay un enlace de oferta, usa la miniatura de búsqueda
                image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            
            category_element = container.find('div', class_='glance_ctn_responsive_right')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            juegos_precios.append({
                "nombre": title, 
                "precio": price, 
                "imagen": image, 
                "url_oferta": oferta_link or detalles_link,  # Usamos el enlace de oferta si está disponible, de lo contrario, el enlace de detalles
                "categorias": category, 
                "plataforma": ['steam']
            })
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Simulation_gog():
    gog_shooter = 'https://www.gog.com/en/games?genres=simulation'
    response = requests.get(gog_shooter)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Simulacion"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_simulation_gog = obtener_datos_Simulation_gog()   

def obtener_datos_Fight():
    url_fight = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=3993&specials=1&ndl=1'
    response = requests.get(url_fight)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0  # Variable para contar juegos recolectados
        for container in game_containers:
            image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                url_oferta = oferta_link
            else:
                url_oferta = detalles_link  # Usamos el enlace de los detalles si no hay oferta
            category_element = container.find('div', class_='tab_item_top_tags')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            # Agregar el juego a la lista de juegos y precios
            juegos_precios.append({"nombre": title, "precio": price, "imagen": image, "url_oferta": url_oferta, "categorias": category, "plataforma": ['steam']})
            
            # Incrementar el contador de juegos recolectados
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Fight_gog():
    gog_fight = 'https://www.gog.com/en/games?tags=fighting&priceRange=0,30'
    response = requests.get(gog_fight)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Pelea"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_figth_gog = obtener_datos_Fight_gog()   

def obtener_datos_Family():
    url_fight = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=5350&specials=1&ndl=1'
    response = requests.get(url_fight)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0  # Variable para contar juegos recolectados
        for container in game_containers:
            image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                url_oferta = oferta_link
            else:
                url_oferta = detalles_link  # Usamos el enlace de los detalles si no hay oferta
            category_element = container.find('div', class_='tab_item_top_tags')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            # Agregar el juego a la lista de juegos y precios
            juegos_precios.append({"nombre": title, "precio": price, "imagen": image, "url_oferta": url_oferta, "categorias": category, "plataforma": ['steam']})
            
            # Incrementar el contador de juegos recolectados
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Family_gog():
    gog_family = 'https://www.gog.com/en/games?tags=family-friendly&priceRange=0,5'
    response = requests.get(gog_family)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Familia"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_family_gog = obtener_datos_Family_gog() 

def obtener_datos_puzle():
    url_puzle = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=1664&specials=1&ndl=1'
    response = requests.get(url_puzle)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0  # Variable para contar juegos recolectados
        for container in game_containers:
            image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                url_oferta = oferta_link
            else:
                url_oferta = detalles_link  # Usamos el enlace de los detalles si no hay oferta
            category_element = container.find('div', class_='tab_item_top_tags')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            # Agregar el juego a la lista de juegos y precios
            juegos_precios.append({"nombre": title, "precio": price, "imagen": image, "url_oferta": url_oferta, "categorias": category, "plataforma": ['steam']})
            
            # Incrementar el contador de juegos recolectados
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_puzle_gog():
    gog_family = 'https://www.gog.com/en/games?tags=puzzle'
    response = requests.get(gog_family)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "puzle"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_family_gog = obtener_datos_Family_gog()  

def obtener_datos_Arcade():
    url_arcade = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=1773&specials=1&ndl=1'
    response = requests.get(url_arcade)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0  # Variable para contar juegos recolectados
        for container in game_containers:
            image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                url_oferta = oferta_link
            else:
                url_oferta = detalles_link  # Usamos el enlace de los detalles si no hay oferta
            category_element = container.find('div', class_='tab_item_top_tags')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            # Agregar el juego a la lista de juegos y precios
            juegos_precios.append({"nombre": title, "precio": price, "imagen": image, "url_oferta": url_oferta, "categorias": category, "plataforma": ['steam']})
            
            # Incrementar el contador de juegos recolectados
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Arcade_gog():
    gog_arcade = 'https://www.gog.com/en/games?tags=arcade'
    response = requests.get(gog_arcade)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Arcade"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_arcade_gog = obtener_datos_Arcade_gog() 

def obtener_datos_Casual():
    url_casual = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=597&specials=1&ndl=1'
    response = requests.get(url_casual)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0  # Variable para contar juegos recolectados
        for container in game_containers:
            image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                url_oferta = oferta_link
            else:
                url_oferta = detalles_link  # Usamos el enlace de los detalles si no hay oferta
            category_element = container.find('div', class_='tab_item_top_tags')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            # Agregar el juego a la lista de juegos y precios
            juegos_precios.append({"nombre": title, "precio": price, "imagen": image, "url_oferta": url_oferta, "categorias": category, "plataforma": ['steam']})
            
            # Incrementar el contador de juegos recolectados
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Casual_gog():
    gog_arcade = 'https://www.gog.com/en/games?tags=casual&priceRange=0,5'
    response = requests.get(gog_arcade)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Casual"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_casual_gog = obtener_datos_Casual_gog() 

def obtener_datos_Sport():
    url_sport = 'https://store.steampowered.com/search/?supportedlang=spanish&tags=701&specials=1&ndl=1'
    response = requests.get(url_sport)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0  # Variable para contar juegos recolectados
        for container in game_containers:
            image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                url_oferta = oferta_link
            else:
                url_oferta = detalles_link  # Usamos el enlace de los detalles si no hay oferta
            category_element = container.find('div', class_='tab_item_top_tags')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            # Agregar el juego a la lista de juegos y precios
            juegos_precios.append({"nombre": title, "precio": price, "imagen": image, "url_oferta": url_oferta, "categorias": category, "plataforma": ['steam']})
            
            # Incrementar el contador de juegos recolectados
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Sport_gog():
    gog_arcade = 'https://www.gog.com/en/games?genres=sports&discounted=true'
    response = requests.get(gog_arcade)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Sport"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_casual_gog = obtener_datos_Casual_gog()

def obtener_datos_Cards():
    url_card = 'https://store.steampowered.com/search/?sort_by=_ASC&supportedlang=spanish&tags=1666&specials=1'
    response = requests.get(url_card)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='search_result_row')
        juegos_precios = []
        count = 0  # Variable para contar juegos recolectados
        for container in game_containers:
            image = container.find('div', class_='search_capsule').find('img')['src']
            title = container.find('span', class_='title').text.strip()
            price_container = container.find('div', class_='discount_final_price')
            if price_container:
                price = price_container.text.strip()
            else:
                price = "Precio no disponible"
            detalles_link = container['href']
            # Obtener el enlace de la oferta del juego
            oferta_link = obtener_enlace_oferta(detalles_link)
            # Si hay un enlace de oferta, lo usamos directamente
            if oferta_link:
                url_oferta = oferta_link
            else:
                url_oferta = detalles_link  # Usamos el enlace de los detalles si no hay oferta
            category_element = container.find('div', class_='tab_item_top_tags')
            category = category_element.text.strip() if category_element else "Categoría desconocida"

            # Agregar el juego a la lista de juegos y precios
            juegos_precios.append({"nombre": title, "precio": price, "imagen": image, "url_oferta": url_oferta, "categorias": category, "plataforma": ['steam']})
            
            # Incrementar el contador de juegos recolectados
            count += 1
            # Verificar si se han recolectado 10 juegos
            if count >= 10:
                break
        
        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
def obtener_datos_Card_gog():
    gog_cartas = 'https://www.gog.com/en/games?tags=card-game&languages=es&discounted=true'
    response = requests.get(gog_cartas)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        game_containers = soup.find_all('a', class_='product-tile')

        juegos_precios = []
        count = 0

        for container in game_containers:
            try:
                # Obtener el enlace de la oferta del juego
                oferta_link = container['href']

                # Obtener la imagen del juego
                image_container = container.find('store-picture', class_='ng-star-inserted')
                source_tag = image_container.find('source')
                image_url = source_tag['srcset'] if source_tag else "URL de imagen predeterminada"

                # Obtener el nombre del juego
                name_element = container.find('span', class_='ng-star-inserted')
                name = name_element.text.strip() if name_element else "Nombre no disponible"

                # Obtener el precio del juego
                price_element = container.find('span', class_='final-value ng-star-inserted')
                price_value = price_element.text.strip() if price_element else "Precio no disponible"

                # Definir la categoría
                category = "Card"

                # Guardar los datos del juego en la lista de juegos_precios
                juegos_precios.append({
                    "nombre": name,
                    "precio": price_value,
                    "imagen": image_url,
                    "url_oferta": oferta_link,
                    "categorias": category,
                    "plataforma": ['gog']  # Agregamos la plataforma como una lista

                })

                # Incrementar el contador de juegos recolectados
                count += 1
                # Verificar si se han recolectado 10 juegos
                if count >= 10:
                    break
                
            except Exception as e:
                print("Error al extraer datos:", e)

        return juegos_precios
    else:
        print("Error al obtener los datos de la página:", response.status_code)
        return []
# Llamada a la función y muestra de los datos obtenidos
ofertas_card_gog = obtener_datos_Card_gog() 

# Ruta principal que muestra la lista de juegos
@app.route('/')
def lista_juegos():
    juegos_precios = obtener_datos_juegos() + obtener_datos_gog()
    return render_template('index.html', juegos=juegos_precios)

# enlaces a categorias
@app.route('/aventura')
def juegos_aventura():
    # datos_steam = obtener_datos_Aventura()
    datos_epic = obtener_datos_Aventura_gog() + obtener_datos_Aventura()
    todos_los_juegos =  datos_epic
    return render_template('aventura.html', juegos=todos_los_juegos)

@app.route('/accion')
def juegos_accion():
    juegos_precios = obtener_datos_Accion() + obtener_datos_Accion_gog()
    return render_template('accion.html', juegos=juegos_precios)



@app.route('/indie')
def juegos_indie():
    juegos_precios = obtener_datos_Indie() + obtener_datos_Indie_gog()
    return render_template('indie.html', juegos=juegos_precios)

@app.route('/strategia')
def juegos_strategia():
    juegos_precios = obtener_datos_Strategy() + obtener_datos_Strategy_gog()
    return render_template('strategia.html', juegos=juegos_precios)

@app.route('/plataforma')
def juegos_plataforma():
    juegos_precios = obtener_datos_plataformer() + obtener_datos_Plataformer_gog()
    return render_template('plataforma.html', juegos=juegos_precios)

@app.route('/shooter')
def juegos_disparos():
    juegos_precios = obtener_datos_Shooter() + obtener_datos_Shooter_gog()
    return render_template('plataforma.html', juegos=juegos_precios)

@app.route('/simulacion')
def juegos_simulacion():
    juegos_precios = obtener_datos_Simulation() + obtener_datos_Simulation_gog()
    return render_template('plataforma.html', juegos=juegos_precios)

@app.route('/pelea')
def juegos_pelea():
    juegos_precios = obtener_datos_Fight() + obtener_datos_Fight_gog()
    return render_template('pelea.html', juegos=juegos_precios)

@app.route('/familia')
def juegos_familia():
    juegos_precios = obtener_datos_Family() + obtener_datos_Family_gog()
    return render_template('familia.html', juegos=juegos_precios)

@app.route('/puzle')
def juegos_puzle():
    juegos_precios = obtener_datos_puzle() + obtener_datos_puzle_gog()
    return render_template('puzle.html', juegos=juegos_precios)

@app.route('/arcade')
def juegos_arcade():
    juegos_precios = obtener_datos_Arcade() + obtener_datos_Arcade_gog()
    return render_template('arcade.html', juegos=juegos_precios)

@app.route('/casual')
def juegos_casual():
    juegos_precios = obtener_datos_Casual() + obtener_datos_Casual_gog()
    return render_template('casual.html', juegos=juegos_precios)

@app.route('/deporte')
def juegos_deporte():
    juegos_precios = obtener_datos_Sport() + obtener_datos_Sport_gog()
    return render_template('deporte.html', juegos=juegos_precios)

@app.route('/cartas')
def juegos_cartas():
    juegos_precios = obtener_datos_Cards() + obtener_datos_Card_gog()
    return render_template('cartas.html', juegos=juegos_precios)


# enlaces a paginas

@app.route('/estilos/<path:filename>')
def custom_css(filename):
    return send_from_directory(os.path.join(app.static_folder, 'estilos', 'Nuevo-estilo'), filename)

@app.route('/Imagenes/<path:filename>')
def custom_images(filename):
    return send_from_directory(os.path.join(app.static_folder, 'Imagenes'), filename)

@app.route('/js/<path:filename>')
def custom_js(filename):
    return send_from_directory(os.path.join(app.static_folder, 'js'), filename)



@app.route('/iniciar_session.html')
def custom_inicio():
    return render_template('iniciar_session.html')

@app.route('/login.html')
def custom_login():
    return render_template('login.html')

@app.route('/static/php/main', methods=['POST'])
def main():
    # Lógica para manejar la solicitud POST aquí

    # Redirigir al usuario de vuelta al index.html
    return redirect(url_for('lista_juegos'))

@app.route('/static/php/inicio', methods=['POST'])
def inicio():
    # Lógica para manejar la solicitud POST aquí

    # Redirigir al usuario a otra página si es necesario
    return redirect(url_for('lista_juegos'))

@app.route('/premium.html')
def custom_premium():
    return render_template('premium.html')

@app.route('/Equipo.html')
def custom_equipo():
    return render_template('Equipo.html')

def obtener_ruta_del_archivo_politica_privacidad():
    # Aquí deberías proporcionar la lógica para obtener la ruta del archivo PDF de política de privacidad
    # Por ejemplo, podrías construir la ruta utilizando el directorio de tu aplicación Flask y el nombre del archivo PDF

    # Supongamos que el archivo PDF se encuentra en el directorio 'static' de tu aplicación Flask
    ruta_pdf = os.path.join(os.path.dirname(__file__), 'static/pdf/', 'Política_de_Privacidad.pdf')

    return ruta_pdf

@app.route('/Política_de_Privacidad.pdf')
def custom_privacidad():
    # Construye dinámicamente la ruta del archivo PDF
    pdf_file_path = custom_privacidad()

    # Verifica si el archivo existe antes de enviarlo
    if os.path.exists(pdf_file_path):
        return send_file(pdf_file_path)
    else:
        return "El archivo no está disponible en el servidor."
    
def obtener_ruta_del_archivo_terminos():
    # Aquí deberías proporcionar la lógica para obtener la ruta del archivo PDF de política de privacidad
    # Por ejemplo, podrías construir la ruta utilizando el directorio de tu aplicación Flask y el nombre del archivo PDF

    # Supongamos que el archivo PDF se encuentra en el directorio 'static' de tu aplicación Flask
    ruta_pdf = os.path.join(os.path.dirname(__file__), 'static/pdf', 'Términos_y_Condiciones de Uso.pdf')

    return ruta_pdf

@app.route('/Términos_y_Condiciones_de_Uso.pdf')
def custom_terminos():
    # Construye dinámicamente la ruta del archivo PDF
    pdf_file_path = custom_terminos()

    # Verifica si el archivo existe antes de enviarlo
    if os.path.exists(pdf_file_path):
        return send_file(pdf_file_path)
    else:
        return "El archivo no está disponible en el servidor."



def abrir_navegador():
    url = 'http://127.0.0.1:5000'  # La dirección de tu servidor local
    webbrowser.open_new_tab(url)
    with open('navegador_abierto.txt', 'w') as f:
            f.write('1')
    

if __name__ == '__main__':
    abrir_navegador()
    app.run(debug=True)
