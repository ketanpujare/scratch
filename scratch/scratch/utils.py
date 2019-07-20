from scrapy.http.request.form       import _get_form, _get_inputs
from scrapy                         import FormRequest



def asp_post(url,response,eventarget,eventargument,formdata=None,meta=None,
                        callback=None):
    def get_asp_data(response):
        get_form = _get_form(response,formname=None,formid=None,formnumber=0,
                        formxpath=None)
        return dict(_get_inputs(get_form,formdata=None,dont_click=True,clickdata=None,
                response=response))
    
    asp_data = get_asp_data(response)
    asp_data['__EVENTTARGET'] = eventarget
    asp_data['__EVENTARGUMENT'] = eventargument
    asp_data.update(formdata or {})
    return FormRequest(url,formdata=asp_data,meta=meta,callback=callback)
