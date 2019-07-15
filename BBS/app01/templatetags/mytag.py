from django import template
from app01 import models
from django.db.models import Count
from django.db.models.functions import TruncMonth


register = template.Library()


@register.inclusion_tag('left_menu.html',name='left_menu')
def left_menu(username):
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    # 统计当前用户每一分类及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name', 'c', 'pk')  # 用元组是为了渲染方便，前端直接可以通过.0.1就可以取值
    # 统计当前用户对应的每一个标签及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name','c','pk')
    # 按日期归档
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(c=Count('pk')).values_list('month','c')
    return {'user_obj':user_obj, 'blog': blog,'category_list':category_list, 'tag_list':tag_list, 'date_list':date_list}




