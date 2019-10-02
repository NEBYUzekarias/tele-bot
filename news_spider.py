import asyncio
from ruia import Request , Response
from parsel import Selector


async def request_example():
    url = 'http://portal.neaea.gov.et/Home/Student'
    params = {
        'name': 'ruia',
    }
    headers = {
        'User-Agent': ('Mozilla/5.0'),
    }
    request = Request(url=url, method='GET', params=params, headers=headers)
    must_cookies = {} 
    must_cookies_names =['__RequestVerificationToken']
    
    response = await request.fetch()
    for cookie_name in must_cookies_names:
        must_cookies[cookie_name] =  response.cookies.get(cookie_name)
    history = response.history
    text=await response.text()
    html = Selector(text= text)
    csrf_token = html.xpath("/html/body/div[2]/div/form/input/@value").get()

    form_data = {
        '__RequestVerificationToken': csrf_token,
        'admissionNumber': None  # to be set
    }
    return form_data , must_cookies ,history
async def sec_request():
    form_data , must_cookies , history = await request_example()    
    headers = {
        'User-Agent': ('Mozilla/5.0'),
    }
    request = Request(url='http://portal.neaea.gov.et/Student/StudentDetailsx', method='POST', 
    headers=headers, metadata=form_data, cookies=must_cookies)
    print(request)
    return request.fetch() 
    # response = await request.fetch()
    # json_result = await response.json()
    # assert json_result['args']['name'] == 'ruia'
    # assert json_result['headers']['User-Agent'] == 'Python3.6'


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(sec_request())