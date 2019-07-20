# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy             import signals
from scrapy.exceptions  import IgnoreRequest

from urllib.parse       import parse_qsl,urlencode,urlsplit,urlunsplit

#Captcha
from io                 import BytesIO
from PIL                import Image
from pyocr.libtesseract import image_to_string
from re                 import sub

class CaptchaStatus():
    NOTSTART = 0
    GETCAPTCHA = 1
    VERIFY = 2
    SOLVED = 3

class Captcha():
    def __init__(self):
        self.status = CaptchaStatus.NOTSTART
        self.tries = 0

    def load(self):
         return self.request.replace(url=self.captcha_url,body=None,method='GET')

    def solve(self,captcha):
        img = Image.open(BytesIO(captcha))
        return sub('[^A-Za-z0-9]','',(image_to_string(img) or '').strip())

    def is_solution_valid(captcha_solution):
        return True # or False

    def is_captcha_solved(response):
        return True # or False

    def verify_solution(self,solution):
        def add_solution(body):
            request_paras = parse_qsl(body,keep_blank_values=True)
            return [(self.param_name,solution)] + list(
                    filter(lambda x: x[0] != self.param_name, request_paras))
        if self.request.method != "GET":
            return self.request.replace(body=None,
                formdata=add_solution(self.request.body.decode()))
        urlparts = list(urlsplit(self.request.url))
        urlparts[3] = urlencode(add_solution(urlparts[3]))
        return self.request.replace(url=urlunsplit(urlparts))

class CaptchaDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def load_captcha(self,captcha):
        captcha.status = CaptchaStatus.GETCAPTCHA
        request = captcha.load()
        request.meta.setdefault('captcha',captcha)
        request.meta.setdefault('cookiejar',captcha.request.meta['cookiejar'])
        request.dont_filter = True
        return request

    def verify_captcha_solution(self,captcha,captcha_solution):
        captcha.status = CaptchaStatus.VERIFY
        request = captcha.verify_solution(captcha_solution)
        request.meta.setdefault('captcha',captcha)
        request.meta.setdefault('cookiejar',captcha.request.meta['cookiejar'])
        request.dont_filter = True
        return request

    
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        if 'captcha' in request.meta:
            captcha = request.meta['captcha']

            if captcha.status == CaptchaStatus.NOTSTART:
                captcha.status = CaptchaStatus.GETCAPTCHA
                captcha.request = request
                return self.load_captcha(captcha)
            
            elif captcha.status == CaptchaStatus.GETCAPTCHA:
                captcha.tries += 1
                if captcha.max_tries < captcha.tries:
                    raise IgnoreRequest

        return None

    def process_response(self, request, response, spider):
        if 'captcha' in request.meta:
            captcha = request.meta['captcha']
            if captcha.status == CaptchaStatus.GETCAPTCHA:
                if response.headers.get('Content-Type',b'').startswith(b'image/'):
                    captcha_solution = captcha.solve(response.body)
                    if captcha.is_solution_valid(captcha_solution):
                        return self.verify_captcha_solution(captcha,captcha_solution)
                return self.load_captcha(captcha)

            elif captcha.status == CaptchaStatus.VERIFY:
                
                if captcha.is_captcha_solved(response):
                    captcha.status = CaptchaStatus.SOLVED
                    return response
                return self.load_captcha(captcha)
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScratchSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScratchDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
