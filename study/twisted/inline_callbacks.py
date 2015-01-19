# coding: utf-8
from twisted.internet import reactor, defer
from twisted.web.client import getPage


def p(result):
    print result


def r():
    raise Exception()


def p2():
    d = defer.Deferred()
    d.addCallback(lambda _: p('p2'))
    d.addErrback(err, content='call p2')
    d.addCallback(lambda _: r())
    d.addErrback(err, content='call r2')
    d.callback('p2 success')


def err(f, **kwargs):
    print 'error ' + kwargs['content']


def run():
    # d = defer.Deferred()
    # d.addBoth(lambda _: p('p'))
    # d.addErrback(err, content='call p')
    # d.addBoth(lambda _: r())
    # d.addErrback(err, content='call r')
    # d.addBoth(lambda _: p2())
    # d.addBoth(lambda _: p('p'))
    # d.callback('success')
    d = getPage('http://www.baidu.com/')
    d.addCallback(p)
    all = [d]
    defer.DeferredList(all).addCallback(lambda _: reactor.stop())


reactor.callLater(0, run)
reactor.run()