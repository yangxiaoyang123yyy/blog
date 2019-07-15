from django.shortcuts import render,HttpResponse,redirect
from app01 import myforms
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.db.models import Count,F
from django.db.models.functions import TruncMonth
import json
from django.utils.safestring import mark_safe
from django.db import transaction


# Create your views here.


def register(request):
    back_dic = {'code': 100, 'msg': ''}
    form_obj = myforms.MyForm()
    if request.method == 'POST':
        form_obj = myforms.MyForm(request.POST)  # form组件做第一层校验
        if form_obj.is_valid():
            data = form_obj.cleaned_data
            # cleaned_data是一个大字典，里面有username...那个几个字段，但是confirm_password我们不需要了，只要通过了这个，说明密码一致了，就不需要confirm_password了,因为数据库中并没有confirm_password这个字段

            # 将confirm_password去掉
            data.pop('confirm_password')
            # 获取用户上传的文件对象
            file_obj = request.FILES.get('myfile')
            # 如果用户没有选择头像，也即没点头像，那myfile里面就没有值，让它走默认字段，这就不需要把avatar添加进来了，如果用户不传了，你在create_user里面令avatar=None,这样并不合理，所有需要判断一下用户有没有传，如果用户没有传字段就不需要再获取了，就直接传username，password，email这三个字段，avatar用默认的就可以了

            # 解决用户表和个人站点绑定问题
            # 方法一  注意没有数据的情况，可以加一个判断，如果blog_obj_list为空就令blog_id=1
            # blog_obj_list = models.Blog.objects.all()
            # # print(blog_obj_list.id)
            # l=[]
            # for i in blog_obj_list:
            #     l.append(i.id)
            #     # print(i.id)
            # blog_id = max(l) + 1
            # with transaction.atomic():
            #     data['blog_id'] = blog_id
            #     models.Blog.objects.create(pk=blog_id)

            # 判断用户是否上传了自己的头像
            if file_obj:
                # 往data里面添加键值
                data['avatar'] = file_obj
                # 这时候data里面就有四组键值了，avatar如果传了就有，没有传就没有

            # 方法二
            models.Blog.objects.create(site_name=data['username'])
            blog_id = models.Blog.objects.filter(site_name=data['username']).first().pk
            data['blog_id'] = blog_id
            models.UserInfo.objects.create_user(**data)
            back_dic['msg'] = '注册成功'
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 101
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request,'register.html', locals())


def login(request):
    back_dic = {'code': 100, 'msg': ''}
    # 判断是ajax请求还是正常form表单请求  request.is_ajax()  ajax请求不能用redirect
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 先校验验证码(可以区分大小写也可以不区分  不区分：统一转成大小或者转成小写进行对比即可)
        if request.session.get('code').upper() == code.upper():
            # 利用auth模块校验用户名和密码是否正确
            user_obj = auth.authenticate(username=username,password=password)  # 这里的request可以传可以不传，因为它有一个request=None
            if user_obj:
                # 利用auth模块记录当前登录状态
                auth.login(request,user_obj)  # 这里的request必须要传
                back_dic['msg'] = '登录成功'
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 102
                back_dic['msg'] = '用户名或密码错误'
        else:
            back_dic['code'] = 103
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


from PIL import Image,ImageDraw,ImageFont,ImageFilter
import random
from io import BytesIO
from django.contrib.auth.decorators import login_required


# 随机生成rgb参数
def get_random():
    return random.randint(128,255),random.randint(128,255),random.randint(128,255)


def get_code(request):
    # # 推导步骤1：打开本地文件发送二进制数据
    # with open(r'D:\SH_PY\BBS\avatar\default.png', 'rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # # 推导步骤2：动态生成图片发送二进制数据
    # # img_obj = Image.new('RGB',(310,35),'green')  # 第三个参数既可以传颜色英文，也可以传rgb参数
    # img_obj = Image.new('RGB',(310,35),(128,128,128))  # 第三个参数既可以传颜色英文，也可以传rgb参数
    # # 先保存成文件   注： 不能直接发送，必须先保存到一个文件里面，再以二进制模式读取发送数据
    # with open('demo.png','wb') as f:
    #     img_obj.save(f)
    # # 再以二进制模式读取发送数据
    # with open('demo.png', 'rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # # 推导步骤3：图片颜色动态变化  图片存放不再依赖文件的形式
    # img_obj = Image.new('RGB',(310,35), get_random())
    # # 生成一个BytesIO对象
    # io_obj = BytesIO()  # 将这个对象看成文件句柄
    # img_obj.save(io_obj, 'png')  # 将图片数据存入内存管理器中  需要指定图片格式！！
    # return HttpResponse(io_obj.getvalue())  # 将保存的数据以二进制的数据返回出来


    # 最终不删减版
    img_obj = Image.new('RGB',(310,35), get_random())
    # 生成一个画笔对象
    img_draw = ImageDraw.Draw(img_obj)  # 你的画笔就可以在该图片上为所欲为
    img_font = ImageFont.truetype('static/font/ttq.ttf',35)

    # 随机验证码：数字+小写字母(65-90)+大写字母(97-122)
    code = ''  # 定义一个变量存储最终验证码
    for i in range(5):
        random_int = str(random.randint(0, 9))
        random_lower = chr(random.randint(97, 122))
        random_upper = chr(random.randint(65, 90))
        temp_code = random.choice([random_int,random_lower,random_upper])
        # 将产生的字一个一个的写到图片上  一定要一个一个写，一起写的话，字都会堆到一起，
        # 第一个参数是坐标，+i*45的目的是调整两个字符之间的距离，也可以写负数，负数是往上移，正数是往下
        img_draw.text((60+i*45,0),temp_code,get_random(),img_font)
        # code记录
        code += temp_code
    print(code)
    # 将code存放到session表中
    request.session['code'] = code
    # 生成io对象
    io_obj = BytesIO()
    # # 图片模糊
    # img_obj = img_obj.filter(ImageFilter.BLUR)
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request):
    # 将网站所有的文章都展示到主页
    article_list = models.Article.objects.all()
    return render(request,'home.html',locals())


def logout(request):
    auth.logout(request)
    return redirect('/home/')


def set_password(request):
    old_password = request.POST.get('old_password')
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')
    # 先判断旧密码是否正确
    res = request.user.check_password(old_password)
    if res:
        # 再来比对新旧密码是否一致
        if new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            return redirect('/login')
    return render(request, 'set_password.html')


def site(request,username,*args,**kwargs):  # **kwargs是后面用户具体点某个分类、标签、日期归档的时候，渲染出对应的文章
    user_obj = models.UserInfo.objects.filter(username=username).first()
    if not user_obj:
        # 当用户不存在的时候  直接跳转我们自己的404页面
        return render(request, 'error.html')
    blog = user_obj.blog
    article_list = models.Article.objects.filter(blog=blog)
    # if not user_obj:
    #     # 当用户不存在的时候  直接跳转我们自己的404页面
    #     return render(request, 'error.html')  # 放在下面，我们输错的时候不会跳转到我们自己的404页面

    # # 统计当前用户每一分类及分类下的文章数
    # category_list = models.Category.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name', 'c', 'pk')  # 用元组是为了渲染方便，前端直接可以通过.0.1就可以取值
    # # 统计当前用户对应的每一个标签及标签下的文章数
    # tag_list = models.Tag.objects.filter(blog=blog).annotate(c=Count('article')).values_list('name','c','pk')
    # # 按日期归档
    # data_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')).values('month').annotate(c=Count('pk')).values_list('month','c')

    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__pk=param)
        else:
            # param = '2018-6'
            year,month = param.split('-')
            article_list = article_list.filter(create_time__year=year,create_time__month=month)

    return render(request,'site.html',locals())


def article_detail(request,username,article_id):
    article_obj = models.Article.objects.filter(pk=article_id).first()
    blog = models.Blog.objects.filter(userinfo__username=username).first()
    # 将放弃文章的所有评论获取到
    comment_list = models.Comment.objects.filter(article=article_obj)
    return render(request,'article_detail.html',locals())


def up_or_down(request):
    """
    1.先判断用户是否登录
    2.判断文章是否是当前用户写的
    3.才能去判断用户是否对该文章点赞或点踩了
    4.需要在两张表里面修改数据
    :param request:
    :return:
    """
    back_dic = {'code': 100, 'msg': ''}
    if request.is_ajax():
        is_up = request.POST.get('is_up')
        is_up = json.loads(is_up)  # 利用json模板反序列成后端python布尔值类型
        article_id = request.POST.get('article_id')
        # 1.判断当前用户是否登录
        if request.user.is_authenticated():
            # 2.判断文章是否是当前用户自己写的
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo.pk == request.user.id:
                # 3.判断当前用户是否对文章点赞点踩了
                res = models.UpAndDown.objects.filter(user=request.user,article=article_obj)
                if not res:
                    # 4.需要在两张表里面修改数据
                    # 先修改普通字段的数据
                    if is_up:
                        # 点赞
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num')+1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        # 点踩
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num')+1)
                        back_dic['msg'] = '点踩成功'
                    # 最后修改UpAndDown表数据
                    models.UpAndDown.objects.create(user=request.user,article=article_obj,is_up=is_up)
                    back_dic['code']=200
                else:
                    back_dic['code'] = 201
                    back_dic['msg'] = '你已经点过了'
            else:
                back_dic['code'] = 202
                back_dic['msg'] = '不能给自己点'
        else:
            back_dic['code'] = 203
            back_dic['msg'] = mark_safe('请先<a href="/login/">登录</a>')
        return JsonResponse(back_dic)


'''
事务ACID
    原子性
    一致性
    隔离性
    持久性
'''


def comment(request):
    back_dic = {'code': 100, 'msg': ''}
    if request.is_ajax():
        # 获取前端发送过来的数据
        article_id = request.POST.get('article_id')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        # 校验当前用户是否登录
        if request.user.is_authenticated:
            with transaction.atomic():    # 绑定事务
                # 在文章表中将普通的评论字段加1
                models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num')+1)
                # 再去评论表存储真正的数据
                models.Comment.objects.create(user=request.user,article_id=article_id,content=content,parent_id=parent_id)
                back_dic['msg'] = '评论成功'
        else:
            back_dic['code'] = 110
            back_dic['msg'] = '请先登录'
    return JsonResponse(back_dic)


from app01.utils.mypage import Pagination


@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog)
    # 添加分页器
    # 用户想访问的当前页面
    current_page = request.GET.get('page',1)
    # 文章总条数
    all_count = article_list.count()
    page_obj = Pagination(current_page=current_page,all_count=all_count)
    # 对数据进行切分
    page_queryset = article_list[page_obj.start:page_obj.end]
    blog = request.user.blog
    return render(request, 'backend/backend.html',locals())  # 后台管理相关的单独放一个文件夹


from bs4 import BeautifulSoup


@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        # 将需要处理的文本内容交由该模块生成一个soup对象
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                # 将script删除
                tag.decompose()  # 1.解决xss攻击问题
        # 文章简介
        desc = soup.text[0:150]  # 2.解决了文章简介的问题

        # 保存到数据库中
        models.Article.objects.create(title=title,content=content,desc=desc,blog=request.user.blog)
        return redirect('/backend/')
    return render(request,'backend/add_article.html')


import os
from BBS import settings


def upload_img(request):
    """
            //成功时
            {
                    "error" : 0,
                    "url" : "http://www.example.com/path/to/file.ext"
            }
            //失败时
            {
                    "error" : 1,
                    "message" : "错误信息"
            }
        :param request:
        :return:
        """
    if request.method == 'POST':
        # 将用户上传的图片存入media文件夹中，以便后续查找
        print(request.FILES)  # 可以看到如下结果，那么我们就可以通过字典的key拿到对应的值
        # <MultiValueDict: {'imgFile': [<InMemoryUploadedFile: 7845c4329de71c67285e07.jpg (image/jpeg)>]}>
        file_obj = request.FILES.get('imgFile')
        # 将该文件存入media文件夹
        # 1 手动拼接文件存放路径
        path = os.path.join(settings.BASE_DIR,'media','article_img')
        # 判断当前文件路径是否存在，如果不存在，自动创建
        if os.path.exists(path):
            os.mkdir(path)  # 自动创建文件夹
        file_path = os.path.join(path,file_obj.name)
        with open(file_path,'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic = {
                "error": 0,
                "url": "/media/article_img/%s"%file_obj.name
        }
        return JsonResponse(back_dic)
    return HttpResponse('OK')


def set_avatar(request):
    back_dic = {'code':100, 'msg': ''}
    avatar = request.user.avatar
    if request.method == 'POST':
        file_obj = request.FILES.get('myfile')
        # 修改用户avatar字段
        # 1.利用queryset内置方法修改  不行，结果会导致数据库保存的文件路径不对
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)
        # 2.利用对象修改
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        back_dic['msg'] = '修改成功'
        back_dic['url'] = '/home/'
        return JsonResponse(back_dic)
    return render(request,'set_avatar.html',locals())


def edit_article(request, edit_id):
    article_obj = models.Article.objects.filter(pk=edit_id).first()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        models.Article.objects.filter(pk=edit_id).update(title=title,content=content)
        return redirect('/backend/')
    return render(request, 'backend/edit_article.html', locals())


def delete_article(request, delete_id):
    article_obj = models.Article.objects.filter(pk=delete_id).first()
    article_obj.delete()
    return redirect('/backend/')


def set_email(request):
    old_email = request.POST.get('old_email')
    new_email = request.POST.get('new_email')
    confirm_email = request.POST.get('confirm_email')
    # 先判断旧邮箱是否正确
    if request.user.email == old_email:
        # 再来比对新旧邮箱是否一致
        if new_email == confirm_email:
            models.UserInfo.objects.filter(pk=request.user.pk).update(email=new_email)
            return redirect('/login')
    return render(request, 'set_email.html')



