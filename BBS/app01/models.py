from django.db import models
from django.contrib.auth.models import AbstractUser   # 别忘了在配置文件夹里面配置

# Create your models here.


class UserInfo(AbstractUser):
    phone = models.BigIntegerField(null=True, blank=True)# blank告诉django后台管理该字段可以为空
    create_time = models.DateField(auto_now_add=True)
    # 该字段会将收到的文件自动存放到avatar文件夹下，只存该文件的路径，比如：avatar/111.png
    avatar = models.FileField(upload_to='avatar/', default='avatar/default.png')
    # 你把文件传给我之后，我会把当前我收到的这个文件对象放到avatar文件夹下面，
    # 文件名是什么就是什么，比如avatar/11.png，然后我这个字段就存当前文件的路径，当用户不选头像的时候就用默认头像
    blog = models.OneToOneField(to='Blog', null=True)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name_plural = '用户表'   # 将表名改成中文
        # 还有一种：verbose_name，但是一般不推荐使用，因为它会自动在名字后面加个s


class Blog(models.Model):
    site_name = models.CharField(max_length=32)
    site_title = models.CharField(max_length=64)
    # 个人站点的样式文件，存放该样式文件的路径
    theme = models.CharField(max_length=64)
    # user = models.OneToOneField(to='UserInfo',null=True)

    def __str__(self):
        return self.site_name


class Category(models.Model):
    name = models.CharField(max_length=64)
    blog = models.ForeignKey(to='Blog', null=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=32)
    blog = models.ForeignKey(to='Blog', null=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=64)
    desc = models.CharField(max_length=255)
    # 存大段文本
    content = models.TextField()
    create_time = models.DateField(auto_now_add=True)
    # 查询优化
    # 评论数
    comment_num = models.IntegerField(default=0)
    # 点赞数
    up_num = models.IntegerField(default=0)
    # 点踩数
    down_num = models.IntegerField(default=0)
    blog = models.ForeignKey(to='Blog', null=True)
    category = models.ForeignKey(to='Category', null=True)
    tags = models.ManyToManyField(to='Tag', through='Article2Tag',through_fields=('article', 'tag'))

    def __str__(self):
        return self.title


class Article2Tag(models.Model):
    article = models.ForeignKey(to='Article')
    tag = models.ForeignKey(to='Tag')


class UpAndDown(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    # 存0/1
    is_up = models.BooleanField()


class Comment(models.Model):
    user = models.ForeignKey(to='UserInfo')
    article = models.ForeignKey(to='Article')
    content = models.CharField(max_length=255)
    create_time = models.DateField(auto_now_add=True)
    parent = models.ForeignKey(to='self', null=True)













