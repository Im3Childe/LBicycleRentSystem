# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
import django.contrib.auth.models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(unique=True, max_length=30, error_messages={'unique': 'A user with that username already exists.'}, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid')], verbose_name='username', help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(verbose_name='active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(related_name='user_set', verbose_name='groups', to='auth.Group', related_query_name='user', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', verbose_name='user permissions', to='auth.Permission', related_query_name='user', blank=True, help_text='Specific permissions for this user.')),
            ],
            options={
                'db_table': 'User',
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('brand', models.CharField(max_length=10)),
                ('img', models.ImageField(upload_to='theSystem')),
            ],
            options={
                'db_table': 'BrandInfo',
                'verbose_name': '商品品牌',
                'verbose_name_plural': '商品品牌',
            },
        ),
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('goods', models.CharField(max_length=20)),
                ('brandId', models.IntegerField()),
                ('styleId', models.IntegerField()),
                ('goodsNum', models.IntegerField()),
                ('img', models.ImageField(upload_to='theSystem')),
                ('price', models.IntegerField()),
                ('sales', models.IntegerField()),
            ],
            options={
                'db_table': 'Goods',
                'verbose_name': '商品',
                'verbose_name_plural': '商品',
            },
        ),
        migrations.CreateModel(
            name='GoodsInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('color', models.CharField(max_length=10)),
                ('brand', models.CharField(max_length=16)),
                ('type', models.CharField(max_length=16)),
            ],
            options={
                'db_table': 'GoodsInfo',
                'verbose_name': '商品信息',
                'verbose_name_plural': '商品信息',
            },
        ),
        migrations.CreateModel(
            name='Income',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('income', models.IntegerField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'Income',
                'verbose_name': 'Income',
                'verbose_name_plural': 'Income',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('goodsNum', models.IntegerField()),
                ('userId', models.CharField(max_length=20)),
                ('lastTime', models.DateTimeField(auto_now=True)),
                ('isOver', models.BooleanField(default=False)),
                ('payMethod', models.CharField(max_length=11)),
                ('amount', models.CharField(max_length=16)),
            ],
            options={
                'db_table': 'Order',
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
            },
        ),
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('orderId', models.IntegerField()),
                ('skuId', models.IntegerField()),
                ('skuNum', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('UserId', models.IntegerField()),
                ('NickName', models.CharField(max_length=20)),
                ('Phone', models.CharField(max_length=11)),
                ('Gender', models.BooleanField(default=False)),
                ('IdCard', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'UserInfo',
                'verbose_name': '用户信息',
                'verbose_name_plural': '用户信息',
            },
        ),
    ]
