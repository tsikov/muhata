# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User, UserManager
import time
from django.utils import timezone
from django.template.defaultfilters import slugify
from unidecode import unidecode

from django import forms

from django.contrib.auth.forms import AuthenticationForm

class Account(User):
    is_over_18 = models.BooleanField()
    submits_adult_content = models.BooleanField(default = False)
    show_ads = models.BooleanField(default = True)
    reported = models.IntegerField(default = 0)
    reports_made = models.IntegerField(default = 0)
    spammer = models.IntegerField(default = 0)
    validation_code = models.CharField(max_length = 10)
    email_verified = models.BooleanField(default = False)
    has_gold = models.BooleanField(default = False)
    gold_creadit = models.IntegerField(default = 0)
    gold_count = models.IntegerField(default = 0)
    trusted_sponsor = models.IntegerField(default = True)

    objects = UserManager()

class AccountForm(ModelForm):
    username = forms.CharField(label = "" , initial='потребителско име', widget=forms.TextInput(attrs={'id': 'register_username_field'}))
    password = forms.CharField(label = "" , initial='парола', widget=forms.PasswordInput(attrs={'id': 'register_password_field'}, render_value = True))
    email = forms.EmailField(label = "" , initial='поща', widget=forms.TextInput(attrs={'id': 'register_email_field'}))
    class Meta:
        model = Account
        fields = ('username','password','email')

class MyAuthForm(AuthenticationForm):
    username = forms.CharField(label = "" , initial='потребителско име', widget=forms.TextInput(attrs={'id': 'login_username_field'}))
    password = forms.CharField(label = "" , initial='парола', widget=forms.PasswordInput(attrs={'id': 'login_password_field'}, render_value = True))

class Ad(models.Model):
    title = models.CharField(max_length = 120)
    slug = models.SlugField(max_length = 120)
    date = models.DateTimeField(default = timezone.now())
    author = models.IntegerField()
    content = models.TextField(max_length = 500)
    has_pic = models.BooleanField()
	# upload_to directory is wrong - files are handled outside of django
	# to skip it's annoying default behaviour
    picture_height = models.IntegerField(default = 0)
    picture_width = models.IntegerField(default = 0)
    adult_content = models.BooleanField(default = False)
    reported_adult = models.IntegerField(default = 0)
    reported = models.IntegerField(default = 0)
    score = models.IntegerField(default = time.time())
    gold = models.IntegerField(default = 1)
    def __unicode__(self):
        return self.title
    def save(self):
        if not self.id:
			self.slug = slugify( unidecode( self.title ) )
        super(Ad, self).save()

class AdForm(ModelForm):
    title = forms.CharField( label = "" , initial='Заглавие')
    content = forms.CharField( label = "" , initial = "съдържание на обявата", widget=forms.Textarea())
    picture = forms.ImageField(label = "", required=False)
    adult_content = forms.BooleanField( label = u"Неподходящо за непълнолетни?", required=False)
    class Meta:
        model = Ad
        fields = ('title','content','adult_content')

class EditAdForm(AdForm):
	class Meta:
		fields = ('title','content','adult_content')

class Tag(models.Model):
    ad = models.ManyToManyField(Ad)
    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 255, default = "")
    count = models.IntegerField(default = 1)
    def __unicode__(self):
        return self.name

class Message(models.Model):
    ad = models.ForeignKey(Ad)
    sender = models.ForeignKey(Account)
    title = models.CharField(max_length = 120)
    content = models.TextField(max_length = 500)

