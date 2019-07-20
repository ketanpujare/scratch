# -*- coding: utf-8 -*-
from scrapy                 import Spider,Request,FormRequest

from scratch.utils          import asp_post
from scratch.middlewares    import Captcha

from uuid                   import uuid4
from io                     import BytesIO
from PIL                    import Image
from pyocr.libtesseract     import image_to_string
from re                     import sub


class FrameCaptcha(Captcha):
    max_tries = 30
    param_name = '#'
    captcha_url = '#'

    def solve(self, bindata):
        # custom solution 
        return

    def is_solution_valid(self, solution):
        if solution and len(solution) in [6]:
            return solution and len(solution) in [6]
        else:
            return False

    def is_captcha_solved(self, response):
        if '#' in response.text:
            return False
        else:
            return True

class FrameSpider(Spider):
    name = 'frame'
    url  = '#'

    def start_requests(self):
        yield Request(self.url,
                    meta={'cookiejar':str(uuid4())},
                    callback=self.get_firstpage)

    def get_firstpage(self,response):
        pass