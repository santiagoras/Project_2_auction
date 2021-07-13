from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import ForeignKey, ManyToManyField


class User(AbstractUser):
    pass

class Listing(models.Model):
    author=models.ForeignKey(User, on_delete=models.CASCADE, related_name="made")
    description=models.TextField(max_length=500)
    image=models.CharField(max_length=256, blank=True)
    title=models.CharField(max_length=64)
    watchers=models.ManyToManyField(User, related_name="following", blank=True)

class Bid(models.Model):
    amount= models.DecimalField(max_digits=15, decimal_places=2)
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    listing=models.ForeignKey(Listing, on_delete=models.CASCADE)

class Comment(models.Model):
    author=models.ForeignKey(User, on_delete=models.CASCADE)
    listing=models.ForeignKey(Listing, on_delete=models.CASCADE)
    content=models.TextField(max_length=500)
    date=models.DateTimeField(auto_now_add=True)



    

