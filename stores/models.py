from django.db import models


class Dong(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.name


# Create your models here.
class Store(models.Model):
    name = models.CharField(max_length=100)
    dong = models.ForeignKey(Dong, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    # lon = models.IntegerField()
    # lat = models.IntegerField()

    def __str__(self):
        return self.name


class Menu(models.Model):
    store = models.ForeignKey(Store, related_name='menus', on_delete=models.CASCADE)
    menu_name = models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.ImageField(upload_to='stores/menu', default='')

    def __str__(self):
        return self.menu_name
