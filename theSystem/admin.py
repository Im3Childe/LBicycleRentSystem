from django.contrib import admin
from django.core.cache import cache
from theSystem.models import *


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新表中的数据时调用'''
        super().save_model(request, obj, form, change)

        # 发出任务，让celery worker重新生成首页静态页
        from zCelery_Tool.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        '''删除表中的数据时调用'''
        super().delete_model(request, obj)
        # 发出任务，让celery worker重新生成首页静态页
        from zCelery_Tool.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')

# Register your models here.
class BrandInfoAdmin(BaseModelAdmin):
    list_per_page = 10  # 指定每页显示10条数据
    list_display = ['id', 'brand']


class UserInfoAdmin(BaseModelAdmin):
    list_per_page = 10
    list_display = ['id', 'username']


class InfoAdmin(BaseModelAdmin):
    list_display = 10
    list_display = ['id', 'NickName']


class GoodsInfoAdmin(BaseModelAdmin):
    list_display = 10
    list_display = ['id', 'goods']


class GoodsAdmin(BaseModelAdmin):
    list_per_page = 10
    list_display = ['id', 'type']


class OrderAdmin(BaseModelAdmin):
    list_per_page = 10
    list_display = ['id', 'time', 'lastTime', 'isOver']


class IncomeAdmin(BaseModelAdmin):
    list_per_page = 10
    list_display = ['id', 'time', 'income']


admin.site.register(User, UserInfoAdmin)
admin.site.register(UserInfo, InfoAdmin)
admin.site.register(Goods, GoodsInfoAdmin)
admin.site.register(GoodsInfo, GoodsAdmin)
admin.site.register(Brand, BrandInfoAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Income, IncomeAdmin)