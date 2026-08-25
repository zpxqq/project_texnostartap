from django.db import models
from django.contrib.auth.models import User


class Site(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="sites")
    name = models.CharField(max_length=200)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} — {self.url}"


class Check(models.Model):
    site = models.ForeignKey(Site,on_delete=models.CASCADE,related_name="checks")
    score = models.FloatField()
    checked_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.site.url} — {self.score}"


class CheckResult(models.Model):
    checkk = models.ForeignKey(Check,on_delete=models.CASCADE,related_name="results")
    type = models.CharField(max_length=100)
    count = models.IntegerField()
    total = models.IntegerField()
    message = models.TextField()
