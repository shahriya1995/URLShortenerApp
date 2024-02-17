import unittest
from app import app

class TestURLShortener(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_shorten_valid_url(self):
        response = self.app.post('/shorten', json={"url": "http://www.example.com"})
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn('short_url', data)

    def test_shorten_invalid_url(self):
        response = self.app.post('/shorten', json={"url": "invalid-url"})
        self.assertEqual(response.status_code, 201)

    def test_redirect_to_long_url(self):
        response = self.app.post('/shorten', json={"url": "http://www.example.com"})
        short_url = response.get_json()['short_url']
        response = self.app.get(short_url)
        self.assertEqual(response.status_code, 302)

    def test_non_existent_short_code(self):
        response = self.app.get('/non_existent_code')
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()