from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser, models.Model):
    '''user模型类，继承AbstractUser类，是注册时候必填的信息'''
    # AbstractUser类中自定义了用户的三个要素username，password，email，并且实现了django自带的认证系统

    class Meta:
        db_table = 'User'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class UserInfo(models.Model):
    '''用户信息表，用户注册成功后在用户中心补充信息'''
    # 对应的用户Id，为了增删改查的方便和系统效率没有设置外键
    UserId = models.IntegerField()
    # 用户昵称
    NickName = models.CharField(max_length=20)
    # 用户手机号码
    Phone = models.CharField(max_length=11)
    # 用户性别
    Gender = models.BooleanField(default=False)
    # 用户身份证信息
    IdCard = models.CharField(max_length=20)

    class Meta:
        db_table = 'UserInfo'
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

class Order(models.Model):
    '''订单模型'''

    # auto_now_add 表示创建时间
    time = models.DateTimeField(auto_now_add=True)
    # 商品数量
    goodsNum = models.IntegerField()
    # 对应的用户
    userId = models.CharField(max_length=20)
    # auto_now 表示修改时间
    lastTime = models.DateTimeField(auto_now=True)
    # 表示订单是否结账
    isOver = models.BooleanField(default=False)
    # 支付方式
    payMethod = models.CharField(max_length=11)
    # 商品总价
    amount = models.CharField(max_length=16)


    class Meta:
        # 定义订单表
        db_table = 'Order'
        verbose_name = '订单'
        verbose_name_plural = verbose_name


class OrderInfo(models.Model):
    '''提交订单后将商品的库存更新的数据'''
    # 对应订单表id
    orderId = models.IntegerField()
    # 对应商品id
    skuId = models.IntegerField()
    # 对应商品数量
    skuNum = models.IntegerField()


class Goods(models.Model):
    '''商品模型'''
    # 商品名字
    goods = models.CharField(max_length=20)
    # 对于品牌ID
    brandId = models.IntegerField()
    # 对应型号ID
    styleId = models.IntegerField()
    # 商品数量
    goodsNum = models.IntegerField()
    # 当图片上传成功了之后，项目文件下会添加一个media的文件夹，并且图片也会自动放在该文件夹下upload_to设置的文件夹路径下
    # 图片
    img = models.ImageField(upload_to='theSystem')
    # 价格
    price = models.IntegerField()
    # 销量
    sales= models.IntegerField()


    class Meta:
        # 定义商品表
        db_table = 'Goods'
        verbose_name = '商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods


class GoodsInfo(models.Model):


    # 商品颜色
    color = models.CharField(max_length=10)
    # 商品品牌
    brand = models.CharField(max_length=16)
    # 商品型号
    type = models.CharField(max_length=16)

    class Meta:
        # 定义商品种类表名称
        db_table = 'GoodsInfo'
        verbose_name = '商品信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id


class Income(models.Model):
    ''''''
    income = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Income'
        verbose_name = 'Income'
        verbose_name_plural = verbose_name



class Brand(models.Model):
    """商品品牌表"""
    # 商品品牌
    brand = models.CharField(max_length=10)
    # 品牌图片
    img = models.ImageField(upload_to='theSystem')
    class Meta:
        # 定义商品种类表名称
        db_table = 'BrandInfo'
        verbose_name = '商品品牌'
        verbose_name_plural = verbose_name


    def __str__(self):
        return self.brand

