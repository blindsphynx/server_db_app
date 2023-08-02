import base64
import os
import unittest
import requests
from requests.auth import HTTPBasicAuth
from src.client.DatabaseClient import encode_password, secret, host


class TestServer(unittest.TestCase):

    def test_authorize(self):
        username = "admin"
        password = "pass1234"
        my_password = encode_password(password, secret)
        response = requests.get(host, auth=HTTPBasicAuth(username, my_password))
        status_code = response.status_code
        self.assertEqual(status_code, 200)

    def test_authorize_wrong(self):
        username = "admin"
        password = "password127"
        my_password = encode_password(password, secret)
        response = requests.get(host, auth=HTTPBasicAuth(username, my_password))
        status_code = response.status_code
        self.assertEqual(status_code, 401)

    # Добавление новой записи
    def test_addNewRecord(self):
        new_data = {
            'id': '7',
            'name': 'Losev Egor',
            'year': 2004,
            'photo': '',
            'course': 1,
            'group': 2375,
        }
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        response = requests.post(host + "/post-data", json=new_data, headers=hdrs)
        server_data = {
            'course': 1,
            'gruppa': 2375,
            'id': '7',
            'name': 'Losev Egor',
            'picture': '',
            'year': 2004
        }
        self.assertEqual(response.status_code, 201)
        # self.assertEqual(response.text, server_data)

    # Удаление записи
    def test_deleteRecord(self):
        data = {"id": "7", "name": "Losev Egor"}
        server_data = ""
        response = requests.delete(host + "/delete-data", json=data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.text, server_data)

    # Тест на добавление изображения
    def test_uploadImage(self):
        with open("photo.jpg", "rb") as img:
            string = base64.b64encode(img.read()).decode('utf-8')
        newData = {"id": 7, "name": "Soldatova Anna",
                   "year": 2002, "photo": "photo.jpg",
                   "course": 3, "group": 1234,
                   "binary_photo": string}
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        response = requests.post(host + "/post-data", json=newData, headers=hdrs)
        server_data = {
            "course": 3,
            "gruppa": 1234,
            "id": 7,
            "name": "Soldatova Anna",
            "picture": "photo.jpg",
            "year": 2002
        }
        # self.assertEqual(response.text, server_data)
        # self.assertEqual(response.status_code, 201)


if __name__ == '__main__':
    unittest.main()
