import os
import django
import pandas as pd
from weather.models import City

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weather_project.settings')
django.setup()
def import_cities_from_excel(file_path):
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        City.objects.create(
            city_rus=row['city_rus'],
            city=row['city'],
            latitude=row['lat'],
            longitude=row['lng']
        )

if __name__ == "__main__":
    import_cities_from_excel('data/city_dataset.xlsx')
