from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.name


# Create your models here.
class Store(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Menu(models.Model):
    store = models.ForeignKey(Store, related_name='menus', on_delete=models.CASCADE)
    menu_name = models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.ImageField(upload_to='stores/menu', default='', null=True, blank=True)

    def __str__(self):
        return self.menu_name
