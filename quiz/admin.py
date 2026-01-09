from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Quiz)
admin.site.register(models.Question)
admin.site.register(models.Option)
admin.site.register(models.UserAnswer)