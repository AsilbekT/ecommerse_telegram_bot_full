from django.db import models
from ckeditor.fields import RichTextField

from bot.models import Branch
# Create your models here.

class Post(models.Model):
     post_title = models.CharField(max_length=1000)
     post_body = RichTextField(blank=True, null=True)
     videofile = models.FileField(upload_to='videos/', blank=True, default='default.mp4')

     # post_body = models.TextField(default='', blank=True)
     image = models.ImageField(blank=True, default='default.jpg')
     branches = models.ManyToManyField(Branch)

     def __str__(self):
          return self.post_title