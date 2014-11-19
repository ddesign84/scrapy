======
阅读Scrapy源代码
======

简介
======

陆续使用Scrapy已经快两年了， 感觉非常方便， 业务上已经没有什么难度了， 准备开始看源代码， 了解他的实现， 以达到从底层进行优化。
如果不太好优化， 看完后需考虑使用golang重写一个类Scrapy的框架。

架构
======


结构
======

* 运行入口

scrapy.crawler

# CrawlerRunner 在一个进行内运行一个爬虫
# CrawlerProcess 在一个进程内同时运行多个爬虫

* 信号管理器 SignalManager

scrapy.signalmanager.SignalManager 信号管理器

* 蜘蛛管理器 SpiderManager

scrapy.spidermanager.SpiderManager 蜘蛛管理器， 有使用

* 中间件管理 MiddlewareManager

scrapy.middleware.MiddlewareManager 中间件管理父类， 两个初始化方法from_crawler、from_settings，代码里middleware简写成mv
中间件有三个初始化方法， 如下代码， 先判断是否from_crawler， 再判断from_settings， 实在没有就使用__init__
```
mwcls = load_object(clspath)
if crawler and hasattr(mwcls, 'from_crawler'):
    mw = mwcls.from_crawler(crawler)
elif hasattr(mwcls, 'from_settings'):
    mw = mwcls.from_settings(settings)
else:
    mw = mwcls()
middlewares.append(mw)
```

# ExtensionManager 扩展管理器（基本扩展在配置EXTENSIONS_BASE， 自定义配置为EXTENSIONS）
调用扩展时， 判断是否有方法from_crawler， 有则crawler做为参数传入， 否则判断是否有方法from_settings， 有则settings做为参数传入