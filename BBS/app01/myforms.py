from django import forms
from django.forms import widgets
from app01 import models


class MyForm(forms.Form):
    username = forms.CharField(max_length=8, min_length=3, label='用户名', error_messages={
        'required': '用户名不能为空',
        'max_length': '用户名最大8位',
        'min_length': '用户名最小3位'
    }, widget=widgets.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=8, min_length=3, label='密码', error_messages={
        'required': '密码不能为空',
        'max_length': '密码最大8位',
        'min_length': '密码最小3位'
    }, widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(max_length=8, min_length=3, label='确认密码', error_messages={
        'required': '确认密码不能为空',
        'max_length': '确认密码最大8位',
        'min_length': '确认密码最小3位'
    }, widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField( label='邮箱', error_messages={
        'required': '邮箱不能为空',
        'invalid': '邮箱格式不正确',
    }, widget=widgets.EmailInput(attrs={'class': 'form-control'}))

    # 局部钩子校验用户名是否存在
    def clean_username(self):
        username = self.cleaned_data.get('username')
        user_obj = models.UserInfo.objects.filter(username=username).first()
        if user_obj:
            self.add_error('username', '用户名已存在')
        return username

    # 全局钩子，校验密码是否一致
    def clean(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if not password == confirm_password:
            self.add_error('confirm_password', '两次密码不一致')
        return self.cleaned_data
















