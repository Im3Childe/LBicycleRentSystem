# 定义索引类
from haystack import indexes
# 导入你的模型类
from theSystem.models import Goods


# 指定对于某个类的某些数据建立索引
# 索引类名格式:模型类名+Index
class GoodsIndex(indexes.SearchIndex, indexes.Indexable):
    # 索引字段 use_template=True指定根据表中的哪些字段建立索引文件的说明放在一个文件中
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        # 返回你的模型类
        return Goods

    # 建立索引的数据
    def index_queryset(self, using=None):
        return self.get_model().objects.all()




'''模板中显示haystack应用中视图函数中传入的参数
三个参数

query: 关键字
page: 当前页的page对象，注意里面装的是SearchResult,SearchResult的object属性指向的是模型对象
paginator： 分页对象
'''
