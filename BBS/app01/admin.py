from django.contrib import admin
from app01 import models


# Register your models here.

# 注册的顺序没有关系，只要注册了即可
admin.site.register(models.UserInfo)
admin.site.register(models.Blog)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Article)
admin.site.register(models.Article2Tag)
admin.site.register(models.UpAndDown)
admin.site.register(models.Comment)


