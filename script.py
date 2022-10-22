# Для скрипта требуются зависимости со следующей командой установки:
# pip install mysql-connector-python requests

import mysql.connector
import datetime
import requests
import json
from xml.etree import ElementTree

log_file = open('log.txt', 'a')


def log(text):
    current_time = datetime.datetime.now()
    separator = ': '
    log_value = f'{current_time}{separator}{text}'

    print(log_value)
    print(log_value, file=log_file)


def insert_db(text):

    mydb = mysql.connector.connect(host="185.20.115.109",
                                   port="3306",
                                   user="admin",
                                   password="ges7Tgeb3Defu7Yb")

    cursor = mydb.cursor()
    cursor.execute(
        f"insert test.test(date, value) value (CURRENT_TIMESTAMP(), '{text}')")
    mydb.commit()

    log('Current DB state:')
    cursor.execute(f"select date, value from test.test")

    for x in cursor:
        log(f'date: {x[0]}, value: {x[1]}')


def send_rest_request(user_text):
    url = "http://185.20.115.109/report"

    body = json.dumps({"value": user_text})
    headers = {'Content-Type': 'application/json'}

    response = requests.request("POST", url, headers=headers, data=body)

    value = response.json()['out']
    log(f'Got from rest endpoint: {value}')

    return value


def send_soap_request(user_text):
    url = "http://185.20.115.109/bank/action"

    payload = f'''
    <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:int="https://internet.by">
    <soapenv:Header/>
    <soapenv:Body>
    <int:test_test1 soapenv:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <value xsi:type="xsd:string">{user_text}</value>
    </int:test_test1>
    </soapenv:Body>
    </soapenv:Envelope>
    '''

    headers = {'Content-Type': 'application/xml'}

    response = requests.request("POST",
                                url,
                                headers=headers,
                                data=payload.encode('utf-8'))
    xml = ElementTree.fromstring(response.content)

    value = xml.find('{http://schemas.xmlsoap.org/soap/envelope/}Body').find(
        '{https://internet.by}test_test1_response').find('value').text

    log(f'Got from soap endpoint: {value}')

    return value


user_text = input("Input base text: ")
result_rest = send_rest_request(user_text)
result_soap = send_soap_request(result_rest)
insert_db(result_soap)
