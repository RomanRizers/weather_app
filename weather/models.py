from django.db import models

class City(models.Model):
    city_rus = models.CharField(max_length=255, unique=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name