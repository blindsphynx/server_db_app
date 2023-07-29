import base64
import unittest
import requests
from cryptography.fernet import Fernet
from requests.auth import HTTPBasicAuth
# from src.client.DatabaseClient import encode_password, secret, host
secret = b'yRIKdydLGHRMmJ-gFdgnhafhd4qi_w8BU2jHsmLP-LM='
host = "http://localhost:8000/"


def encode_password(password, key):
    bytes_password = password.encode('ascii')
    base64_password = base64.b64encode(bytes_password)
    encoded_password = Fernet(key).encrypt(base64_password)
    return encoded_password


class TestServer(unittest.TestCase):

    def test_authorize(self):
        username = "admin"
        password = "pyro127"
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


if __name__ == '__main__':
    unittest.main()
