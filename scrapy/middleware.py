from collections import defaultdict

from scrapy import log
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object
from scrapy.utils.defer import process_parallel, process_chain, process_chain_both

class MiddlewareManager(object):
    """Base class for implementing middleware managers"""

    component_name = 'foo middleware'

    def __init__(self, *middlewares):
        self.middlewares = middlewares
        self.methods = defaultdict(list)
        for mw in middlewares:
            self._add_middleware(mw)

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        """
        取得中间件列表， 字典
        ExtensionManager有做重写， 返回EXTENSIONS_BASE 并 EXTENSIONS的class path
        """
        raise NotImplementedError

    @classmethod
    def from_settings(cls, settings, crawler=None):
        mwlist = cls._get_mwlist_from_settings(settings)
        middlewares = []
        for clspath in mwlist:
            try:
                mwcls = load_object(clspath)
                if crawler and hasattr(mwcls, 'from_crawler'):
                    mw = mwcls.from_crawler(crawler)
                elif hasattr(mwcls, 'from_settings'):
                    mw = mwcls.from_settings(settings)
                else:
                    mw = mwcls()
                middlewares.append(mw)
            except NotConfigured as e:
                if e.args:
                    clsname = clspath.split('.')[-1]
                    log.msg(format="Disabled %(clsname)s: %(eargs)s",
                            level=log.WARNING, clsname=clsname, eargs=e.args[0])

        enabled = [x.__class__.__name__ for x in middlewares]
        log.msg(format="Enabled %(componentname)ss: %(enabledlist)s", level=log.INFO,
                componentname=cls.component_name, enabledlist=', '.join(enabled))
        return cls(*middlewares)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings, crawler)

    def _add_middleware(self, mw):
        """
        添加中间件的方法open_spider和close_spider方法， 如果存在则添加
        注意先后顺序open = append, close = insert(0
        先open后close, 后open， 先close
        """
        if hasattr(mw, 'open_spider'):
            self.methods['open_spider'].append(mw.open_spider)
        if hasattr(mw, 'close_spider'):
            self.methods['close_spider'].insert(0, mw.close_spider)

    def _process_parallel(self, methodname, obj, *args):
        """
        并行处理
        """
        # Chen: process_parallel 什么是并行处理， 暂时不看, twisted的资料太少了， 先使用
        return process_parallel(self.methods[methodname], obj, *args)

    def _process_chain(self, methodname, obj, *args):
        return process_chain(self.methods[methodname], obj, *args)

    def _process_chain_both(self, cb_methodname, eb_methodname, obj, *args):
        return process_chain_both(self.methods[cb_methodname], \
            self.methods[eb_methodname], obj, *args)

    def open_spider(self, spider):
        """
        并行处理 所有中间件的 open_spider
        """
        return self._process_parallel('open_spider', spider)

    def close_spider(self, spider):
        """
        并行处理 所有中间件的 close_spider
        """
        return self._process_parallel('close_spider', spider)
