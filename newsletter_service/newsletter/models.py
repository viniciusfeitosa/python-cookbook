from django.contrib.auth.models import User
from django.db import models


class Newsletter(models.Model):
    author = models.ForeignKey(User)
    subject = models.CharField(max_length=250)
    content = models.TextField()
