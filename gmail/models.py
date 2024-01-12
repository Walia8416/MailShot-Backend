from django.db import models

# Create your models here.

class Gmail(models.Model):
    id = models.IntegerField(primary_key=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    