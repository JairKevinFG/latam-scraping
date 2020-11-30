import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException





def obtener_precios(vuelo):
    tarifas = vuelo.find_elements_by_xpath('.//div[@class="fares-table-container"]//tfoot//td[contains(@class,"fare-")]')
    precios = []
    for tarifa in tarifas:
        nombre= tarifa.find_element_by_xpath('.//label').get_attribute('for')
        moneda = tarifa.find_element_by_xpath('.//span[@class="price"]/span[@class="currency-symbol"]').text
        valor = tarifa.find_element_by_xpath('.//span[@class="price"]/span[@class="value"]').text
        dict_tarifa = {nombre : {'moneda': moneda , 'valor': valor}}
        precios.append(dict_tarifa)

    return precios


def obtener_tiempos(vuelo):

    tiempos = {}
    salida = vuelo.find_element_by_xpath('.//div[@class="departure"]/time').get_attribute('datetime')
    llegada = vuelo.find_element_by_xpath('.//div[@class="arrival"]/time').get_attribute('datetime')
    duracion = vuelo.find_element_by_xpath('.//span[@class="duration"]/time').get_attribute('datetime')
    duracion = duracion.replace('PT', '')

    tiempos['hora de salida'] = salida
    tiempos['hora de llegada'] = llegada
    tiempos['duracion '] = duracion

    return tiempos


def obtener_datos_escalas(vuelo):
    segmentos = vuelo.find_elements_by_xpath('//div[@class="sc-hZSUBg gfeULV"]/div[@class="sc-cLQEGU hyoued"]')
    info_escalas = []
    for segmento in segmentos:

        origen = segmento.find_elements_by_xpath('.//div[@class="sc-iujRgT jEtESl"]//abbr[@class="sc-hrWEMg hlCkST"]')[0].text
        hra_salida = segmento.find_elements_by_xpath('.//div[@class="sc-iujRgT jEtESl"]//time')[0].get_attribute('datetime')
        destino = segmento.find_elements_by_xpath('.//div[@class="sc-iujRgT jEtESl"]//abbr[@class="sc-hrWEMg hlCkST"]')[1].text
        hra_llegad = segmento.find_elements_by_xpath('.//div[@class="sc-iujRgT jEtESl"]//time')[1].get_attribute('datetime')
        duracion = segmento.find_element_by_xpath('.//span[@class="sc-cmthru ipcOEH"]//time').get_attribute('datetime')
        num_vuelo = segmento.find_element_by_xpath('.//div[@class="sc-hMFtBS bGZqFm"]//b').text
        mod_avion = segmento.find_element_by_xpath('.//div[@class="sc-hMFtBS bGZqFm"]//span[@class="sc-gzOgki uTyOl"]').text

        data_dict = {
            'origen': origen,
            'hra_salida':hra_salida,
            'destino':destino,
            'hra_llegad':hra_llegad,
            'duracion':duracion,
            'num_vuelo':num_vuelo,
            'mod_avion':mod_avion
        }

        info_escalas.append(data_dict)

        return info_escalas


def obtener_info(driver):

    driver.find_element_by_xpath('//div[@class="onesignal-slidedown-dialog"]//button[@class="align-right secondary slidedown-button"]').click()
    vuelos = driver.find_elements_by_xpath('//li[@class="flight"]')
    print(f'Se encontraron {len(vuelos)} vuelos')
    print('Iniciando scraping')
    info = []
    for vuelo in vuelos:

        tiempos = obtener_tiempos(vuelo)
        vuelo.find_element_by_xpath('.//div[@class="flight-summary-stops-description"]/button').click()
        escalas = obtener_datos_escalas(vuelo)
        driver.find_element_by_xpath('//div[@class="modal-header sc-dnqmqq cGfTsx"]//button[@class="close"]').click()
        vuelo.click()
        precios = obtener_precios(vuelo)
        vuelo.click()
        info.append({'precios':precios,'tiempo':tiempos,'escalas':escalas})
    print(info)
    return info


url = 'https://www.latam.com/es_pe/apps/personas/booking?fecha1_dia=02&fecha1_anomes=2020-12&auAvailability=1&ida_vuelta=ida&vuelos_origen=Lima&from_city1=LIM&vuelos_destino=Nueva%20York&to_city1=NYC&flex=1&vuelos_fecha_salida_ddmmaaaa=02/12/2020&cabina=Y&nadults=1&nchildren=0&ninfants=0&cod_promo=&stopover_outbound_days=0&stopover_inbound_days=0#/'
headers = {
    'User-Agent'  : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
}
response = requests.get(url , headers = headers)
s = BeautifulSoup(response.text,'lxml')

options = webdriver.ChromeOptions()
options.add_argument('--incognito')
driver = webdriver.Chrome(executable_path='/home/jkevin/Documents/Proyectos/LatamScraper/chromedriver',options=options)
driver.get(url)
delay = 10
try:
    vuelo = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.XPATH, '//li[@class="flight"]')))
    print("page finished loading")
    info_vuelos = obtener_info(driver);
except TimeoutException:
    print("web took a long time to load")
    info_vuelos = []

driver.close()