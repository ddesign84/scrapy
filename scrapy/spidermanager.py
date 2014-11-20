# coding: utf-8
"""
SpiderManager is the class which locates and manages all website-specific
spiders
"""

from zope.interface import implementer
import six

from scrapy.interfaces import ISpiderManager
from scrapy.utils.misc import walk_modules
from scrapy.utils.spider import iter_spider_classes


@implementer(ISpiderManager)
class SpiderManager(object):

    def __init__(self, settings):
        self.spider_modules = settings.getlist('SPIDER_MODULES')
        self._spiders = {}
        for name in self.spider_modules:
            # 取得SPIDER_MODULES及所有子模块
            for module in walk_modules(name):
                self._load_spiders(module)

    def _load_spiders(self, module):
        """
        加载模块中的蜘蛛
        inspect.isclass(obj) 是类
        issubclass(obj, Spider) 是Spider的子类
        obj.__module__ == module.__name__
        getattr(obj, 'name', None) name不为空
        """
        for spcls in iter_spider_classes(module):
            self._spiders[spcls.name] = spcls

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    def load(self, spider_name):
        try:
            return self._spiders[spider_name]
        except KeyError:
            raise KeyError("Spider not found: {}".format(spider_name))

    def find_by_request(self, request):
        return [name for name, cls in six.iteritems(self._spiders)
            if cls.handles_request(request)]

    def list(self):
        return list(self._spiders.keys())
