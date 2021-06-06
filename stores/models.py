from django.db import models


class Dong(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# Create your models here.
class Store(models.Model):
    name = models.CharField(max_length=100)
    dong = models.ForeignKey(Dong, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, default='')

    # lon = models.IntegerField()
    # lat = models.IntegerField()

    def __str__(self):
        return self.name


class Menu(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    menu_name = models.CharField(max_length=100)
    price = models.IntegerField()

    def __str__(self):
        return self.menu_name
