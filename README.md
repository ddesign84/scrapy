陆续使用Scrapy已经快两年了， 感觉非常方便， 业务上已经没有什么难度了， 准备开始看源代码， 了解他的实现， 以达到从底层进行优化。

读后感：
已经基本看完， 没有特别深入， 只详细看了核心相关的代码。
感觉scrapy真心不错， 可以快速架构抓取， 已经完全满足我的工作需要。

# 架构

## 架构图

![scrapy](http://doc.scrapy.org/en/0.24/_images/scrapy_architecture.png)

# 阅读源代码

## 运行入口 scrapy.crawler

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

## Spider 蜘蛛

scrapy.spider.Spider

* Crawl scrapy.contrib.spiders.crawl.CrawlSpider
* Feed scrapy.contrib.spiders.feed.XMLFeedSpider、 CSVFeedSpider
* SiteMap scrapy.contrib.spiders.sitempa.SitemapSpider

### Request 请求

scrapy.http.request.Request

## 抓取控制引擎

scrapy.core.engine.ExecutionEngine

### Slot 插件

### SCHEDULER 任务调度器

优先使用DISK QUEUE， 如果*JOBDIR*未设置， 则使用MEMORY QUEUE

如果需要实现*分布式抓取*可以自定义一个*任务调度器*， 使用数据库或消息队列(zmq、rabbitmq、redis等)来做*Request去重*和*任务调度*。

#### DUPEFILTER Request去重

* scrapy.dupefilter.RFPDupeFilter

Request去重算法*request_fingerprint*， URL的GET参数会做重新排序（如：b=1&a=2会转成a=2&b=1）, 并使用sha1生成唯一URL
如果有配置*JOBDIR*， 则会将URL数据保存至requests.seen文件中， 下次打开时会加载至内存
RFPDupeFilter一般使用没问题， 但是URL多了， 如上百万时， 将会很占内存， 可以使用Bloom Filter算法

* BaseDupeFilter

#### DISK QUEUE 磁盘队列

scrapy.squeue.PickleLifoDiskQueue

#### MEMORY QUEUE 内存队列

scrapy.squeue.LifoMemoryQueue

### Scraper 蜘蛛解析器
### DOWNLOADER 下载器

## 信号管理器 SignalManager

scrapy.signalmanager.SignalManager

## 蜘蛛管理器 SpiderManager

scrapy.spidermanager.SpiderManager

自定义配置SPIDER_MODULES，所有自定义的蜘蛛模块

## 蜘蛛 Spider

scrapy.spider.Spider

## 中间件管理 MiddlewareManager

执行所有中间件的*open_spider*和*close_spider*方法

### MiddlewareManager 中间件管理器父类

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

### ExtensionManager 扩展中间件管理器

scrapy.extension.ExtensionManager

基本扩展在配置EXTENSIONS_BASE， 自定义配置为EXTENSIONS

### SpiderMiddlewareManager 蜘蛛中间件管理器

scrapy.core.spidermw.SpiderMiddlewareManager
执行所有蜘蛛的*process_spider_input*、*process_spider_output*、*process_spider_exception*和*process_start_requests*

```python
SPIDER_MIDDLEWARES = {}
SPIDER_MIDDLEWARES_BASE = {
    # Engine side
    'scrapy.contrib.spidermiddleware.httperror.HttpErrorMiddleware': 50,
    'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': 500,
    'scrapy.contrib.spidermiddleware.referer.RefererMiddleware': 700,
    'scrapy.contrib.spidermiddleware.urllength.UrlLengthMiddleware': 800,
    'scrapy.contrib.spidermiddleware.depth.DepthMiddleware': 900,
    # Spider side
}
```

### ItemPipelineManager Item通道中间件管理器

scrapy.contrib.pipeline.ItemPipelineManager
执行所有Item通道的*process_item*方法

#### files
#### images
#### media