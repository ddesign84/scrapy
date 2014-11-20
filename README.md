陆续使用Scrapy已经快两年了， 感觉非常方便， 业务上已经没有什么难度了， 准备开始看源代码， 了解他的实现， 以达到从底层进行优化。
如果不太好优化， 看完后需考虑使用golang重写一个类Scrapy的框架。

##架构

##阅读源代码

###运行入口 scrapy.crawler

* CrawlerRunner 在一个进程内运行一个爬虫
* CrawlerProcess 在一个进程内同时运行多个爬虫，继承*CrawlerRunner*
* Crawler 爬虫
运行爬虫方法如下：
```python
@defer.inlineCallbacks
def crawl(self, *args, **kwargs):
    assert not self.crawling, "Crawling already taking place"
    self.crawling = True

    try:
        self.spider = self._create_spider(*args, **kwargs)
        self.engine = self._create_engine()
        start_requests = iter(self.spider.start_requests())
        yield self.engine.open_spider(self.spider, start_requests)
        yield defer.maybeDeferred(self.engine.start)
    except Exception:
        self.crawling = False
        raise
```

###抓取引擎

scrapy.core.engine.ExecutionEngine

* SCHEDULER 调度器
* DOWNLOADER 下载器


###信号管理器 SignalManager

scrapy.signalmanager.SignalManager

###蜘蛛管理器 SpiderManager

scrapy.spidermanager.SpiderManager

自定义配置SPIDER_MODULES，所有自定义的蜘蛛模块

###蜘蛛 Spider

scrapy.spider.Spider

###中间件管理 MiddlewareManager

#### MiddlewareManager 中间件管理器父类

scrapy.middleware.MiddlewareManager

中间件管理器初始化方法*from_crawler*、*from_settings*，代码里middleware简写成mv
中间件初始化方法*from_crawler*、*from_settings*、*__init__*， 代码如下：

```python
mwcls = load_object(clspath)
if crawler and hasattr(mwcls, 'from_crawler'):
    mw = mwcls.from_crawler(crawler)
elif hasattr(mwcls, 'from_settings'):
    mw = mwcls.from_settings(settings)
else:
    mw = mwcls()
middlewares.append(mw)
```

#### ExtensionManager 扩展管理器

scrapy.extension.ExtensionManager

基本扩展在配置EXTENSIONS_BASE， 自定义配置为EXTENSIONS