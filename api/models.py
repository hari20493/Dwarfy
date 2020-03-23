from django.db import models

# Create your models here.
from django.template.defaultfilters import slugify

from api.utils import unique_slug_generator


class Urls(models.Model):
    title = models.CharField(null=True,blank=True,max_length=255)
    long_url = models.URLField(null=True, blank=True)
    slug = models.SlugField(max_length=250, null=True, blank=True)
    added_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self)
        super().save(*args, **kwargs)


class Reports(models.Model):
    url = models.OneToOneField(Urls, null=True, blank=True,on_delete=models.CASCADE)
    hits = models.IntegerField(default=0)
    last_hit_time = models.DateTimeField(auto_now=True)


class Logs(models.Model):
    url = models.ForeignKey(Urls, null=True, blank=True,on_delete=models.CASCADE)
    hit_time = models.DateTimeField(auto_now_add=True)
