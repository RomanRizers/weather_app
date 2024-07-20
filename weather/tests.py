from django.test import TestCase, Client
from django.urls import reverse
from .models import City
from unittest.mock import patch


class WeatherViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.city = City.objects.create(city='Moscow', city_rus='Москва', latitude=55.7558, longitude=37.6173)
        self.index_url = reverse('index')
        self.autocomplete_url = reverse('autocomplete')

    def test_index_view_get(self):
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')
        self.assertIn('form', response.context)
        self.assertIn('search_history', response.context)

    def test_index_view_post_valid_city(self):
        with patch('weather.views.get_weather_data') as mock_get_weather_data, \
                patch('weather.views.prepare_weather_data') as mock_prepare_weather_data:
            mock_get_weather_data.return_value = {'current': {}, 'daily': {}}
            mock_prepare_weather_data.return_value = {'current': {}, 'daily': []}

            response = self.client.post(self.index_url, {'city': 'Moscow'})

            self.assertEqual(response.status_code, 200)
            self.assertIn('weather_data', response.context)
            self.assertIn('current', response.context['weather_data'])
            self.assertIn('daily', response.context['weather_data'])

    def test_index_view_post_invalid_city(self):
        response = self.client.post(self.index_url, {'city': 'InvalidCity'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('weather_data', response.context)
        self.assertIn('error', response.context['weather_data'])

    def test_get_weather_data(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'current': {}, 'daily': {}}

            from .views import get_weather_data
            data = get_weather_data(55.7558, 37.6173)

            self.assertEqual(data, {'current': {}, 'daily': {}})
            mock_get.assert_called_once()

    def test_prepare_weather_data(self):
        from .views import prepare_weather_data
        data = {
            'current': {
                'temperature_2m': 20,
                'rain': 0,
                'wind_speed_10m': 5
            },
            'daily': {
                'time': ['2023-07-20'],
                'temperature_2m_max': [25],
                'temperature_2m_min': [15],
                'precipitation_probability_max': [10]
            }
        }

        result = prepare_weather_data(data)

        self.assertIn('current', result)
        self.assertIn('daily', result)
        self.assertEqual(result['current']['temperature'], 20)
        self.assertEqual(result['daily'][0]['max_temp'], 25)

    def test_autocomplete(self):
        response = self.client.get(self.autocomplete_url, {'q': 'Mos'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, [{'city': 'Moscow', 'city_rus': 'Москва'}])

    def test_clear_search_history(self):
        session = self.client.session
        session['search_history'] = ['Moscow']
        session.save()

        response = self.client.post(self.index_url, {'clear_history': 'true'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.index_url)

        session = self.client.session
        self.assertEqual(session.get('search_history'), [])
