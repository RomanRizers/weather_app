from django.shortcuts import render, redirect
from .forms import CityForm
from .models import City
import requests
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime
from babel.dates import format_date

def index(request):
    form = CityForm(request.POST or None)
    weather_data = None
    search_history = request.session.get('search_history', [])

    if request.method == 'POST':
        if 'clear_history' in request.POST:
            request.session['search_history'] = []
            return redirect('index')

        if form.is_valid():
            city_name = form.cleaned_data['city']
            cities = City.objects.filter(Q(city__iexact=city_name) | Q(city_rus__iexact=city_name))

            if cities.exists():
                city = cities.first()
                data = get_weather_data(city.latitude, city.longitude)
                weather_data = prepare_weather_data(data)

                if city_name not in search_history:
                    search_history.append(city_name)
                    request.session['search_history'] = search_history

            else:
                weather_data = {'error': 'Город не найден!'}

    selected_city = request.GET.get('selected_city')
    if selected_city:
        cities = City.objects.filter(Q(city__iexact=selected_city) | Q(city_rus__iexact=selected_city))
        if cities.exists():
            city = cities.first()
            data = get_weather_data(city.latitude, city.longitude)
            weather_data = prepare_weather_data(data)
        else:
            weather_data = {'error': 'Город не найден!'}

    return render(request, 'weather/index.html', {
        'form': form,
        'weather_data': weather_data,
        'search_history': search_history
    })


def get_weather_data(latitude, longitude):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,rain,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=Europe/Moscow'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def prepare_weather_data(data):
    current = data.get('current', {})
    daily = data.get('daily', {})

    current_weather = {
        'temperature': current.get('temperature_2m'),
        'rain': current.get('rain'),
        'wind_speed': current.get('wind_speed_10m')
    }

    weather_list = []
    for date, max_temp, min_temp, precip_prob in zip(
            daily.get('time', []),
            daily.get('temperature_2m_max', []),
            daily.get('temperature_2m_min', []),
            daily.get('precipitation_probability_max', [])
    ):
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        formatted_date = format_date(date_obj, format='d MMMM', locale='ru_RU')

        weather_list.append({
            'date': formatted_date,
            'max_temp': max_temp,
            'min_temp': min_temp,
            'precipitation_probability_max': precip_prob,
        })

    return {
        'current': current_weather,
        'daily': weather_list
    }

def autocomplete(request):
    query = request.GET.get('q', '')
    cities = City.objects.filter(
        Q(city__icontains=query) | Q(city_rus__icontains=query)
    ).values_list('city', 'city_rus')[:10]

    suggestions = []
    for city in cities:
        suggestions.append({
            'city': city[0],
            'city_rus': city[1]
        })

    return JsonResponse(suggestions, safe=False)