"""
The Extension Manager

See documentation in docs/topics/extensions.rst
"""
from scrapy.middleware import MiddlewareManager
from scrapy.utils.conf import build_component_list

class ExtensionManager(MiddlewareManager):
    """
    扩展管理器
    通过配置， 取得所有扩展

    build_component_list： 合并EXTENSIONS_BASE和EXTENSIONS， 去重， 并把值为None的扩展移除
    """
    component_name = 'extension'

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        return build_component_list(settings['EXTENSIONS_BASE'], \
            settings['EXTENSIONS'])
