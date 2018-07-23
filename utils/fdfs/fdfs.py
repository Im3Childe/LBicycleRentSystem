from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FDFSStorage(Storage):
    '''fast dfs文件存储类'''
    def __init__(self, client_conf=None, base_url=None):
        # 再django中，都是系统自动调用类，所以一般情况下我们是不能初始化类的，
        '''再setting中设置配置文件路径以及nginx的url，这样使得函数复用性增强'''
        if settings.FDFS_CLIENT_CONF == '':
            self.conf = './utils/fdfs/client.conf'
        else:
            self.conf = settings.FDFS_CLIENT_CONF
        if settings.FDFS_URL == '':
            self.url = 'http://192.168.181.131:8888/'
        else:
            self.url = settings.FDFS_URL

    def _open(self, name, mode='rb'):
        '''打开文件时使用'''
        pass

    def _save(self, name, content):
        '''保存文件时使用'''
        # name:你选择上传文件的名字
        # content:包含你上传文件内容的File对象

        # 创建一个Fdfs_client对象
        client = Fdfs_client(self.conf)

        # 上传文件到fast dfs系统中
        res = client.upload_by_buffer(content.read())

        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到fast dfs失败')

        # 获取返回的文件ID
        filename = res.get('Remote file_id')

        return filename

    def exists(self, name):
        '''Django判断文件名是否可用'''
        return False

    def url(self, name):
        '''返回访问文件的url路径'''
        return self.url+name