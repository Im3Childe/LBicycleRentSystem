from datetime import datetime # 时间模块函数
from django.shortcuts import render,redirect # 模板重定向以及渲染
from django.core.urlresolvers import reverse # 模板的方向解析
from django.core.paginator import Paginator # 模板的分页函数
from django.db import transaction # 数据库事务
from django.views.generic import View # 类视图
from django.contrib.auth import authenticate, login, logout # django的认证系统
from utils.mytool import LoginRequiredMixin # 登陆状态验证
from django.http import HttpResponse # 应答
from zCelery_Tool.tasks import send_register_active_email # 激活邮件发送
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer # 加密
from itsdangerous import SignatureExpired # 密码失效抛出
from django_redis import get_redis_connection # python与redis交互
from django.core.cache import cache # 缓存设置
from django.http import JsonResponse # ajax数据返回
from django.conf import settings # 静态设置
from theSystem.models import * # 模型类
import re # 正则匹配
# Create your views here.
# 注册
class Register(View):
    '''注册功能实现'''
    '''from django.views.generic import View 实现类视图'''
    def get(self, request):
        return render(request,'register.html')

    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # idCard = request.POST.get('IDcard')

        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg':'数据不完整'})

        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

            # 进行业务处理: 进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        # # 加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info) # bytes
        token = token.decode()

        # 发邮件
        send_register_active_email.delay(email, username, token)

        # 返回应答, 跳转到首页
        return redirect(reverse('system:index'))
	# 用HttpResponse来返回数据
        # return HttpResponse('ok')

# 登陆
class LoginView(View):
    '''登陆功能实现'''
    def get(self, request):
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        # 使用模板
        return render(request, 'login.html', {'username':username, 'checked':checked})

    def post(self,request):
        '''登录校验'''
        # 接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')

        # 校验数据
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        # 业务处理:登录校验
        user = authenticate(username=username, password=password)
        if user is not None:
            # 用户名密码正确
            if user.is_active:
                # 用户已激活
                # 记录用户的登录状态
                login(request, user)

                # 获取登录后所要跳转到的地址
                # 默认跳转到首页
                next_url = request.GET.get('next', reverse('system:user'))

                # 跳转到next_url
                response = redirect(next_url)  # HttpResponseRedirect

                # 判断是否需要记住用户名
                remember = request.POST.get('remember')

                if remember == 'on':
                    # 记住用户名
                    response.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    response.delete_cookie('username')

                # 返回response
                return response
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})

# 登出
class LogoutView(View):
    '''退出登录'''
    def get(self, request):
        '''退出登录'''
        # 清除用户的session信息
        logout(request)

        # 跳转到首页
        return redirect(reverse('system:index'))

# 激活账户
class ActiveView(View):
    '''用户激活'''
    def get(self, request, token):
        '''进行用户激活'''
        # 进行解密，获取要激活的用户信息
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info = serializer.loads(token)
            # 获取待激活用户的id
            user_id = info['confirm']

            # 根据id获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            # 跳转到登录页面
            return redirect(reverse('system:login'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期')
        '''
        celety 服务器启动
        celery -A zCelery_Tool.task worker -l info'''

# 用户中心
class UserInfoView(LoginRequiredMixin, View):
    '''用户中心-信息页'''
    def get(self, request):
        '''显示'''
        # Django会给request对象添加一个属性request.user
        # 如果用户未登录->user是AnonymousUser类的一个实例对象
        # 如果用户登录->user是User类的一个实例对象
        # 如果页面发啦ajax请求,最好用request对象的user
        # request.user.is_authenticated()

        # 获取用户的个人信息
        user = request.user
        try:
            userInfo = UserInfo.objects.get(UserId=user.id)
        except UserInfo.DoesNotExist as e:
            userInfo = None

        # 获取用户的历史浏览记录
        # from redis import StrictRedis
        # sr = StrictRedis(host='172.16.179.130', port='6379', db=9)
        # 获得redis的连接
        con = get_redis_connection('default')

        history_key = 'history_%d'%user.id

        # 获取用户最新浏览的5个商品的id
        sku_ids = con.lrange(history_key, 0, 4) # [2,3,1]
        print(sku_ids)
        # 从数据库中查询用户浏览的商品的具体信息
        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        #
        # goods_res = []
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)

        # 遍历获取用户浏览的商品信息
        goods_li = []
        for id in sku_ids:
            goods = Goods.objects.get(id=id)
            print(goods)
            goods_li.append(goods)

        print(goods_li)

        # 组织上下文
        context = {'page':'user',
                   'userInfo':userInfo,
                   'goods_li':goods_li}

        # 除了你给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件
        return render(request, 'user_center_info.html', context)

#  订单中心
class OrderView(LoginRequiredMixin, View):
    '''用户中心-订单页'''

    def get(self, request, page=None):
        '''显示'''
        # 获取用户的订单信息
        user = request.user
        orders = Order.objects.filter(userId=user.id, isOver=False).order_by('-time')
        print(orders)
        # 分页
        paginator = Paginator(orders, 1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文
        context = {'order_page': order_page,
                   'pages': pages,
                   'orders': orders}

        # 使用模板
        return render(request, 'user_order_info.html', context)
# 信息中兴
class SiteView(LoginRequiredMixin, View):
    '''用户中心-地址页'''
    def get(self, request):
        '''显示'''
        # 获取登录用户对应User对象
        user = request.user

        # 获取用户的默认收货地址
        # try:
        #     address = Address.objects.get(user=user, is_default=True) # models.Manager
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        userInfo = UserInfo.objects.filter(UserId=user.id)

        # 使用模板
        return render(request, 'user_center_site.html', {'page':'userInfo', 'userInfo':userInfo})

    def post(self, request):
        '''地址的添加'''
        # 接收数据
        nickname = request.POST.get('nickname')
        idcard = request.POST.get('idcard')
        gender = request.POST.get('gender')
        phone = request.POST.get('phone')


        # 校验数据
        if not all([nickname, idcard, phone, gender]):
            return render(request, 'user_center_site.html', {'errmsg':'数据不完整'})

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg':'手机格式不正确'})

        # 业务处理：地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录用户对应User对象
        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None

        # address = Address.objects.get_default_address(user)
        userInfo = UserInfo.objects.filter(UserId=user.id)
        if gender:
            gender = True
        else:
            gender = False


        if userInfo:
            is_default = False
        else:
            is_default = True

        # 添加地址
        UserInfo.objects.create(UserId=user.id,
                                NickName=nickname,
                                Phone=phone,
                                Gender=gender,
                                IdCard=idcard
                               )

        # 返回应答,刷新地址页面
        return redirect(reverse('system:site')) # get请求方式

# 首页
class Index(View):
    def get(self, request):
        '''显示首页'''
        # 尝试从缓存中获取数据
        context = cache.get('index_page_data')

        if context is None:
            # 缓存中没有数据
            # 获取商品的种类信息
            types = Brand.objects.all()
            for type in types:

                good = Goods.objects.filter(brandId=type.id)[:4]

                # name = good.goods
                # good_id = good.id
                # goods = {'good':name, 'id':good_id}
                type.good = good

            context = {'types': types,
                       }
            # 设置缓存
            # key  value timeout
            cache.set('index_page_data', context, 3600)

        # 获取用户购物车中商品的数目

        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # 用户已登录
            try:
                nickname = UserInfo.objects.get(UserId=user.id, id=1)
            except UserInfo.DoesNotExist as e :
                nickname = ''
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            if nickname:
                user.nickname = nickname.NickName
            else:
                user.nickname = ''
        # 组织模板上下文

        context.update(cart_count=cart_count)

        # 使用模板
        return render(request, 'index.html', context)
        ''' 启动nginx
            需要切换到/usr/local/nginx/sbin
            sudo ./nginx -c /usr/local/nginx/conf/nginx.conf
        '''
# 商品详情
class Detail(LoginRequiredMixin, View):
    '''商品详情页面'''

    def get(self, request, goods_id):
        '''显示详情页'''
        try:
            sku = Goods.objects.get(id=goods_id)
        except Goods.DoesNotExist:
            # 商品不存在
            return redirect(reverse('system:index'))

        # 获取商品的分类信息

        brand = Brand.objects.get(id=sku.brandId)
        types = Brand.objects.all()

        # # 获取商品的评论信息
        # sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')
        #
        # # 获取新品信息
        # new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        # 获取同一个SPU的其他规格商品
        # same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)

        # 获取用户购物车中商品的数目
        # 获取新品信息
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            # 添加用户的历史记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' % user.id
            # 移除列表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的5条信息
            conn.ltrim(history_key, 0, 4)

        # 组织模板上下文
        context = {'sku': sku, 'types': types,
                   "brand":brand,
                   'cart_count': cart_count}

        # 使用模板
        return render(request, 'detail.html', context)

# 商品列表
class ListView(View):
    '''列表页'''
    def get(self, request, type_id, page):
        '''显示列表页'''
        # 获取种类信息
        try:
            type = Brand.objects.get(id=type_id)
        except Goods.DoesNotExist:
            # 种类不存在
            return redirect(reverse('system:index'))

        # 获取商品的分类信息
        types = Brand.objects.all()

        # 获取排序的方式 # 获取分类商品的信息
        # sort=default 按照默认id排序
        # sort=price 按照商品价格排序
        # sort=hot 按照商品销量排序
        sort = request.GET.get('sort')

        if sort == 'price':
            skus = Goods.objects.filter(brandId=type.id).order_by('price')
        elif sort == 'hot':
            skus = Goods.objects.filter(brandId=type.id).order_by('-sales')
        else:
            sort = 'default'
            skus = Goods.objects.filter(brandId=type.id).order_by('-id')

        # 对数据进行分页
        paginator = Paginator(skus, 1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        skus_page = paginator.page(page)

        # 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context = {'type':type, 'types':types,
                   'skus_page':skus_page,
                   'cart_count':cart_count,
                   'pages': pages,
                   'sort':sort}

        # 使用模板
        return render(request, 'list.html', context)

# ajax发起的请求都在后台，在浏览器中看不到效果
# /add
class CartAddView(View):
    '''购物车记录添加'''
    def post(self, request):
        '''购物车记录添加'''
        user = request.user

        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res':0, 'errmsg':'请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res':1, 'errmsg':'数据不完整'})

        # 校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res':2, 'errmsg':'商品数目出错'})

        # 校验商品是否存在
        try:
            sku = Goods.objects.get(id=sku_id)
        except Goods.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res':3, 'errmsg':'商品不存在'})

        # 业务处理:添加购物车记录
        # 将购物车信息记录到redis数据库中
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # 先尝试获取sku_id的值 -> hget cart_key 属性
        # 如果sku_id在hash中不存在，hget返回None
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            # 累加购物车中商品的数目
            count += int(cart_count)

        # 校验商品的库存
        if count > sku.goodsNum:
            return JsonResponse({'res':4, 'errmsg':'商品库存不足'})
        print(7)
        # 设置hash中sku_id对应的值
        # hset->如果sku_id已经存在，更新数据， 如果sku_id不存在，添加数据
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车商品的条目数

        total_count = conn.hlen(cart_key)


        # 返回应答
        return JsonResponse({'res':5, 'total_count':total_count, 'message':'添加成功'})


class New(View):
    def get(self, request):
        '''购物车记录添加'''
        user = request.user

        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})
        # 接收数据
        sku_id = request.GET.get('sku_id')
        count = request.GET.get('count')
        print(sku_id)
        print(count)
        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        # 校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})

        # 校验商品是否存在
        try:
            sku = Goods.objects.get(id=sku_id)
        except Goods.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理:添加购物车记录
        # 将购物车信息记录到redis数据库中
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 先尝试获取sku_id的值 -> hget cart_key 属性
        # 如果sku_id在hash中不存在，hget返回None
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            # 累加购物车中商品的数目
            count += int(cart_count)

        # 校验商品的库存
        if count > sku.goodsNum:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})
        print(7)
        # 设置hash中sku_id对应的值
        # hset->如果sku_id已经存在，更新数据， 如果sku_id不存在，添加数据
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车商品的条目数

        total_count = conn.hlen(cart_key)

        # 返回应答
        # return JsonResponse({'res': 5, 'total_count': total_count, 'message': '添加成功'})
        return HttpResponse('ok')
# /cart
class CartInfoView(LoginRequiredMixin, View):
    '''购物车页面显示'''
    def get(self, request):
        '''显示'''
        # 获取登录的用户
        user = request.user
        # 获取用户购物车中商品的信息
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id
        # {'商品id':商品数量}
        cart_dict = conn.hgetall(cart_key)

        skus = []
        # 保存用户购物车中商品的总数目和总价格
        total_count = 0
        total_price = 0
        # 遍历获取商品的信息
        for sku_id, count in cart_dict.items():
            # 根据商品的id获取商品的信息
            sku = Goods.objects.get(id=sku_id)
            # 计算商品的小计
            amount = sku.price*int(count)
            # 动态给sku对象增加一个属性amount, 保存商品的小计
            sku.amount = amount
            # 动态给sku对象增加一个属性count, 保存购物车中对应商品的数量
            sku.count = count
            # 添加
            skus.append(sku)

            # 累加计算商品的总数目和总价格
            total_count += int(count)
            total_price += amount

        # 组织上下文
        context = {'total_count':total_count,
                   'total_price':total_price,
                   'skus':skus}

        # 使用模板
        return render(request, 'cart.html', context)



class CartUpdateView(View):
    '''购物车记录更新'''
    def post(self, request):
        '''购物车记录更新'''
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收数据
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        # 数据校验
        if not all([sku_id, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        # 校验添加的商品数量
        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'errmsg': '商品数目出错'})

        # 校验商品是否存在
        try:
            sku = Goods.objects.get(id=sku_id)
        except Goods.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res': 3, 'errmsg': '商品不存在'})

        # 业务处理:更新购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        # 校验商品的库存
        if count > sku.goodsNum:
            return JsonResponse({'res':4, 'errmsg':'商品库存不足'})

        # 更新
        conn.hset(cart_key, sku_id, count)

        # 计算用户购物车中商品的总件数 {'1':5, '2':3}
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        # 返回应答
        return JsonResponse({'res':5, 'total_count':total_count, 'message':'更新成功'})


# 删除购物车记录
# 采用ajax post请求
# 前端需要传递的参数:商品的id(sku_id)
# /cart/delete
class CartDeleteView(View):
    '''购物车记录删除'''
    def post(self, request):
        '''购物车记录删除'''
        user = request.user
        if not user.is_authenticated():
            # 用户未登录
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # 接收参数
        sku_id = request.POST.get('sku_id')

        # 数据的校验
        if not sku_id:
            return JsonResponse({'res':1, 'errmsg':'无效的商品id'})

        # 校验商品是否存在
        try:
            sku = Goods.objects.get(id=sku_id)
        except Goods.DoesNotExist:
            # 商品不存在
            return JsonResponse({'res':2, 'errmsg':'商品不存在'})

        # 业务处理:删除购物车记录
        conn = get_redis_connection('default')
        cart_key = 'cart_%d'%user.id

        # 删除 hdel
        conn.hdel(cart_key, sku_id)

        # 计算用户购物车中商品的总件数 {'1':5, '2':3}
        total_count = 0
        vals = conn.hvals(cart_key)
        for val in vals:
            total_count += int(val)

        # 返回应答
        return JsonResponse({'res':3, 'total_count':total_count, 'message':'删除成功'})


# /place
class OrderPlaceView(LoginRequiredMixin, View):
    '''锁定商品'''
    @transaction.atomic
    def post(self, request):
        '''提交订单页面显示'''
        # 获取登录的用户
        user = request.user
        # 获取参数sku_ids
        sku_ids = request.POST.getlist('sku_ids') # [1,26]


        # 校验参数
        if not sku_ids:
            # 跳转到购物车页面
            return redirect(reverse('system:cart'))
        print(sku_ids)

        # 保存商品的总件数和总价格
        total_count = 0
        total_price = 0
        save_id = transaction.savepoint()
        try:

            # todo: 向df_order_info表中添加一条记录
            order = Order.objects.create(userId=user.id,
                                         goodsNum=total_count,
                                         amount=total_price,
                                         payMethod= 0,
                                         )
            # todo: 用户的订单中有几个商品，需要向df_order_goods表中加入几条记录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            # sku_ids = sku_ids.split(',')
            for sku_id in sku_ids:
                print(type(sku_id))
                for i in range(3):
                    # 获取商品的信息
                    try:
                        sku = Goods.objects.get(id=sku_id)
                    except:
                        # 商品不存在
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 4, 'errmsg': '商品不存在'})

                    # 从redis中获取用户所要购买的商品的数量
                    count = conn.hget(cart_key, sku_id)
                    # todo: 判断商品的库存
                    if int(count) > sku.goodsNum:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})
                        # todo: 向df_order_goods表中添加一条记录
                    print('ok')
                    OrderInfo.objects.create(orderId=order.id,
                                              skuId=sku_id,
                                              skuNum=count,)
                    print('bad')
                    # todo: 更新商品的库存和销量
                    orgin_stock = sku.goodsNum
                    new_stock = orgin_stock - int(count)
                    new_sales = sku.sales + int(count)

                    # 返回受影响的行数
                    res = Goods.objects.filter(id=sku_id, goodsNum=orgin_stock).update(goodsNum=new_stock, sales=new_sales)
                    if res == 0:
                        if i == 2:
                            # 尝试的第3次
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'res': 7, 'errmsg': 2})
                        continue

                    # todo: 累加计算订单商品的总数量和总价格
                    amount = sku.price * int(count)
                    total_count += int(count)
                    total_price += amount

                    # 跳出循环
                    break

            # todo: 更新订单信息表中的商品的总数量和总价格
            # 再订单表新增商品总单价以及商品总数
            order.goodsNum = total_count
            order.amount = total_price
            order.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res': 9, 'errmsg': '下单失败'})

        # 提交事务
        transaction.savepoint_commit(save_id)

        # todo: 清除用户购物车中对应的记录
        conn.hdel(cart_key, *sku_ids)

        # 使用模板
        # 组织上下文
        order_id = order.id
        context = {
                   'order':order,
                   'total_count': total_count,
                   'total_price': total_price,
                   'order_id': order_id}
        return render(request, 'user_order_info.html', context)


# 前端传递的参数:地址id(addr_id) 支付方式(pay_method) 用户要购买的商品id字符串(sku_ids)
# mysql事务: 一组sql操作，要么都成功，要么都失败
# 高并发:秒杀
# 支付宝支付
# 订单页面生成
class OrderShow(View):
    '''订单页面生成'''
    def get(self, request, order_id):
        user = request.user
        if not user.is_authenticated():
            return redirect(reverse('system:index'))

        order = Order.objects.get(id=order_id, userId=user.id)

        context = {'order':order}
        # datetime.strftime('%H')将时间按想要的时间段取出
        print(order.time.strftime('%H'))
        return render(request, 'take_order.html', context)


class OrderCommitView(View):
    '''订单创建'''
    def post(self,request):
        user = request.user
        if not user.is_authenticated():
            return redirect(reverse('system:index'))
        order_id = request.POST.get('order_id')
        order_method = request.POST.get('pay_method')
        now = datetime.now().strftime('%H')
        # 判断支付方式
        paymethod = ''
        if order_method == '1':
            paymethod = '微信支付'
        else:
            paymethod ='支付宝'
        order = Order.objects.get(userId=user.id, id=order_id)
        order_time = Order.objects.get(userId=user.id, id=order_id).time.strftime('%H')
        # thetime = order_time.time.strftime('%H')
        # 将时间相减乘以单价得出支付金额
        time = int(now) - int(order_time)
        money = int(order.amount) * time
        if money:
            Income.objects.create(income=money)
        # 将库存更新
        # 将该订单表中的所有商品id以及商品购买数量取出,形成更新
        Infos = OrderInfo.objects.filter(orderId = order.id)
        for info in Infos:
            skuId = info.skuId
            goods = Goods.objects.get(id=skuId)
            skuNum = info.skuNum+goods.goodsNum
            Goods.objects.filter(id=skuId).update(goodsNum=skuNum)
            print(skuNum)
        order.save()
        return JsonResponse({'res': 5, 'paymethod': paymethod, 'money': money,'order_id':order.id})
