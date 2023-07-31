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


if __name__ == '__main__':
    unittest.main()
