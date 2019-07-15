"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from app01 import views
from django.views.static import serve
from BBS import settings

urlpatterns = [
    url('^admin/', admin.site.urls),
    url('^register/', views.register),
    url('^login/', views.login),
    url('^get_code/', views.get_code),
    url('^home/', views.home),
    url('^logout/', views.logout),
    url('^set_password/', views.set_password),

    # 手动配置media文件配置
    url(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    # 不要轻易尝试下面的做法，否则后果自负
    # url(r'^app01/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT})

    # 点赞点踩   放在这里是因为：如果放在后面会先被下面的个人站点匹配到
    url(r'^up_or_down/',views.up_or_down),

    # 评论
    url(r'^comment/', views.comment),

    # 后台管理相关
    url(r'backend/', views.backend),

    # 添加文章
    url(r'^add_article/',views.add_article),

    # 富文本编辑器上传图片
    url(r'^upload_img', views.upload_img),

    # 修改头像
    url(r'^set_avatar/',views.set_avatar),

    # 修改邮箱
    url(r'^set_email/',views.set_email),

    # 编辑文章
    url(r'^edit_article(\d+)/',views.edit_article),

    # 删除文章
    url(r'^delete_article(\d+)/',views.delete_article),

    # 个人站点
    url(r'^(?P<username>\w+)/$', views.site),

    # 个人站点按照分类或标签或日期筛选文章
    # url(r'^(?P<username>\w+)/(?P<condition>category)/(?P<param>d+/)', views.site),
    # url(r'^(?P<username>\w+)/(?P<condition>tag)/(?P<param>d+/)', views.site),
    # url(r'^(?P<username>\w+)/(?P<condition>archive)/(?P<param>\w+/)', views.site),

    # 三条整合成一条
    url(r'^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)',views.site),

    # 文章详情页
    url(r'^(?P<username>\w+)/article/(?P<article_id>\d+)/', views.article_detail),

]
