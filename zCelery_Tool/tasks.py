# 使用celery
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader, RequestContext
from celery import Celery


import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LBicycleRentSystem.settings")
django.setup()
from theSystem.models import *
# 在任务处理者一端加这几句


# from goods.models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django_redis import get_redis_connection

# 创建一个Celery类的实例对象
app = Celery('zCelery_Tool.tasks', broker='redis://127.0.0.1:6379/2')

# 定义任务函数
@app.task
def send_register_active_email(to_email, username, token):
    '''发送激活邮件'''
    # 组织邮件信息
    print(1)
    subject = '欢迎信息'
    message = ''
    #
    from_email = settings.EMAIL_FROM
    recipient_list = [to_email]
    html_message = '<h1>%s, 欢迎您成为注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/active/%s">http://127.0.0.1:8000/active/%s</a>' % (username, token, token)

    send_mail(subject, message, from_email, recipient_list, html_message=html_message)

#

@app.task
def generate_static_index_html():
    '''产生首页静态页面'''
    # 缓存中没有数据
    # 获取商品的种类信息
    types = Brand.objects.all()
    # 将各个品牌的商品输出
    for type in types:
        print(type.img)
        good = Goods.objects.filter(brandId=type.id)
        type.good = good


    # 组织模板上下文
    context = {'types': types}

    # 使用模板
    # 1.加载模板文件,返回模板对象
    temp = loader.get_template('static_index.html')
    # 2.模板渲染
    static_index_html = temp.render(context)

    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)
