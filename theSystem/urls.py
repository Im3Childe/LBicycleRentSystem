from django.conf.urls import url
from theSystem.views import *

urlpatterns = [
    url(r'^register$', Register.as_view(), name='register'),  # 用户注册
    url(r'^login$', LoginView.as_view(), name='login'), # 用户登陆
    url(r'^logout$', LogoutView.as_view(), name='logout'), # 用户登出
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'), # 用户激活
    url(r'^user$', UserInfoView.as_view(), name='user'), # 用户个人中心页面
    url(r'^order/(?P<page>\d+)$', OrderView.as_view(), name='order'), # 用户订单页面
    url(r'^site$', SiteView.as_view(), name='site'), # 信息页面
    url(r'^index$', Index.as_view(), name='index'), # 主页
    url(r'^detail/(?P<goods_id>\d+)$', Detail.as_view(), name='detail'), # 商品详情页面
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$', ListView.as_view(), name='list'),  # 列表页
    url(r'^add$', CartAddView.as_view(), name='add'), # 购物车添加
    url(r'^cart$', CartInfoView.as_view(), name='cart' ), # 购物车页面
    url(r'^delete$', CartDeleteView.as_view(), name='delete'), # 购物车页面删除功能
    url(r'^updata$', CartUpdateView.as_view(), name='updata'), # 购物车页面数据更新
    url(r'^takeorder$', OrderPlaceView.as_view(), name='takeorder'), # 提交订单页面
    url(r'^ordercommit', OrderCommitView.as_view(), name='ordercommit'), # 结账
    url(r'^show/(?P<order_id>\d+)$', OrderShow.as_view(), name='show'),
    url(r'^new$', New.as_view(), name='new')
]
